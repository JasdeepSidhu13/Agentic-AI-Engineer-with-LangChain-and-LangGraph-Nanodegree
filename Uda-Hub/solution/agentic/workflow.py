import logging
import os
import sys

from dotenv import load_dotenv

# Ensure solution root is on path
_SOLUTION_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _SOLUTION_ROOT not in sys.path:
    sys.path.insert(0, _SOLUTION_ROOT)

load_dotenv(os.path.join(_SOLUTION_ROOT, ".env"))

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph

from agentic.agents.account_agent import account_agent_node
from agentic.agents.classifier import classifier_node
from agentic.agents.escalation import escalation_node
from agentic.agents.resolver import resolver_node
from agentic.agents.supervisor import supervisor_node
from agentic.state import AgentState

# --- Logging ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s %(message)s",
)
logger = logging.getLogger("udahub.workflow")


# --- Routing Functions ---
def route_after_supervisor(state: AgentState) -> str:
    """Conditional edge from supervisor to the next agent."""
    next_agent = state.get("next_agent", "classifier")
    logger.info(f"Routing from supervisor to: {next_agent}")

    if next_agent == "FINISH":
        return END
    if next_agent in ("classifier", "resolver", "account_agent", "escalation"):
        return next_agent

    # Fallback: if unknown agent name, go to classifier
    logger.warning(f"Unknown next_agent '{next_agent}', defaulting to classifier")
    return "classifier"


# --- Build the Graph ---
def build_graph() -> StateGraph:
    graph = StateGraph(AgentState)

    # Add nodes
    graph.add_node("supervisor", supervisor_node)
    graph.add_node("classifier", classifier_node)
    graph.add_node("resolver", resolver_node)
    graph.add_node("account_agent", account_agent_node)
    graph.add_node("escalation", escalation_node)

    # Entry: always start with supervisor
    graph.add_edge(START, "supervisor")

    # Supervisor conditionally routes to any agent or END
    graph.add_conditional_edges(
        "supervisor",
        route_after_supervisor,
        {
            "classifier": "classifier",
            "resolver": "resolver",
            "account_agent": "account_agent",
            "escalation": "escalation",
            END: END,
        },
    )

    # After each specialist, return to supervisor for next decision
    graph.add_edge("classifier", "supervisor")
    graph.add_edge("resolver", "supervisor")
    graph.add_edge("account_agent", "supervisor")

    # Escalation terminates the flow
    graph.add_edge("escalation", END)

    return graph


# --- Compile with checkpointer (short-term memory via thread_id) ---
checkpointer = MemorySaver()
orchestrator = build_graph().compile(checkpointer=checkpointer)
