"""Categories page - Manage categories and auto-match rules."""

import streamlit as st

from app.services.category_service import DEFAULT_CATEGORIES

st.set_page_config(page_title="Categorias", page_icon=":label:")
st.title(":label: Categorias")

# Initialize categories in session state
if "categories" not in st.session_state:
    st.session_state.categories = DEFAULT_CATEGORIES.copy()

if "category_rules" not in st.session_state:
    st.session_state.category_rules = []

# Display current categories
st.subheader("Categorias Atuais")
for i, cat in enumerate(st.session_state.categories):
    col1, col2, col3 = st.columns([1, 4, 1])
    col1.color_picker("Cor", cat["color"], key=f"color_{i}", label_visibility="collapsed")
    col2.text(cat["name"])
    if col3.button("Remover", key=f"del_{i}"):
        st.session_state.categories.pop(i)
        st.rerun()

# Add new category
st.divider()
st.subheader("Adicionar Categoria")
with st.form("new_category"):
    col1, col2 = st.columns([3, 1])
    new_name = col1.text_input("Nome da categoria")
    new_color = col2.color_picker("Cor", "#808080")
    if st.form_submit_button("Adicionar"):
        if new_name:
            st.session_state.categories.append({"name": new_name, "color": new_color})
            st.success(f"Categoria '{new_name}' adicionada!")
            st.rerun()

# Category rules
st.divider()
st.subheader("Regras de Classificacao")
st.caption("Adicione padroes para classificar transacoes automaticamente.")

with st.form("new_rule"):
    col1, col2 = st.columns(2)
    pattern = col1.text_input("Padrao (texto da descricao)")
    category = col2.selectbox(
        "Categoria",
        options=[c["name"] for c in st.session_state.categories],
    )
    if st.form_submit_button("Adicionar Regra"):
        if pattern:
            st.session_state.category_rules.append({"match_pattern": pattern, "category": category})
            st.success(f"Regra adicionada: '{pattern}' -> {category}")
            st.rerun()

# Display current rules
if st.session_state.category_rules:
    st.dataframe(
        st.session_state.category_rules,
        use_container_width=True,
        hide_index=True,
    )
