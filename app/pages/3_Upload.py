"""Upload page - Parse bank statement PDFs."""

import streamlit as st

from app.components.file_uploader import render_file_uploader
from app.services.category_service import DEFAULT_CATEGORIES, apply_category_rules
from app.services.import_service import parse_uploaded_pdf, transactions_to_dataframe

DEFAULT_PATTERNS: dict[str, list[str]] = {
    "Alimentacao": ["mercadona", "continente", "pingo doce", "lidl", "aldi", "minipreco"],
    "Transporte": ["uber", "bolt", "cp ", "metro", "combustivel", "galp", "repsol", "bp "],
    "Lazer": ["netflix", "spotify", "cinema", "amazon prime", "hbo"],
    "Arrendamento": ["renda", "arrendamento", "aluguel"],
    "Saude": ["farmacia", "hospital", "clinica", "medic"],
    "Educacao": ["escola", "universidade", "curso", "livro"],
}

st.set_page_config(page_title="Upload", page_icon=":outbox_tray:")
st.title(":outbox_tray: Upload de Extratos")

uploaded_files, bank_name = render_file_uploader()

if uploaded_files:
    all_transactions = []
    progress = st.progress(0)

    for i, uploaded_file in enumerate(uploaded_files):
        try:
            pdf_bytes = uploaded_file.getvalue()
            transactions = parse_uploaded_pdf(pdf_bytes, bank_name)
            all_transactions.extend(transactions)
            st.success(f"{uploaded_file.name}: {len(transactions)} transacoes encontradas")
        except Exception as e:
            st.error(f"{uploaded_file.name}: Erro ao processar - {e}")
        progress.progress((i + 1) / len(uploaded_files))

    if all_transactions:
        df = transactions_to_dataframe(all_transactions)

        # Apply default category rules (until user manages their own)
        default_rules = [
            {"match_pattern": pattern, "category": cat}
            for cat in [c["name"] for c in DEFAULT_CATEGORIES]
            for pattern in DEFAULT_PATTERNS.get(cat, [])
        ]
        df = apply_category_rules(df, default_rules)

        # Store in session state for other pages
        st.session_state.transactions = df

        st.divider()
        st.subheader(f"Total: {len(df)} transacoes carregadas")
        st.dataframe(df, use_container_width=True, hide_index=True)
