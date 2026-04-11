"""Transactions page - Browse and filter transactions."""

import streamlit as st

from app.components.transaction_table import render_transaction_table

st.set_page_config(page_title="Transacoes", page_icon=":money_with_wings:")
st.title(":money_with_wings: Transacoes")

if "transactions" not in st.session_state or st.session_state.transactions.empty:
    st.info("Nenhuma transacao carregada. Va ate a pagina de Upload primeiro.")
    st.stop()

df = st.session_state.transactions

# Date range filter
col1, col2 = st.columns(2)
with col1:
    min_date = df["date"].min()
    start_date = st.date_input("De", value=min_date, min_value=min_date, max_value=df["date"].max())
with col2:
    max_date = df["date"].max()
    end_date = st.date_input("Ate", value=max_date, min_value=min_date, max_value=max_date)

filtered = df[(df["date"] >= str(start_date)) & (df["date"] <= str(end_date))]

st.caption(f"{len(filtered)} transacoes encontradas")
render_transaction_table(filtered)

# Export
if not filtered.empty:
    csv = filtered.to_csv(index=False).encode("utf-8")
    st.download_button("Exportar CSV", csv, "transacoes.csv", "text/csv")
