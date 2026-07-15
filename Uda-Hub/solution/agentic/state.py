from typing import TypedDict, Annotated, Literal
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    # Core message history (LangGraph accumulator)
    messages: Annotated[list[BaseMessage], add_messages]

    # Ticket metadata set by classifier
    ticket_id: str
    user_id: str  # CultPass external user ID
    account_id: str  # e.g. "cultpass"
    classification: str  # "billing", "technical", "account", "reservation", "general"
    urgency: Literal["low", "medium", "high"]
    complexity: Literal["simple", "complex"]

    # RAG results from resolver
    retrieved_articles: list[dict]  # List of {title, content, score}
    confidence_score: float  # 0.0 - 1.0, set by resolver

    # Routing / flow control
    next_agent: str  # Which node to go to next
    resolution_status: Literal["resolved", "escalated", "in_progress", "needs_tool"]

    # Tool results
    tool_results: list[dict]  # Accumulated tool call results

    # Memory context
    long_term_context: str  # Retrieved long-term memory summary
