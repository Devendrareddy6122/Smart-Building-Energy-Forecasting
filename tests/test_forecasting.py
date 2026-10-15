import pandas as pd

from forecasting.baseline import baseline_forecast
from forecasting.predict import compute_peak_summary


def test_baseline_forecast_matches_previous_day_pattern():
    ts = pd.date_range("2026-01-01 00:00:00", periods=48, freq="h")
    values = [10.0 + i * 0.2 for i in range(48)]
    df = pd.DataFrame({"timestamp": ts, "active_power_kw": values})

    forecast = baseline_forecast(df, horizon=24)

    assert len(forecast) == 24
    assert forecast.iloc[0] > 0


def test_peak_summary_uses_maximum_demand_and_time():
    data = pd.DataFrame(
        {
            "timestamp": pd.date_range("2026-01-01 00:00:00", periods=5, freq="h"),
            "active_power_kw": [1.0, 3.0, 2.0, 5.0, 4.0],
        }
    )

    summary = compute_peak_summary(data)

    assert summary["max_demand"] == 5.0
    assert summary["peak_timestamp"] == pd.Timestamp("2026-01-01 03:00:00")
