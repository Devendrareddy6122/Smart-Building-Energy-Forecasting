from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st


def render_metrics_table(metrics: dict) -> None:
    st.subheader("Model comparison")
    if not metrics:
        st.info("No evaluation metrics are available yet.")
        return
    table = pd.DataFrame.from_dict(metrics, orient="index", columns=["value"])
    st.dataframe(table)


def render_actual_vs_predicted(actual: pd.Series, predicted: pd.Series) -> None:
    comparison = pd.DataFrame({"actual": actual, "predicted": predicted})
    fig = px.line(comparison, title="Actual versus predicted demand")
    st.plotly_chart(fig, use_container_width=True)
