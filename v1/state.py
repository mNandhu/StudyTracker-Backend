from langgraph.graph import MessagesState


class AssistantState(MessagesState):
    task_decision: str
    database_agent_response: str
    invalid_decision_count: int