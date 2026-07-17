from __future__ import annotations

import json
import logging

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.runnables import RunnableConfig
from langgraph.prebuilt import create_react_agent

from src.prompts import MARKET_ADVISOR_PROMPT
from src.retrieval.rag import retrieve_domain_knowledge
from src.state import AgentState
from src.tools.data_tools import MEMORY_TOOLS

logger = logging.getLogger("powerline.market_advisor")


def market_advisor_node(state: AgentState, config: RunnableConfig) -> AgentState:
    llm = config["configurable"]["llm"]
    prompt = MARKET_ADVISOR_PROMPT.format(
        data_results=json.dumps(state.get("data_results", {}), default=str)[:4000],
        evaluator_feedback=state.get("evaluator_feedback") or "None",
    )
    tools = [retrieve_domain_knowledge, *MEMORY_TOOLS]
    agent = create_react_agent(llm, tools, prompt=SystemMessage(content=prompt))
    result = agent.invoke({"messages": [HumanMessage(content=state["user_query"])]})
    final_message = result["messages"][-1].content
    confidence = 0.8 if state.get("data_results") else 0.65
    recommendations = []
    if "recommend" in final_message.lower():
        recommendations = [line.strip("- ") for line in final_message.splitlines() if line.strip().startswith("-")]
    logger.info("Market advisor confidence=%.2f", confidence)
    return {
        "draft_answer": final_message,
        "recommendations": recommendations,
        "confidence_score": confidence,
        "messages": result["messages"],
        "next_agent": "supervisor",
        "actions_taken": ["market_advisor"],
    }
