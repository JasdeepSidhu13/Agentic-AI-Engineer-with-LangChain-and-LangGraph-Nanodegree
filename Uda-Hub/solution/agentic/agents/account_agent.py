import json
import logging
import os

from langchain_core.messages import SystemMessage, ToolMessage
from langchain_openai import ChatOpenAI

from agentic.prompts import ACCOUNT_AGENT_PROMPT
from agentic.state import AgentState
from agentic.tools.mcp_server import (
    account_lookup,
    process_refund,
    reservation_lookup,
    subscription_management,
)
from agentic.tools.memory_tools import retrieve_long_term_memory, store_long_term_memory

logger = logging.getLogger("udahub.account_agent")

_tools = [
    account_lookup,
    subscription_management,
    reservation_lookup,
    process_refund,
    retrieve_long_term_memory,
    store_long_term_memory,
]
_tools_by_name = {t.name: t for t in _tools}

_llm = None


def _get_llm():
    global _llm
    if _llm is None:
        _llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, base_url=os.environ.get("OPENAI_BASE_URL")).bind_tools(_tools)
    return _llm


def account_agent_node(state: AgentState) -> dict:
    """Handle account operations using CultPass DB tools."""
    llm = _get_llm()
    messages = [SystemMessage(content=ACCOUNT_AGENT_PROMPT)] + state["messages"]

    response = llm.invoke(messages)
    updated_messages = [response]
    tool_results = list(state.get("tool_results", []) or [])

    # Iterative tool-calling loop
    max_iterations = 5
    iteration = 0
    while response.tool_calls and iteration < max_iterations:
        iteration += 1
        for tc in response.tool_calls:
            tool_fn = _tools_by_name.get(tc["name"])
            if tool_fn:
                result = tool_fn.invoke(tc["args"])
                logger.info(f"Account agent tool call: {tc['name']}({tc['args']})")
                tool_results.append({
                    "tool": tc["name"],
                    "args": tc["args"],
                    "result": result,
                })
            else:
                result = json.dumps({"error": f"Tool {tc['name']} not found"})

            updated_messages.append(
                ToolMessage(content=result, tool_call_id=tc["id"])
            )

        response = llm.invoke(messages + updated_messages)
        updated_messages.append(response)

    logger.info(f"Account agent finished: {len(tool_results)} tool calls made")

    return {
        "messages": updated_messages,
        "tool_results": tool_results,
        "resolution_status": "resolved",
    }
