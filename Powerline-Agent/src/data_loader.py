from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "data.csv"

# Maps canonical names to acceptable CSV column aliases for generalization.
COLUMN_ALIASES: dict[str, list[str]] = {
    "timestamp": ["timestamp", "datetime", "time", "interval_start"],
    "market_price_usd_mwh": ["market_price_usd_mwh", "price", "lmp", "spot_price"],
    "historical_power_mw": ["historical_power_mw", "historical_power", "actual_power_mw", "power_mw"],
    "perfect_power_mw": ["perfect_power_mw", "perfect_power", "counterfactual_power_mw"],
    "historical_revenue_usd": ["historical_revenue_usd", "historical_revenue", "actual_revenue_usd", "revenue_usd"],
    "perfect_revenue_usd": ["perfect_revenue_usd", "perfect_revenue", "benchmark_revenue_usd", "counterfactual_revenue_usd"],
    "state_of_charge_pct": ["state_of_charge_pct", "soc", "soc_pct", "state_of_charge"],
    "perfect_state_of_charge_pct": ["perfect_state_of_charge_pct", "perfect_soc", "perfect_soc_pct"],
}


def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    lower_map = {col.lower(): col for col in df.columns}
    rename: dict[str, str] = {}
    for canonical, aliases in COLUMN_ALIASES.items():
        for alias in aliases:
            if alias.lower() in lower_map:
                rename[lower_map[alias.lower()]] = canonical
                break
    normalized = df.rename(columns=rename)
    required = [
        "timestamp",
        "historical_revenue_usd",
        "perfect_revenue_usd",
        "historical_power_mw",
        "perfect_power_mw",
        "market_price_usd_mwh",
        "state_of_charge_pct",
    ]
    missing = [col for col in required if col not in normalized.columns]
    if missing:
        raise ValueError(f"CSV missing required columns after normalization: {missing}")
    normalized["timestamp"] = pd.to_datetime(normalized["timestamp"])
    return normalized.sort_values("timestamp").reset_index(drop=True)


class DataStore:
    """In-memory view of interval-level battery performance data."""

    def __init__(self, csv_path: Path | None = None):
        path = csv_path or DATA_PATH
        self.df = _normalize_columns(pd.read_csv(path))

    @property
    def summary(self) -> dict[str, Any]:
        return {
            "row_count": len(self.df),
            "time_min": str(self.df["timestamp"].min()),
            "time_max": str(self.df["timestamp"].max()),
            "columns": list(self.df.columns),
        }


_STORE: DataStore | None = None


def get_data_store(csv_path: Path | None = None) -> DataStore:
    global _STORE
    if csv_path is not None:
        _STORE = DataStore(csv_path)
        return _STORE
    if _STORE is None:
        _STORE = DataStore()
    return _STORE
