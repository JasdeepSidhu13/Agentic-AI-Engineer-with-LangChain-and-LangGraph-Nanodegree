import pytest

from src.data_loader import get_data_store


@pytest.fixture(autouse=True)
def reset_store():
    import src.data_loader as dl

    dl._STORE = None


def test_dataset_loads():
    store = get_data_store()
    assert store.schema["row_count"] > 0
    assert len(store.schema["assets"]) >= 1


def test_revenue_metrics_query():
    store = get_data_store()
    result = store.query(
        "SELECT ROUND(SUM(revenue_usd), 2) AS total FROM asset_data"
    )
    assert result[0]["total"] is not None


def test_benchmark_comparison_by_asset():
    store = get_data_store()
    rows = store.query(
        """
        SELECT asset_id, SUM(revenue_usd) AS rev
        FROM asset_data
        GROUP BY asset_id
        """
    )
    assert len(rows) == len(store.schema["assets"])
