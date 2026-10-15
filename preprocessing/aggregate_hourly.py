from __future__ import annotations

import pandas as pd


def aggregate_to_hourly(df: pd.DataFrame, timestamp_col: str = "timestamp", value_col: str = "active_power_kw") -> pd.DataFrame:
    if df.empty:
        return df.copy()
    subset = df[[timestamp_col, value_col]].copy()
    subset[timestamp_col] = pd.to_datetime(subset[timestamp_col], errors="coerce")
    subset = subset.dropna(subset=[timestamp_col, value_col])
    subset = subset.sort_values(timestamp_col).drop_duplicates(subset=[timestamp_col], keep="last")
    return subset.set_index(timestamp_col).resample("h").mean().reset_index()
