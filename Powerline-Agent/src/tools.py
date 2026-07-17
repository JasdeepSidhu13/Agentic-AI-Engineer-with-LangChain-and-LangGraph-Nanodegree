from __future__ import annotations

import json
from typing import Any

import pandas as pd
from langchain_core.tools import tool

from src.data_loader import get_data_store


def _df() -> pd.DataFrame:
    return get_data_store().df.copy()


def _add_gap_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["revenue_gap_usd"] = df["perfect_revenue_usd"] - df["historical_revenue_usd"]
    df["power_gap_mw"] = df["perfect_power_mw"] - df["historical_power_mw"]
    return df


@tool
def compute_revenue_summary() -> str:
    """Compute total historical revenue, total perfect revenue, and the performance gap."""
    df = _df()
    historical = round(float(df["historical_revenue_usd"].sum()), 2)
    perfect = round(float(df["perfect_revenue_usd"].sum()), 2)
    gap = round(perfect - historical, 2)
    gap_pct = round(gap / perfect * 100, 2) if perfect else 0.0
    return json.dumps(
        {
            "total_historical_revenue_usd": historical,
            "total_perfect_revenue_usd": perfect,
            "total_gap_usd": gap,
            "gap_pct_of_perfect": gap_pct,
            "interval_count": len(df),
        }
    )


@tool
def identify_high_price_intervals(top_n: int = 10) -> str:
    """Return the highest-price intervals and whether historical dispatch captured the opportunity."""
    df = _add_gap_columns(_df())
    top = df.nlargest(top_n, "market_price_usd_mwh")
    rows = []
    for _, row in top.iterrows():
        rows.append(
            {
                "timestamp": str(row["timestamp"]),
                "market_price_usd_mwh": round(float(row["market_price_usd_mwh"]), 2),
                "historical_power_mw": round(float(row["historical_power_mw"]), 2),
                "perfect_power_mw": round(float(row["perfect_power_mw"]), 2),
                "revenue_gap_usd": round(float(row["revenue_gap_usd"]), 2),
                "missed_discharge": float(row["historical_power_mw"]) < float(row["perfect_power_mw"]),
            }
        )
    missed = sum(1 for r in rows if r["missed_discharge"])
    return json.dumps({"top_n": top_n, "intervals": rows, "missed_discharge_count": missed})


@tool
def compare_historical_vs_perfect_dispatch(top_n: int = 10) -> str:
    """Compare historical and perfect dispatch for the intervals with the largest revenue gap."""
    df = _add_gap_columns(_df())
    worst = df.nlargest(top_n, "revenue_gap_usd")
    rows = []
    for _, row in worst.iterrows():
        rows.append(
            {
                "timestamp": str(row["timestamp"]),
                "market_price_usd_mwh": round(float(row["market_price_usd_mwh"]), 2),
                "historical_power_mw": round(float(row["historical_power_mw"]), 2),
                "perfect_power_mw": round(float(row["perfect_power_mw"]), 2),
                "historical_revenue_usd": round(float(row["historical_revenue_usd"]), 2),
                "perfect_revenue_usd": round(float(row["perfect_revenue_usd"]), 2),
                "revenue_gap_usd": round(float(row["revenue_gap_usd"]), 2),
            }
        )
    total_gap_in_worst = round(sum(r["revenue_gap_usd"] for r in rows), 2)
    return json.dumps(
        {
            "top_n": top_n,
            "largest_gap_intervals": rows,
            "total_gap_in_top_intervals_usd": total_gap_in_worst,
        }
    )


@tool
def analyze_state_of_charge_patterns() -> str:
    """Analyze SOC patterns during high-price periods and low-SOC constraints on discharge."""
    df = _add_gap_columns(_df())
    price_threshold = float(df["market_price_usd_mwh"].quantile(0.75))
    high_price = df[df["market_price_usd_mwh"] >= price_threshold]

    low_soc_high_price = high_price[high_price["state_of_charge_pct"] < 30]
    under_discharge = high_price[high_price["historical_power_mw"] < high_price["perfect_power_mw"]]

    return json.dumps(
        {
            "high_price_threshold_usd_mwh": round(price_threshold, 2),
            "high_price_interval_count": len(high_price),
            "high_price_under_discharge_count": len(under_discharge),
            "high_price_under_discharge_gap_usd": round(float(under_discharge["revenue_gap_usd"].sum()), 2),
            "low_soc_during_high_price_count": len(low_soc_high_price),
            "low_soc_during_high_price_gap_usd": round(float(low_soc_high_price["revenue_gap_usd"].sum()), 2),
            "avg_soc_during_high_price": round(float(high_price["state_of_charge_pct"].mean()), 2),
            "avg_soc_overall": round(float(df["state_of_charge_pct"].mean()), 2),
        }
    )


@tool
def get_dataset_info() -> str:
    """Return dataset metadata (time range, interval count, columns)."""
    return json.dumps(get_data_store().summary)


ANALYSIS_TOOLS = [
    compute_revenue_summary,
    identify_high_price_intervals,
    compare_historical_vs_perfect_dispatch,
    analyze_state_of_charge_patterns,
    get_dataset_info,
]
