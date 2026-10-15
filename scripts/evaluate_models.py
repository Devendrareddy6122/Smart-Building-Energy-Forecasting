from __future__ import annotations

from pathlib import Path

import pandas as pd

from forecasting.arima_model import forecast_arima
from forecasting.evaluate import mae_score, mape_score, rmse_score
from forecasting.predict import compute_peak_summary
from forecasting.prophet_model import forecast_prophet, train_prophet


def main() -> None:
    data_path = Path("data/processed/hourly_consumption.csv")
    df = pd.read_csv(data_path)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.sort_values("timestamp").reset_index(drop=True)

    train = df.iloc[:-24].copy()
    test = df.iloc[-24:].copy()

    arima_forecast = forecast_arima(train.set_index("timestamp")["active_power_kw"], horizon=24, order=(2, 1, 2))
    prophet_model = train_prophet(train)
    prophet_forecast = forecast_prophet(prophet_model, horizon=24)

    comparison = test[["timestamp", "active_power_kw"]].copy()
    comparison = comparison.rename(columns={"active_power_kw": "actual_demand"})
    comparison["arima_forecast"] = arima_forecast["arima_forecast"].to_numpy()
    comparison["prophet_forecast"] = prophet_forecast["prophet_forecast"].to_numpy()
    comparison = comparison.sort_values("timestamp").reset_index(drop=True)

    metrics = {
        "ARIMA": {
            "MAE": mae_score(test["active_power_kw"].values, comparison["arima_forecast"].values),
            "RMSE": rmse_score(test["active_power_kw"].values, comparison["arima_forecast"].values),
            "MAPE": mape_score(test["active_power_kw"].values, comparison["arima_forecast"].values),
        },
        "Prophet": {
            "MAE": mae_score(test["active_power_kw"].values, comparison["prophet_forecast"].values),
            "RMSE": rmse_score(test["active_power_kw"].values, comparison["prophet_forecast"].values),
            "MAPE": mape_score(test["active_power_kw"].values, comparison["prophet_forecast"].values),
        },
    }

    next_24 = pd.DataFrame(
        {
            "timestamp": pd.date_range(start=df["timestamp"].max() + pd.Timedelta(hours=1), periods=24, freq="h"),
            "arima_forecast": arima_forecast["arima_forecast"].to_numpy(),
            "prophet_forecast": prophet_forecast["prophet_forecast"].to_numpy(),
        }
    )

    comparison.to_csv("data/processed/forecast_comparison.csv", index=False)
    next_24.to_csv("data/processed/next_24h_forecast.csv", index=False)

    report_lines = [
        "# Model Evaluation Report",
        "",
        "## Evaluation horizon",
        "- The most recent 24 hourly observations were held back as a test set.",
        "- All earlier observations were used for model fitting.",
        "",
        "## Actual metrics",
        "",
        f"- ARIMA MAE: {metrics['ARIMA']['MAE']:.6f}",
        f"- ARIMA RMSE: {metrics['ARIMA']['RMSE']:.6f}",
        f"- ARIMA MAPE: {metrics['ARIMA']['MAPE']:.6f}%",
        f"- Prophet MAE: {metrics['Prophet']['MAE']:.6f}",
        f"- Prophet RMSE: {metrics['Prophet']['RMSE']:.6f}",
        f"- Prophet MAPE: {metrics['Prophet']['MAPE']:.6f}%",
        "",
        "## Forecast sample",
        "",
        "| timestamp | actual_demand | arima_forecast | prophet_forecast |",
        "| --- | ---: | ---: | ---: |",
    ]
    for _, row in comparison.head(5).iterrows():
        report_lines.append(
            f"| {row['timestamp']} | {row['actual_demand']:.3f} | {row['arima_forecast']:.3f} | {row['prophet_forecast']:.3f} |"
        )
    report_lines.extend([
        "",
        "## Peak-demand summary",
        "",
        f"- Next-24h ARIMA peak: {next_24['arima_forecast'].max():.3f} kW",
        f"- Next-24h Prophet peak: {next_24['prophet_forecast'].max():.3f} kW",
    ])
    Path("reports").mkdir(exist_ok=True)
    Path("reports/model_evaluation.md").write_text("\n".join(report_lines), encoding="utf-8")

    print(metrics)


if __name__ == "__main__":
    main()
