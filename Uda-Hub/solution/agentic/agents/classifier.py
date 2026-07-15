import json
import logging
import os

from langchain_core.messages import AIMessage, SystemMessage
from langchain_openai import ChatOpenAI

from agentic.prompts import CLASSIFIER_PROMPT
from agentic.state import AgentState

logger = logging.getLogger("udahub.classifier")

_llm = None


def _get_llm():
    global _llm
    if _llm is None:
        _llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, base_url=os.environ.get("OPENAI_BASE_URL"))
    return _llm


def classifier_node(state: AgentState) -> dict:
    """Classify the incoming ticket by type, urgency, and complexity."""
    messages = [SystemMessage(content=CLASSIFIER_PROMPT)] + state["messages"]
    response = _get_llm().invoke(messages)

    try:
        result = json.loads(response.content)
    except json.JSONDecodeError:
        logger.warning("Classifier returned invalid JSON, using defaults")
        result = {
            "classification": "general",
            "urgency": "medium",
            "complexity": "simple",
            "reasoning": "Could not parse classification, defaulting to general.",
        }

    classification = result.get("classification", "general")
    urgency = result.get("urgency", "medium")
    complexity = result.get("complexity", "simple")
    reasoning = result.get("reasoning", "")

    logger.info(
        f"Classified ticket: {classification} | urgency={urgency} | "
        f"complexity={complexity} | reason={reasoning}"
    )

    return {
        "messages": [
            AIMessage(
                content=f"[Classifier] Ticket classified as: {classification}, "
                f"urgency: {urgency}, complexity: {complexity}. Reason: {reasoning}"
            )
        ],
        "classification": classification,
        "urgency": urgency,
        "complexity": complexity,
    }
