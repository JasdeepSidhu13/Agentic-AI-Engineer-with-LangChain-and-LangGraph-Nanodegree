import json
import logging
import os

from langchain_core.messages import SystemMessage, ToolMessage
from langchain_openai import ChatOpenAI

from agentic.prompts import RESOLVER_PROMPT
from agentic.state import AgentState
from agentic.tools.knowledge_retrieval import retrieve_knowledge
from agentic.tools.memory_tools import retrieve_long_term_memory, store_long_term_memory

logger = logging.getLogger("udahub.resolver")

_tools = [retrieve_knowledge, retrieve_long_term_memory, store_long_term_memory]
_tools_by_name = {t.name: t for t in _tools}

_llm = None


def _get_llm():
    global _llm
    if _llm is None:
        _llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, base_url=os.environ.get("OPENAI_BASE_URL")).bind_tools(_tools)
    return _llm


def resolver_node(state: AgentState) -> dict:
    """Resolve the ticket using knowledge base retrieval (RAG)."""
    llm = _get_llm()
    messages = [SystemMessage(content=RESOLVER_PROMPT)] + state["messages"]

    response = llm.invoke(messages)
    updated_messages = [response]
    retrieved = []
    confidence = 0.0

    # Iterative tool-calling loop
    max_iterations = 5
    iteration = 0
    while response.tool_calls and iteration < max_iterations:
        iteration += 1
        for tc in response.tool_calls:
            tool_fn = _tools_by_name.get(tc["name"])
            if tool_fn:
                result = tool_fn.invoke(tc["args"])
                logger.info(f"Resolver tool call: {tc['name']}({tc['args']})")
                # Track retrieved articles for confidence scoring
                if tc["name"] == "retrieve_knowledge":
                    try:
                        articles = json.loads(result)
                        retrieved.extend(articles)
                        if articles:
                            confidence = max(
                                confidence,
                                max(a.get("relevance_score", 0) for a in articles),
                            )
                    except json.JSONDecodeError:
                        pass
            else:
                result = json.dumps({"error": f"Unknown tool: {tc['name']}"})

            updated_messages.append(
                ToolMessage(content=result, tool_call_id=tc["id"])
            )

        response = llm.invoke(messages + updated_messages)
        updated_messages.append(response)

    resolution_status = "resolved" if confidence >= 0.6 else "in_progress"
    logger.info(
        f"Resolver finished: confidence={confidence:.4f}, status={resolution_status}, "
        f"articles_retrieved={len(retrieved)}"
    )

    return {
        "messages": updated_messages,
        "retrieved_articles": retrieved,
        "confidence_score": confidence,
        "resolution_status": resolution_status,
    }
