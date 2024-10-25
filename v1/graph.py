from dotenv import load_dotenv

load_dotenv()

from langgraph.graph import StateGraph, END

import v1.state as state
from v1.nodes import Nodes


class WorkFlow:
    def __init__(self):
        self.messages = []
        nodes = Nodes()

        workflow = StateGraph(state.AssistantState)

        # Add nodes
        workflow.add_node("respond_or_query", nodes.respond_or_query)
        workflow.add_node("crewai_agent_query", nodes.crewai_query)
        workflow.add_node("main_conversation", nodes.main_conversation)

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
        workflow.add_edge("crewai_agent_query", "respond_or_query")
        workflow.add_edge("main_conversation", END)

        # Compile the graph
        self.app = workflow.compile()

    def display_graph(self) -> str:
        return self.app.get_graph().draw_mermaid()

    def invoke(self, user_input: str) -> dict:
        self.messages.append(user_input)
        return self.app.invoke({"messages": self.messages})

    def clear(self):
        self.messages = []

if __name__ == "__main__":
    wf = WorkFlow()
    # print(wf.display_graph())

    # from langchain_core.messages import HumanMessage

    # messages = []
    while True:
        # messages.append(HumanMessage(content=input("You: ")))
        # result = wf.app.invoke({"messages": messages})
        result = wf.invoke(input("You: "))
        print("\n\nFinal result:")
        print(result['messages'][-1].content)

        print("\n\n")
