import logging
import os

from langchain_core.messages import SystemMessage
from langchain_openai import ChatOpenAI

from agentic.prompts import ESCALATION_PROMPT
from agentic.state import AgentState

logger = logging.getLogger("udahub.escalation")

_llm = None


def _get_llm():
    global _llm
    if _llm is None:
        _llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, base_url=os.environ.get("OPENAI_BASE_URL"))
    return _llm


def escalation_node(state: AgentState) -> dict:
    """Escalate the ticket to human support with a summary."""
    context = f"""Ticket context:
- User ID: {state.get('user_id', 'unknown')}
- Classification: {state.get('classification', 'unknown')}
- Urgency: {state.get('urgency', 'unknown')}
- Confidence score from resolver: {state.get('confidence_score', 'N/A')}
- Tool results so far: {state.get('tool_results', [])}
"""
    messages = [
        SystemMessage(content=ESCALATION_PROMPT + "\n\n" + context)
    ] + state["messages"]

    response = _get_llm().invoke(messages)

    logger.info(
        f"Escalation triggered: classification={state.get('classification')}, "
        f"urgency={state.get('urgency')}, confidence={state.get('confidence_score')}"
    )

    return {
        "messages": [response],
        "resolution_status": "escalated",
    }
