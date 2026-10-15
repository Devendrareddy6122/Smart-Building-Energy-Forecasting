from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st


def prepare_history_chart(df: pd.DataFrame) -> px.line:
    if df.empty:
        return px.line(title="No data available")
    chart_df = df.sort_values("timestamp").copy()
    fig = px.line(chart_df, x="timestamp", y="active_power_kw", title="Hourly electricity consumption")
    return fig


def prepare_forecast_chart(history: pd.DataFrame, forecast: pd.DataFrame) -> px.line:
    if history.empty or forecast.empty:
        return px.line(title="No forecast data")
    forecast_column = "selected_forecast" if "selected_forecast" in forecast.columns else "arima_forecast"
    plot_df = pd.concat([
        history[["timestamp", "active_power_kw"]].rename(columns={"active_power_kw": "demand"}),
        forecast[["timestamp", forecast_column]].rename(columns={forecast_column: "demand"}),
    ], ignore_index=True)
    fig = px.line(plot_df, x="timestamp", y="demand", title="Demand and forecast overlay")
    return fig
