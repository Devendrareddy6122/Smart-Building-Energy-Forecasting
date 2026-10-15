from __future__ import annotations

import warnings

import pandas as pd
from statsmodels.tsa.arima.model import ARIMA

warnings.filterwarnings("ignore")


def train_arima(series: pd.Series, order: tuple[int, int, int] = (2, 1, 2)) -> ARIMA:
    model = ARIMA(series, order=order, enforce_stationarity=False, enforce_invertibility=False)
    return model.fit()


def forecast_arima(series: pd.Series, horizon: int = 24, order: tuple[int, int, int] = (2, 1, 2)) -> pd.DataFrame:
    fitted = train_arima(series, order=order)
    pred = fitted.forecast(steps=horizon)
    forecast_df = pd.DataFrame({"timestamp": pd.date_range(start=series.index[-1] + pd.Timedelta(hours=1), periods=horizon, freq="h"), "arima_forecast": pred.values})
    return forecast_df
