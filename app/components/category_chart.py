"""Reusable chart components for the dashboard."""

import altair as alt
import pandas as pd
import streamlit as st


def render_expenses_by_category_chart(df: pd.DataFrame) -> None:
    """Render a line chart of monthly expenses grouped by category."""
    if df.empty:
        st.info("Nenhum dado para exibir no grafico.")
        return

    chart = (
        alt.Chart(df)
        .mark_line(point=True)
        .encode(
            x=alt.X("month:O", title="Mes"),
            y=alt.Y("amount:Q", title="Despesas (EUR)"),
            color=alt.Color(
                "category:N",
                title="Categoria",
                scale=alt.Scale(scheme="category10"),
            ),
            tooltip=["month", "category", "amount"],
        )
        .properties(height=400)
    )
    st.altair_chart(chart, use_container_width=True)
