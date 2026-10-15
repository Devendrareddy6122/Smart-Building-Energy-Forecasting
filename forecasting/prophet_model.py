from __future__ import annotations

import pandas as pd

try:
    from prophet import Prophet
except ImportError:  # pragma: no cover
    Prophet = None


def train_prophet(df: pd.DataFrame) -> object:
    if Prophet is None:
        raise ImportError("The 'prophet' package is not installed.")

    prophet_df = df.rename(columns={"timestamp": "ds", "active_power_kw": "y"})[["ds", "y"]].copy()
    model = Prophet(daily_seasonality=True, weekly_seasonality=True, yearly_seasonality=False)
    model.fit(prophet_df)
    return model


def forecast_prophet(model: object, horizon: int = 24) -> pd.DataFrame:
    future = model.make_future_dataframe(periods=horizon, freq="h")
    forecast = model.predict(future)
    result = forecast[["ds", "yhat", "yhat_lower", "yhat_upper"]].tail(horizon).reset_index(drop=True)
    result = result.rename(columns={"ds": "timestamp", "yhat": "prophet_forecast"})
    return result
