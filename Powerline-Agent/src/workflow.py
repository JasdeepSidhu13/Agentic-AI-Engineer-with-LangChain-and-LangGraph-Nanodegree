from __future__ import annotations

import os

from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph

from src.agents.classifier import classifier_node
from src.agents.data_analyst import data_analyst_node
from src.agents.evaluator import evaluator_node
from src.agents.market_advisor import market_advisor_node
from src.agents.supervisor import route_from_supervisor, supervisor_node
from src.state import AgentState


def build_app():
    graph = StateGraph(AgentState)

    graph.add_node("supervisor", supervisor_node)
    graph.add_node("classifier", classifier_node)
    graph.add_node("data_analyst", data_analyst_node)
    graph.add_node("market_advisor", market_advisor_node)
    graph.add_node("evaluator", evaluator_node)

    graph.set_entry_point("supervisor")

    for node in ["classifier", "data_analyst", "market_advisor", "evaluator"]:
        graph.add_edge(node, "supervisor")

    graph.add_conditional_edges(
        "supervisor",
        route_from_supervisor,
        {
            "classifier": "classifier",
            "data_analyst": "data_analyst",
            "market_advisor": "market_advisor",
            "evaluator": "evaluator",
            "finish": END,
        },
    )

    return graph.compile(checkpointer=MemorySaver())


def get_llm() -> ChatOpenAI:
    return ChatOpenAI(
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        temperature=0,
        api_key=os.getenv("OPENAI_API_KEY"),
    )
