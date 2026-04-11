"""Reusable transaction table component."""

import pandas as pd
import streamlit as st


def render_transaction_table(df: pd.DataFrame) -> None:
    """Render a filterable transaction table."""
    if df.empty:
        st.info("Nenhuma transacao encontrada.")
        return

    if "category" in df.columns:
        categories = st.multiselect(
            "Filtrar por categoria",
            options=sorted(df["category"].dropna().unique()),
            default=sorted(df["category"].dropna().unique()),
        )
        df = df[df["category"].isin(categories)]

    st.dataframe(
        df[["date", "trx_type", "description", "amount", "balance", "category"]]
        if "category" in df.columns
        else df[["date", "trx_type", "description", "amount", "balance"]],
        use_container_width=True,
        hide_index=True,
    )
