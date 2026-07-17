import operator
from typing import Annotated, Any, Optional

from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage
from typing_extensions import TypedDict


class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    user_query: str

    intent: Optional[str]
    time_range: Optional[dict[str, str]]
    asset_ids: Optional[list[str]]
    complexity: Optional[str]

    data_results: Optional[dict[str, Any]]
    chart_paths: Optional[list[str]]

    draft_answer: Optional[str]
    recommendations: Optional[list[str]]
    confidence_score: Optional[float]

    quality_score: Optional[float]
    approved: Optional[bool]
    evaluator_feedback: Optional[str]

    next_agent: str
    resolution_status: str
    retry_count: int

    session_id: str
    user_id: Optional[str]
    actions_taken: Annotated[list[str], operator.add]
