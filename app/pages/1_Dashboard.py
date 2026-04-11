"""Dashboard page - Summary stats and charts."""

import streamlit as st

from app.components.category_chart import render_expenses_by_category_chart
from app.services.analytics_service import monthly_expenses_by_category, summary_stats

st.set_page_config(page_title="Dashboard", page_icon=":chart_with_upwards_trend:")
st.title(":chart_with_upwards_trend: Dashboard")

if "transactions" not in st.session_state or st.session_state.transactions.empty:
    st.info("Nenhuma transacao carregada. Va ate a pagina de Upload primeiro.")
    st.stop()

df = st.session_state.transactions

# Summary metrics
stats = summary_stats(df)
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Despesas", f"EUR {stats['total_expenses']:,.2f}")
col2.metric("Transacoes", stats["transaction_count"])
col3.metric("Top Categoria", stats["top_category"])
avg = stats["total_expenses"] / max(stats["transaction_count"], 1)
col4.metric("Media/Transacao", f"EUR {avg:,.2f}")

st.divider()

# Monthly chart
st.subheader("Despesas por Categoria e Mes")
chart_data = monthly_expenses_by_category(df)
render_expenses_by_category_chart(chart_data)
