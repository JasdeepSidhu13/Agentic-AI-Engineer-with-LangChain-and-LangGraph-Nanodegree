from __future__ import annotations

import json
import logging

from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableConfig

from src.prompts import EVALUATOR_PROMPT, EvaluationResult
from src.state import AgentState

logger = logging.getLogger("powerline.evaluator")


def evaluator_node(state: AgentState, config: RunnableConfig) -> AgentState:
    llm = config["configurable"]["llm"]
    prompt = EVALUATOR_PROMPT.format(
        user_query=state["user_query"],
        draft_answer=state.get("draft_answer", ""),
        data_results=json.dumps(state.get("data_results", {}), default=str)[:3000],
    )
    structured = llm.with_structured_output(EvaluationResult)
    result: EvaluationResult = structured.invoke(prompt)
    logger.info("Evaluator approved=%s score=%.2f", result.approved, result.quality_score)
    updates: AgentState = {
        "quality_score": result.quality_score,
        "approved": result.approved,
        "evaluator_feedback": result.feedback,
        "next_agent": "supervisor",
        "actions_taken": ["evaluator"],
    }
    if result.approved:
        updates["resolution_status"] = "resolved"
        updates["messages"] = [AIMessage(content=state.get("draft_answer", ""))]
    else:
        updates["retry_count"] = state.get("retry_count", 0) + 1
        if updates["retry_count"] >= 2:
            updates["resolution_status"] = "resolved"
            updates["approved"] = True
    return updates
