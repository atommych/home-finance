"""Settings page - Profile and preferences."""

import streamlit as st

st.set_page_config(page_title="Configuracoes", page_icon=":gear:")
st.title(":gear: Configuracoes")

st.subheader("Perfil")
st.text_input("Nome", value="", placeholder="Seu nome")
st.selectbox("Moeda", options=["EUR", "BRL", "USD"], index=0)

st.divider()
st.subheader("Dados")

if st.button("Limpar todas as transacoes"):
    if "transactions" in st.session_state:
        del st.session_state.transactions
        st.success("Transacoes removidas.")
        st.rerun()

st.divider()
st.caption("Home Finance SaaS v0.1.0")
