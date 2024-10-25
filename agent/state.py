from langgraph.graph import MessagesState

import uuid
from dataclasses import dataclass, field
from typing import Annotated, Any, Literal, Optional, Sequence, Union

from langchain_core.messages import AnyMessage
from langgraph.graph import add_messages


class AssistantState(MessagesState):
    user_query: str
    task_decision: str
    database_agent_response: str
    invalid_decision_count: int


@dataclass(kw_only=True)
class InputState:
    """Represents the input state for the agent."""

    messages: Annotated[Sequence[AnyMessage], add_messages]
