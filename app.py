from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

from dashboard.charts import prepare_forecast_chart, prepare_history_chart
from dashboard.model_comparison import render_metrics_table
from dashboard.overview import render_overview
from forecasting.train import train_and_forecast
from storage.local_storage import LocalStorage


st.set_page_config(page_title="Smart Building Energy Forecasting", layout="wide")
st.title("Smart Building Energy Consumption Forecasting")


@st.cache_data
def load_data(file_mtime_ns: int, file_size: int) -> pd.DataFrame:
    del file_mtime_ns, file_size  # These arguments invalidate the cache when the pipeline refreshes the CSV.
    storage = LocalStorage(Path(__file__).resolve().parent / "data")
    path = storage.base_dir / "processed" / "hourly_consumption.csv"
    if not path.exists():
        return pd.DataFrame(columns=["timestamp", "active_power_kw"])
    df = pd.read_csv(path)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    return df.sort_values("timestamp").reset_index(drop=True)

data_path = Path(__file__).resolve().parent / "data" / "processed" / "hourly_consumption.csv"
if data_path.exists():
    data_stat = data_path.stat()
    history = load_data(data_stat.st_mtime_ns, data_stat.st_size)
else:
    history = pd.DataFrame(columns=["timestamp", "active_power_kw"])

if history.empty:
    st.warning("The system has no historical hourly data yet. Run the data pipeline to generate model inputs.")
    st.stop()

with st.sidebar:
    st.header("Controls")
    selected_start = st.date_input("Start date", value=pd.to_datetime(history["timestamp"].min()).date())
    selected_end = st.date_input("End date", value=pd.to_datetime(history["timestamp"].max()).date())
    alert_threshold = st.number_input("Peak-demand alert threshold (kW)", min_value=0.0, value=10.0, step=0.5)

filtered = history[(history["timestamp"].dt.date >= pd.to_datetime(selected_start).date()) & (history["timestamp"].dt.date <= pd.to_datetime(selected_end).date())]

st.subheader("Historical consumption")
st.plotly_chart(prepare_history_chart(filtered), use_container_width=True)

@st.cache_data(show_spinner="Fitting and selecting a forecast model...")
def build_forecast(data: pd.DataFrame) -> dict:
    return train_and_forecast(data, horizon=24)


if filtered.empty:
    st.warning("No hourly readings fall within the selected date range. Choose a range that includes data.")
    st.stop()

model_results = build_forecast(filtered)
forecast = model_results["combined"]
# Keep the open result files in sync with the date range currently driving the dashboard.
output_dir = data_path.parent
forecast.to_csv(output_dir / "next_24h_forecast.csv", index=False)

comparison = model_results["validation_actual"].copy()
for candidate, values in model_results["validation_predictions"].items():
    comparison[f"{candidate}_forecast"] = values.to_numpy()
comparison.to_csv(output_dir / "forecast_comparison.csv", index=False)

selected_model = model_results["selected_model"].title()
render_overview(filtered, model_name=selected_model)

st.subheader("Next 24-hour forecast")
st.plotly_chart(prepare_forecast_chart(filtered, forecast), use_container_width=True)

if forecast["arima_forecast"].max() > alert_threshold:
    st.warning("A high-demand alert is active based on the current forecast threshold.")

metric_dict = {f"{name.title()} validation MAE (kW)": score for name, score in model_results["validation_mae"].items()}
render_metrics_table(metric_dict)
st.caption(f"Selected model by rolling chronological holdout MAE: **{selected_model}**")
