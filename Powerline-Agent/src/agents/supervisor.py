from __future__ import annotations

import logging

from langchain_core.runnables import RunnableConfig

from src.state import AgentState

logger = logging.getLogger("powerline.supervisor")

DATA_INTENTS = {
    "performance_summary",
    "benchmark_analysis",
    "anomaly_investigation",
    "exploratory",
}


def supervisor_node(state: AgentState, config: RunnableConfig) -> AgentState:
    next_agent = _route(state)
    logger.info("Supervisor routing to %s", next_agent)
    return {"next_agent": next_agent, "actions_taken": ["supervisor"]}


def _route(state: AgentState) -> str:
    if state.get("resolution_status") == "resolved":
        return "finish"

    if not state.get("intent"):
        return "classifier"

    if state.get("approved"):
        return "finish"

    intent = state.get("intent", "")
    if intent in DATA_INTENTS and not state.get("data_results"):
        return "data_analyst"

    if state.get("data_results") and not state.get("draft_answer"):
        return "market_advisor"

    if intent == "general_knowledge" and not state.get("draft_answer"):
        return "market_advisor"

    if state.get("draft_answer") and state.get("approved") is None:
        return "evaluator"

    if state.get("approved") is False and state.get("retry_count", 0) < 2:
        return "market_advisor"

    if state.get("draft_answer"):
        return "finish"

    return "data_analyst"


def route_from_supervisor(state: AgentState) -> str:
    nxt = state.get("next_agent", "finish")
    if nxt == "finish" or state.get("resolution_status") == "resolved":
        return "finish"
    return nxt
