from __future__ import annotations

import pandas as pd


def baseline_forecast(df: pd.DataFrame, horizon: int = 24) -> pd.Series:
    """Predict each future hourly value from the equivalent hour on the previous day."""
    if df.empty:
        return pd.Series(dtype=float)

    series = df.sort_values("timestamp").copy()
    if "active_power_kw" not in series.columns:
        raise ValueError("The input data must contain an 'active_power_kw' column.")

    last_ts = series["timestamp"].iloc[-1]
    if len(series) < 24:
        prior_values = series["active_power_kw"].iloc[:].tolist()
    else:
        prior_values = series["active_power_kw"].iloc[-24:].tolist()

    forecast_values = []
    for offset in range(horizon):
        idx = offset % 24
        if idx < len(prior_values):
            forecast_values.append(float(prior_values[idx]))
        else:
            forecast_values.append(float(prior_values[-1]))

    result = pd.Series(forecast_values, name="baseline_forecast")
    result.index = pd.date_range(start=last_ts + pd.Timedelta(hours=1), periods=horizon, freq="h")
    return result
