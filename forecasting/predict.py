from __future__ import annotations

import pandas as pd


def compute_peak_summary(df: pd.DataFrame) -> dict:
    """Summarize the maximum, minimum, average, and timestamp of the peak demand."""
    if df.empty:
        return {
            "max_demand": 0.0,
            "peak_timestamp": None,
            "min_demand": 0.0,
            "avg_demand": 0.0,
            "demand_range": 0.0,
        }

    s = df.sort_values("timestamp").copy()
    if "active_power_kw" not in s.columns:
        raise ValueError("The input data must contain an 'active_power_kw' column.")

    max_row = s.loc[s["active_power_kw"].idxmax()]
    return {
        "max_demand": float(max_row["active_power_kw"]),
        "peak_timestamp": max_row["timestamp"],
        "min_demand": float(s["active_power_kw"].min()),
        "avg_demand": float(s["active_power_kw"].mean()),
        "demand_range": float(s["active_power_kw"].max() - s["active_power_kw"].mean()),
    }
