from __future__ import annotations

import pandas as pd

from forecasting.arima_model import forecast_arima
from forecasting.baseline import baseline_forecast
from forecasting.predict import compute_peak_summary
from forecasting.prophet_model import forecast_prophet, train_prophet


def _forecast_candidates(history: pd.DataFrame, horizon: int) -> dict[str, pd.Series]:
    """Fit available forecasters and return aligned, non-negative predictions."""
    candidates: dict[str, pd.Series] = {}
    series = history.set_index("timestamp")["active_power_kw"]

    # The previous-day profile is a strong and inexpensive reference model.
    baseline = baseline_forecast(history, horizon=horizon)
    if len(baseline) == horizon:
        candidates["baseline"] = pd.Series(baseline.to_numpy(), index=baseline.index)

    try:
        arima = forecast_arima(series, horizon=horizon)
        candidates["arima"] = pd.Series(arima["arima_forecast"].to_numpy(), index=arima["timestamp"])
    except Exception:
        pass

    # Prophet needs enough observations to estimate its seasonal components.
    if len(history) >= 48:
        try:
            prophet = forecast_prophet(train_prophet(history), horizon=horizon)
            candidates["prophet"] = pd.Series(prophet["prophet_forecast"].to_numpy(), index=prophet["timestamp"])
        except Exception:
            pass

    return {name: values.clip(lower=0) for name, values in candidates.items()}


def train_and_forecast(df: pd.DataFrame, horizon: int = 24) -> dict:
    numeric = df.sort_values("timestamp").copy()
    numeric["active_power_kw"] = pd.to_numeric(numeric["active_power_kw"], errors="coerce")
    numeric = numeric.dropna(subset=["active_power_kw"]).reset_index(drop=True)

    if horizon < 1:
        raise ValueError("horizon must be at least 1")

    # Choose the model from a chronological holdout matching the requested horizon.
    # A one-day holdout requires at least two days of history for a baseline.
    selected_model = "baseline"
    validation_scores: dict[str, float] = {}
    validation_predictions: dict[str, pd.Series] = {}
    validation_actual = pd.DataFrame(columns=["timestamp", "actual_demand"])
    if len(numeric) > horizon:
        validation_history = numeric.iloc[:-horizon]
        validation_rows = numeric.iloc[-horizon:]
        actual = validation_rows["active_power_kw"].to_numpy(dtype=float)
        validation_actual = validation_rows[["timestamp", "active_power_kw"]].rename(
            columns={"active_power_kw": "actual_demand"}
        ).reset_index(drop=True)
        for name, prediction in _forecast_candidates(validation_history, horizon).items():
            if len(prediction) == horizon:
                validation_predictions[name] = prediction.reset_index(drop=True)
                validation_scores[name] = float((abs(actual - prediction.to_numpy())).mean())
        if validation_scores:
            selected_model = min(validation_scores, key=validation_scores.get)

    predictions = _forecast_candidates(numeric, horizon)
    if selected_model not in predictions:
        selected_model = min(predictions, key=lambda name: validation_scores.get(name, float("inf")))

    timestamps = pd.date_range(
        start=numeric["timestamp"].iloc[-1] + pd.Timedelta(hours=1), periods=horizon, freq="h"
    )
    merged = pd.DataFrame({"timestamp": timestamps})
    for name, values in predictions.items():
        merged[f"{name}_forecast"] = values.to_numpy()
    merged["selected_model"] = selected_model
    merged["selected_forecast"] = merged[f"{selected_model}_forecast"]
    baseline = predictions.get("baseline", pd.Series(dtype=float)).rename("baseline_forecast")
    arima_forecast = merged[["timestamp", "arima_forecast"]] if "arima_forecast" in merged else pd.DataFrame(columns=["timestamp", "arima_forecast"])
    prophet_forecast = merged[["timestamp", "prophet_forecast"]] if "prophet_forecast" in merged else pd.DataFrame(columns=["timestamp", "prophet_forecast"])

    return {
        "arima": arima_forecast,
        "prophet": prophet_forecast,
        "combined": merged,
        "peak": compute_peak_summary(numeric),
        "baseline": baseline,
        "selected_model": selected_model,
        "validation_mae": validation_scores,
        "validation_actual": validation_actual,
        "validation_predictions": validation_predictions,
    }
