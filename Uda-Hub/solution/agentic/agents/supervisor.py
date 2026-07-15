import json
import logging
import os

from langchain_core.messages import AIMessage, SystemMessage
from langchain_openai import ChatOpenAI

from agentic.prompts import SUPERVISOR_PROMPT
from agentic.state import AgentState

logger = logging.getLogger("udahub.supervisor")

_llm = None


def _get_llm():
    global _llm
    if _llm is None:
        _llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, base_url=os.environ.get("OPENAI_BASE_URL"))
    return _llm


def supervisor_node(state: AgentState) -> dict:
    """Route to the appropriate specialist agent based on current state."""
    context = f"""Current state:
- Classification: {state.get('classification', 'not yet classified')}
- Urgency: {state.get('urgency', 'unknown')}
- Complexity: {state.get('complexity', 'unknown')}
- Resolution status: {state.get('resolution_status', 'in_progress')}
- Confidence score: {state.get('confidence_score', 'N/A')}
"""
    messages = [
        SystemMessage(content=SUPERVISOR_PROMPT + "\n\n" + context)
    ] + state["messages"]

    response = _get_llm().invoke(messages)

    try:
        result = json.loads(response.content)
        next_agent = result.get("next_agent", "classifier")
        reasoning = result.get("reasoning", "")
    except json.JSONDecodeError:
        # Fallback logic
        if not state.get("classification") or state.get("classification") == "not yet classified":
            next_agent = "classifier"
            reasoning = "No classification yet, routing to classifier."
        elif state.get("resolution_status") in ("resolved", "escalated"):
            next_agent = "FINISH"
            reasoning = "Issue already resolved/escalated."
        else:
            next_agent = "resolver"
            reasoning = "Default routing to resolver."
        logger.warning(f"Supervisor returned invalid JSON, fallback to: {next_agent}")

    logger.info(f"Supervisor routing to: {next_agent} | reason: {reasoning}")

    return {
        "next_agent": next_agent,
        "messages": [AIMessage(content=f"[Supervisor] Routing to: {next_agent}. {reasoning}")],
    }
