import json

import pytest

from src.data_loader import get_data_store
from src.tools import (
    analyze_state_of_charge_patterns,
    compare_historical_vs_perfect_dispatch,
    compute_revenue_summary,
    identify_high_price_intervals,
)


@pytest.fixture(autouse=True)
def reset_store():
    import src.data_loader as dl
    dl._STORE = None


def test_dataset_loads_one_week():
    store = get_data_store()
    assert store.summary["row_count"] == 672


def test_revenue_summary():
    data = json.loads(compute_revenue_summary.invoke({}))
    assert data["total_perfect_revenue_usd"] >= data["total_historical_revenue_usd"]
    assert data["total_gap_usd"] == pytest.approx(
        data["total_perfect_revenue_usd"] - data["total_historical_revenue_usd"], abs=0.01
    )


def test_high_price_intervals():
    data = json.loads(identify_high_price_intervals.invoke({"top_n": 5}))
    assert len(data["intervals"]) == 5


def test_dispatch_comparison():
    data = json.loads(compare_historical_vs_perfect_dispatch.invoke({"top_n": 5}))
    assert data["total_gap_in_top_intervals_usd"] > 0


def test_soc_patterns():
    data = json.loads(analyze_state_of_charge_patterns.invoke({}))
    assert "high_price_under_discharge_gap_usd" in data
