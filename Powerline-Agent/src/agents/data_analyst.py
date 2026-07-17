from __future__ import annotations

import json
import logging

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.runnables import RunnableConfig
from langgraph.prebuilt import create_react_agent

from src.prompts import DATA_ANALYST_PROMPT
from src.state import AgentState
from src.tools.data_tools import DATA_TOOLS

logger = logging.getLogger("powerline.data_analyst")


def data_analyst_node(state: AgentState, config: RunnableConfig) -> AgentState:
    llm = config["configurable"]["llm"]
    prompt = DATA_ANALYST_PROMPT.format(
        intent=state.get("intent", "exploratory"),
        asset_ids=state.get("asset_ids", []),
        time_range=state.get("time_range", {}),
    )
    agent = create_react_agent(llm, DATA_TOOLS, prompt=SystemMessage(content=prompt))
    result = agent.invoke({"messages": [HumanMessage(content=state["user_query"])]})
    tool_outputs = [
        m.content for m in result["messages"] if m.type == "tool"
    ]
    data_results = {"tool_outputs": tool_outputs, "message_count": len(result["messages"])}
    logger.info("Data analyst produced %d tool outputs", len(tool_outputs))
    return {
        "data_results": data_results,
        "messages": result["messages"],
        "next_agent": "supervisor",
        "actions_taken": ["data_analyst"],
    }
