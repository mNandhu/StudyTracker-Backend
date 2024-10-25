from v1.state import AssistantState
from langchain_core.messages import AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from backendcrew.src.backendcrew.crew import backendcrewCrew


def crewai_dummy(query: str) -> str:
    return input("Database Query: " + query)
    # return backendcrewCrew().crew().kickoff(inputs={'query': query}).raw


class Nodes:
    def __init__(self):
        self.chat = ChatGroq(model="llama-3.1-70b-versatile")

    def respond_or_query(self, state: AssistantState) -> AssistantState:
        prompt = ChatPromptTemplate.from_messages([
            ("system",
             "Decide if we need to consult the CrewAI agents for more information or if we can respond directly."
             "Output ONLY 'query' or 'respond'. Invalid decisions so far: {invalid_count}. More than 10 will result in termination."),
            ("human", "{input}"),
            ("system", "Context retrieved from CrewAI: {database_agent_response}. Query again?"),
        ])

        chain = prompt | self.chat

        decision = chain.invoke(
            {"input": state["messages"][-1].content,
             "invalid_count": state.get("invalid_decision_count", 0),
             "database_agent_response": state.get("database_agent_response", "None.")})

        decision_content = decision.content.strip(" \n\t\'.\"\\{}()/").lower()

        invalid_decision_count = 0
        # if decision_content.startswith("query") or 'query' in decision_content[:20]:
        #     decision_content = "query"
        if True or decision_content.startswith("respond") or 'respond' in decision_content[:20]:
            decision_content = "respond"
        else:
            # print("Invalid DECISION: ", decision_content, invalid_decision_count)
            decision_content = "invalid"
            invalid_decision_count = state.get("invalid_decision_count", 0) + 1

        print("Task Decision: ", decision_content)

        return {"task_decision": decision_content, "invalid_decision_count": invalid_decision_count}

    def crewai_query(self, state: AssistantState) -> AssistantState:
        prompt = ChatPromptTemplate.from_messages([
            ("system", "Formulate a natural language query for the CrewAI agents based on the student's question."),
            ("human", "{input}"),
        ])
        chain = prompt | self.chat
        result = chain.invoke({"input": state["messages"][-1].content})

        # print("CrewAI Query: ", result.content)

        return {"database_agent_response": state.get("database_agent_response", "") + crewai_dummy(result.content)}

    def main_conversation(self, state: AssistantState) -> AssistantState:
        # print("Context Received: ", state.get("database_agent_response", "No additional information available."))
        prompt = ChatPromptTemplate.from_messages([
            ("system",
             "You are a helpful assistant for a student. Respond based on the conversation and any information from the CrewAI agents."),
            ("human", "{input}"),
            ("system", "Information provided CrewAI Agent: {database_agent_response}\nResponse:"),
        ])
        chain = prompt | self.chat
        response = chain.invoke({
            "input": state["messages"][-1].content,
            "database_agent_response": state.get("database_agent_response", "No additional information available.")
        })
        print("AI Agent reply: ", response.content)
        return {"messages": [AIMessage(content=response.content)]}
