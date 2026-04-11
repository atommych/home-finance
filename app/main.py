"""Home Finance SaaS - Main entry point."""

import streamlit as st

st.set_page_config(
    page_title="Home Finance",
    page_icon=":bar_chart:",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title(":bar_chart: Home Finance")
st.write(
    """
    Analise seus extratos bancarios de forma simples e rapida.
    Faca upload dos seus extratos em PDF e visualize seus gastos por categoria.
    """
)

st.divider()

st.markdown(
    """
    ### Como usar

    1. **Upload** - Va ate a pagina de Upload e selecione seus extratos em PDF
    2. **Transacoes** - Visualize e filtre todas as suas transacoes
    3. **Dashboard** - Acompanhe seus gastos por categoria e mes
    4. **Categorias** - Gerencie suas categorias e regras de classificacao

    ---
    *Selecione uma pagina no menu lateral para comecar.*
    """
)
