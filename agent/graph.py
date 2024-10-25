# from dotenv import load_dotenv

# load_dotenv()

from langchain_core.runnables import RunnableConfig
from langgraph.graph import StateGraph, END
from agent.utils import load_chat_model
from langchain_core.messages import AIMessage
from langchain_core.prompts import ChatPromptTemplate
import agent.state as state
from agent.configuration import Configuration

def crewai_stub(query: str) -> str:
    return "User's Name is Chris"

async def respond_or_query(state: state.AssistantState,*,config:RunnableConfig):
    prompt = ChatPromptTemplate.from_messages([
        ("system",
            "Decide if we need to consult the CrewAI agents for more information or if we can respond directly."
            "Output ONLY 'query' or 'respond'. Invalid decisions so far: {invalid_count}"),
        ("human", "{input}"),
    ])

    configuration = Configuration.from_runnable_config(config)
    chain = prompt | load_chat_model(configuration.response_model)

    decision = chain.invoke(
        {"input": state["messages"][-1].content, "invalid_count": state.get("invalid_decision_count", 0)})

    decision_content = decision.content.strip().lower()

    invalid_decision_count = 0
    if decision_content.startswith("query"):
        decision_content = "query"
    elif decision_content.startswith("respond"):
        decision_content = "respond"
    else:
        decision_content = "invalid"
        invalid_decision_count = state.get("invalid_decision_count", 0) + 1

    return {"task_decision": decision_content, "invalid_decision_count": invalid_decision_count}

async def crewai_query(state: state.AssistantState, *, config: RunnableConfig):
    prompt = ChatPromptTemplate.from_messages([
        ("system", "Formulate a natural language query for the CrewAI agents based on the student's question."),
        ("human", "{input}"),
    ])
    configuration = Configuration.from_runnable_config(config)
    chain = prompt | load_chat_model(configuration.query_model)
    result = chain.invoke({"input": state["messages"][-1].content})
    return {"database_agent_response": [crewai_stub(result.content)]}

def main_conversation(state: state.AssistantState, *, config: RunnableConfig):
    prompt = ChatPromptTemplate.from_messages([
        ("system",
            "You are a helpful assistant for a student. Respond based on the conversation and any information from the CrewAI agents."),
        ("human", "{input}"),
        ("ai", "CrewAI Agent info: {database_agent_response}\nResponse:"),
    ])
    configuration = Configuration.from_runnable_config(config)
    chain = prompt | load_chat_model(configuration.query_model)
    response = chain.invoke({
        "input": state["messages"][-1].content,
        "database_agent_response": state.get("database_agent_response", "No additional information available.")
    })
    return {"messages": [AIMessage(content=response.content)]}


workflow = StateGraph(state.AssistantState,input=state.InputState,config_schema=Configuration)

# Add nodes
workflow.add_node("respond_or_query", respond_or_query)
workflow.add_node("crewai_agent_query", crewai_query)
workflow.add_node("main_conversation", main_conversation)

# Add edges
workflow.set_entry_point("respond_or_query")
workflow.add_conditional_edges(
    "respond_or_query",
    lambda x: "crewai_agent_query" if x["task_decision"] == "query" else (
        "main_conversation" if x["task_decision"] == "respond" else "respond_or_query"),
    {
        "crewai_agent_query": "crewai_agent_query",
        "main_conversation": "main_conversation",
        "respond_or_query": "respond_or_query"
    }
)
workflow.add_edge("main_conversation", END)

# Compile the graph
graph = workflow.compile()
graph.name = "StudyAssitance"


