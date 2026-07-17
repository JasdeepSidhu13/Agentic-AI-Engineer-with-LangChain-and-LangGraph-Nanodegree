from src.agents.supervisor import _route


def test_route_to_classifier_when_no_intent():
    assert _route({"intent": None}) == "classifier"


def test_route_to_data_analyst_for_benchmark():
    state = {"intent": "benchmark_analysis", "data_results": None}
    assert _route(state) == "data_analyst"


def test_route_to_market_advisor_when_data_ready():
    state = {
        "intent": "benchmark_analysis",
        "data_results": {"tool_outputs": ["{}"]},
        "draft_answer": None,
    }
    assert _route(state) == "market_advisor"


def test_route_finish_when_resolved():
    state = {"resolution_status": "resolved"}
    assert _route(state) == "finish"
