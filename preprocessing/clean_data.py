from __future__ import annotations

import logging
from typing import Iterable

import pandas as pd

logger = logging.getLogger(__name__)


def parse_datetime_column(df: pd.DataFrame, date_col: str = "Date", time_col: str = "Time") -> pd.DataFrame:
    """Combine UCI date and time columns into a single timezone-naive timestamp."""
    if df.empty:
        return df.copy()

    parsed = df.copy()
    parsed["timestamp"] = pd.to_datetime(
        parsed[date_col].astype(str) + " " + parsed[time_col].astype(str),
        format="%d/%m/%Y %H:%M:%S",
        errors="coerce",
    )
    return parsed


def _validate_numeric(values: Iterable[object]) -> pd.Series:
    return pd.to_numeric(pd.Series(values), errors="coerce")


def preprocess_power_data(df: pd.DataFrame, target_col: str = "Global_active_power") -> pd.DataFrame:
    """Clean minute-level UCI power data and aggregate it into hourly averages in kW."""
    cleaned = parse_datetime_column(df)
    cleaned = cleaned.loc[:, ["timestamp", target_col]].copy()
    cleaned[target_col] = _validate_numeric(cleaned[target_col])
    cleaned = cleaned.dropna(subset=["timestamp", target_col]).copy()
    cleaned = cleaned.sort_values("timestamp").drop_duplicates(subset=["timestamp"], keep="last")

    cleaned = cleaned.rename(columns={target_col: "active_power_kw"})
    cleaned = cleaned.set_index("timestamp").asfreq("min", fill_value=None)
    hourly = cleaned.resample("h").mean().reset_index().rename(columns={"timestamp": "timestamp"})
    hourly["active_power_kw"] = pd.to_numeric(hourly["active_power_kw"], errors="coerce")
    hourly = hourly.dropna(subset=["active_power_kw"]).reset_index(drop=True)
    logger.info("Hourly aggregation finished with %s rows", len(hourly))
    return hourly
