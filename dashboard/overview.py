from __future__ import annotations

import pandas as pd
import streamlit as st

from forecasting.predict import compute_peak_summary


def render_overview(df: pd.DataFrame, model_name: str = "ARIMA") -> None:
    if df.empty:
        st.warning("No recent demand data is available yet.")
        return

    metric_summary = compute_peak_summary(df.tail(48))
    st.subheader("Overview")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Meters / Buildings", len(df["building_id"].unique()) if "building_id" in df.columns else 1)
    with col2:
        st.metric("Latest Demand", f"{df['active_power_kw'].iloc[-1]:.2f} kW")
    with col3:
        st.metric("Predicted Peak", f"{metric_summary['max_demand']:.2f} kW")
    with col4:
        st.metric("Selected Model", model_name)

    st.caption(f"Expected peak time: {metric_summary['peak_timestamp']}")
