from __future__ import annotations

import json
import logging

from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.runnables import RunnableConfig
from langgraph.prebuilt import create_react_agent

from src.data_loader import get_data_store
from src.prompts import CLASSIFIER_PROMPT, ClassificationResult
from src.state import AgentState

logger = logging.getLogger("powerline.classifier")


def classifier_node(state: AgentState, config: RunnableConfig) -> AgentState:
    llm = config["configurable"]["llm"]
    store = get_data_store()
    prompt = CLASSIFIER_PROMPT.format(
        assets=", ".join(store.schema["assets"]),
        time_min=store.schema["time_min"],
        time_max=store.schema["time_max"],
    )
    structured = llm.with_structured_output(ClassificationResult)
    result: ClassificationResult = structured.invoke(
        [
            {"role": "system", "content": prompt},
            {"role": "user", "content": state["user_query"]},
        ]
    )
    logger.info("Classified intent=%s assets=%s", result.intent, result.asset_ids)
    return {
        "intent": result.intent,
        "asset_ids": result.asset_ids or store.schema["assets"][:1],
        "time_range": result.time_range,
        "complexity": result.complexity,
        "next_agent": "supervisor",
        "actions_taken": ["classifier"],
    }
