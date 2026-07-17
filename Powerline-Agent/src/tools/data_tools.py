from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any

from langchain_core.tools import tool

from src.data_loader import get_data_store

OUTPUT_DIR = Path(__file__).resolve().parents[1] / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)
MEMORY_DB = Path(__file__).resolve().parents[1] / "memory.db"


def _init_memory_db() -> None:
    with sqlite3.connect(MEMORY_DB) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS long_term_memory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                category TEXT NOT NULL,
                summary TEXT NOT NULL,
                details TEXT,
                created_at TEXT NOT NULL
            )
            """
        )


@tool
def query_asset_data(
    asset_id: str | None = None,
    start: str | None = None,
    end: str | None = None,
    limit: int = 20,
) -> str:
    """Query battery asset operational rows from the dataset."""
    store = get_data_store()
    clauses = ["1=1"]
    params: list[Any] = []
    if asset_id:
        clauses.append("asset_id = ?")
        params.append(asset_id)
    if start:
        clauses.append("timestamp >= ?")
        params.append(start)
    if end:
        clauses.append("timestamp <= ?")
        params.append(end)
    sql = f"SELECT * FROM asset_data WHERE {' AND '.join(clauses)} ORDER BY timestamp LIMIT ?"
    params.append(limit)
    rows = store.query(sql, tuple(params))
    return json.dumps({"row_count": len(rows), "rows": rows}, default=str)


@tool
def compute_revenue_metrics(
    asset_id: str | None = None,
    start: str | None = None,
    end: str | None = None,
) -> str:
    """Compute total revenue, benchmark revenue, average capture rate, and interval count."""
    store = get_data_store()
    clauses = ["1=1"]
    params: list[Any] = []
    if asset_id:
        clauses.append("asset_id = ?")
        params.append(asset_id)
    if start:
        clauses.append("timestamp >= ?")
        params.append(start)
    if end:
        clauses.append("timestamp <= ?")
        params.append(end)
    where = " AND ".join(clauses)
    sql = f"""
        SELECT
            COUNT(*) AS interval_count,
            ROUND(SUM(revenue_usd), 2) AS total_revenue_usd,
            ROUND(SUM(benchmark_revenue_usd), 2) AS total_benchmark_usd,
            ROUND(AVG(capture_rate), 4) AS avg_capture_rate,
            ROUND(MIN(capture_rate), 4) AS min_capture_rate,
            ROUND(MAX(capture_rate), 4) AS max_capture_rate
        FROM asset_data
        WHERE {where}
    """
    result = store.query(sql, tuple(params))[0]
    if result["total_benchmark_usd"]:
        result["portfolio_capture_rate"] = round(
            result["total_revenue_usd"] / result["total_benchmark_usd"], 4
        )
    return json.dumps(result, default=str)


@tool
def benchmark_comparison(
    group_by: str = "asset_id",
    start: str | None = None,
    end: str | None = None,
) -> str:
    """Compare actual revenue against benchmark grouped by asset or day."""
    store = get_data_store()
    if group_by not in {"asset_id", "day"}:
        return json.dumps({"error": "group_by must be 'asset_id' or 'day'"})
    group_expr = "asset_id" if group_by == "asset_id" else "date(timestamp)"
    clauses = ["1=1"]
    params: list[Any] = []
    if start:
        clauses.append("timestamp >= ?")
        params.append(start)
    if end:
        clauses.append("timestamp <= ?")
        params.append(end)
    where = " AND ".join(clauses)
    sql = f"""
        SELECT
            {group_expr} AS group_key,
            ROUND(SUM(revenue_usd), 2) AS actual_revenue_usd,
            ROUND(SUM(benchmark_revenue_usd), 2) AS benchmark_revenue_usd,
            ROUND(SUM(benchmark_revenue_usd - revenue_usd), 2) AS revenue_gap_usd,
            ROUND(SUM(revenue_usd) * 1.0 / NULLIF(SUM(benchmark_revenue_usd), 0), 4) AS capture_rate
        FROM asset_data
        WHERE {where}
        GROUP BY {group_expr}
        ORDER BY capture_rate ASC
    """
    rows = store.query(sql, tuple(params))
    return json.dumps({"comparisons": rows}, default=str)


@tool
def time_series_aggregate(
    asset_id: str,
    metric: str = "revenue_usd",
    freq: str = "D",
    start: str | None = None,
    end: str | None = None,
) -> str:
    """Aggregate a metric over hourly (H) or daily (D) intervals for one asset."""
    store = get_data_store()
    allowed_metrics = {"revenue_usd", "benchmark_revenue_usd", "capture_rate", "market_price_usd_mwh"}
    if metric not in allowed_metrics:
        return json.dumps({"error": f"metric must be one of {sorted(allowed_metrics)}"})
    freq_map = {"H": "hour", "D": "day"}
    if freq not in freq_map:
        return json.dumps({"error": "freq must be 'H' or 'D'"})
    clauses = ["asset_id = ?"]
    params: list[Any] = [asset_id]
    if start:
        clauses.append("timestamp >= ?")
        params.append(start)
    if end:
        clauses.append("timestamp <= ?")
        params.append(end)
    where = " AND ".join(clauses)
    sql = f"""
        SELECT
            strftime('%Y-%m-%d', timestamp) AS period,
            ROUND(SUM(revenue_usd), 2) AS revenue_usd,
            ROUND(AVG({metric}), 4) AS metric_value,
            COUNT(*) AS intervals
        FROM asset_data
        WHERE {where}
        GROUP BY period
        ORDER BY period
    """
    rows = store.query(sql, tuple(params))
    return json.dumps({"asset_id": asset_id, "metric": metric, "series": rows}, default=str)


@tool
def generate_chart(
    asset_id: str,
    metric: str = "revenue_usd",
    start: str | None = None,
    end: str | None = None,
) -> str:
    """Generate a daily time-series chart for an asset metric and return the file path."""
    import matplotlib.pyplot as plt

    store = get_data_store()
    clauses = ["asset_id = ?"]
    params: list[Any] = [asset_id]
    if start:
        clauses.append("timestamp >= ?")
        params.append(start)
    if end:
        clauses.append("timestamp <= ?")
        params.append(end)
    where = " AND ".join(clauses)
    sql = f"""
        SELECT strftime('%Y-%m-%d', timestamp) AS day, SUM({metric}) AS value
        FROM asset_data
        WHERE {where}
        GROUP BY day
        ORDER BY day
    """
    rows = store.query(sql, tuple(params))
    if not rows:
        return json.dumps({"error": "No data for chart"})
    days = [row["day"] for row in rows]
    values = [row["value"] for row in rows]
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(days, values, marker="o")
    ax.set_title(f"{metric} — {asset_id}")
    ax.set_xlabel("Day")
    ax.set_ylabel(metric)
    ax.tick_params(axis="x", rotation=45)
    fig.tight_layout()
    path = OUTPUT_DIR / f"{asset_id}_{metric}_chart.png"
    fig.savefig(path)
    plt.close(fig)
    return json.dumps({"chart_path": str(path), "points": len(rows)})


@tool
def get_dataset_summary() -> str:
    """Return dataset schema, assets, and time range metadata."""
    return json.dumps(get_data_store().describe(), default=str)


@tool
def store_long_term_memory(
    user_id: str,
    category: str,
    summary: str,
    details: str = "",
) -> str:
    """Store a long-term memory entry for a user."""
    _init_memory_db()
    with sqlite3.connect(MEMORY_DB) as conn:
        conn.execute(
            "INSERT INTO long_term_memory (user_id, category, summary, details, created_at) VALUES (?, ?, ?, ?, ?)",
            (user_id, category, summary, details, datetime.utcnow().isoformat()),
        )
    return json.dumps({"stored": True, "category": category})


@tool
def retrieve_long_term_memory(user_id: str, limit: int = 5) -> str:
    """Retrieve recent long-term memory entries for a user."""
    _init_memory_db()
    with sqlite3.connect(MEMORY_DB) as conn:
        rows = conn.execute(
            """
            SELECT category, summary, details, created_at
            FROM long_term_memory
            WHERE user_id = ?
            ORDER BY id DESC
            LIMIT ?
            """,
            (user_id, limit),
        ).fetchall()
    memories = [
        {"category": r[0], "summary": r[1], "details": r[2], "created_at": r[3]}
        for r in rows
    ]
    return json.dumps({"memories": memories})


DATA_TOOLS = [
    query_asset_data,
    compute_revenue_metrics,
    benchmark_comparison,
    time_series_aggregate,
    generate_chart,
    get_dataset_summary,
]

MEMORY_TOOLS = [store_long_term_memory, retrieve_long_term_memory]

ALL_TOOLS = DATA_TOOLS + MEMORY_TOOLS
