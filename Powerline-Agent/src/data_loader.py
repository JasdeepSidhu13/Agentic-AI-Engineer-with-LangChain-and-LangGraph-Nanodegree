from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

import pandas as pd

DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "data.csv"

COLUMN_ALIASES = {
    "timestamp": ["timestamp", "datetime", "time", "interval_start"],
    "asset_id": ["asset_id", "asset", "project_id", "asset_name"],
    "market": ["market", "region", "iso"],
    "power_mw": ["power_mw", "power", "dispatch_mw", "net_power_mw"],
    "energy_mwh": ["energy_mwh", "energy", "mwh"],
    "state_of_charge_pct": ["state_of_charge_pct", "soc", "soc_pct", "state_of_charge"],
    "market_price_usd_mwh": ["market_price_usd_mwh", "price", "lmp", "spot_price"],
    "revenue_usd": ["revenue_usd", "revenue", "actual_revenue"],
    "benchmark_revenue_usd": ["benchmark_revenue_usd", "benchmark_revenue", "perfect_revenue"],
    "capture_rate": ["capture_rate", "capture", "performance_ratio"],
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
    required = ["timestamp", "asset_id", "revenue_usd", "benchmark_revenue_usd"]
    missing = [col for col in required if col not in normalized.columns]
    if missing:
        raise ValueError(f"CSV missing required columns after normalization: {missing}")
    normalized["timestamp"] = pd.to_datetime(normalized["timestamp"])
    return normalized


class DataStore:
    def __init__(self, csv_path: Path | None = None):
        path = csv_path or DATA_PATH
        self.df = _normalize_columns(pd.read_csv(path))
        self.conn = sqlite3.connect(":memory:", check_same_thread=False)
        self.df.to_sql("asset_data", self.conn, index=False, if_exists="replace")
        self.schema = {
            "columns": list(self.df.columns),
            "assets": sorted(self.df["asset_id"].unique().tolist()),
            "time_min": str(self.df["timestamp"].min()),
            "time_max": str(self.df["timestamp"].max()),
            "row_count": len(self.df),
        }

    def query(self, sql: str, params: tuple[Any, ...] = ()) -> list[dict[str, Any]]:
        cursor = self.conn.execute(sql, params)
        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]

    def describe(self) -> dict[str, Any]:
        return self.schema


_STORE: DataStore | None = None


def get_data_store() -> DataStore:
    global _STORE
    if _STORE is None:
        _STORE = DataStore()
    return _STORE
