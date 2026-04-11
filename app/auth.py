"""Supabase Auth helpers for Streamlit."""

import streamlit as st
from gotrue.errors import AuthApiError

from app.database import get_supabase_client


def require_auth() -> dict:
    """Check if user is authenticated. Show login form if not.

    Returns the user dict if authenticated, calls st.stop() otherwise.
    """
    if "user" in st.session_state and st.session_state.user:
        return st.session_state.user

    st.warning("Voce precisa fazer login para acessar esta pagina.")
    render_auth_form()
    st.stop()


def render_auth_form() -> None:
    """Render login/signup tabs."""
    tab_login, tab_signup = st.tabs(["Login", "Criar Conta"])

    with tab_login:
        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input("Senha", type="password")
            submitted = st.form_submit_button("Entrar", use_container_width=True)

            if submitted and email and password:
                _handle_login(email, password)

    with tab_signup:
        with st.form("signup_form"):
            email = st.text_input("Email", key="signup_email")
            password = st.text_input("Senha", type="password", key="signup_password")
            password_confirm = st.text_input(
                "Confirmar Senha", type="password", key="signup_confirm"
            )
            submitted = st.form_submit_button("Criar Conta", use_container_width=True)

            if submitted:
                if password != password_confirm:
                    st.error("As senhas nao coincidem.")
                elif email and password:
                    _handle_signup(email, password)


def _handle_login(email: str, password: str) -> None:
    """Process login attempt."""
    try:
        client = get_supabase_client()
        response = client.auth.sign_in_with_password({"email": email, "password": password})
        st.session_state.user = {
            "id": response.user.id,
            "email": response.user.email,
        }
        st.session_state.supabase_session = response.session
        st.success("Login realizado com sucesso!")
        st.rerun()
    except AuthApiError as e:
        st.error(f"Erro no login: {e.message}")


def _handle_signup(email: str, password: str) -> None:
    """Process signup attempt."""
    try:
        client = get_supabase_client()
        response = client.auth.sign_up({"email": email, "password": password})
        if response.user:
            st.success("Conta criada! Verifique seu email para confirmar.")
        else:
            st.error("Erro ao criar conta.")
    except AuthApiError as e:
        st.error(f"Erro no cadastro: {e.message}")


def logout() -> None:
    """Log out the current user."""
    try:
        client = get_supabase_client()
        client.auth.sign_out()
    except Exception:
        pass
    st.session_state.pop("user", None)
    st.session_state.pop("supabase_session", None)
    st.rerun()


def get_current_user_id() -> str | None:
    """Get the current user's ID, or None if not logged in."""
    user = st.session_state.get("user")
    return user["id"] if user else None
