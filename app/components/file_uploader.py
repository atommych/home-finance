"""File upload component for bank statements."""

import streamlit as st

from app.parsers import PARSERS


def render_file_uploader() -> tuple[list, str]:
    """Render file upload widget with bank selection.

    Returns:
        Tuple of (uploaded_files, selected_bank_name).
    """
    col1, col2 = st.columns([3, 1])

    with col2:
        bank_name = st.selectbox(
            "Banco",
            options=list(PARSERS.keys()),
            format_func=lambda x: x.upper(),
        )

    with col1:
        uploaded_files = st.file_uploader(
            "Selecione seus extratos em PDF",
            accept_multiple_files=True,
            type=["pdf"],
        )

    return uploaded_files or [], bank_name
