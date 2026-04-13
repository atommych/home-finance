"""Supabase client setup."""

import streamlit as st

from app.config import settings
from supabase import Client, create_client


@st.cache_resource
def get_supabase_client() -> Client:
    """Create and cache a Supabase client.

    Uses Streamlit's cache_resource so the client is shared across reruns.
    """
    if not settings.supabase_url or not settings.supabase_key:
        raise RuntimeError(
            "SUPABASE_URL and SUPABASE_KEY must be set. "
            "Copy .env.example to .env and fill in your Supabase credentials."
        )
    return create_client(settings.supabase_url, settings.supabase_key)


def get_authenticated_client() -> Client | None:
    """Get a Supabase client with the current user's session.

    Returns None if no user is logged in.
    """
    if "supabase_session" not in st.session_state:
        return None

    client = get_supabase_client()
    session = st.session_state.supabase_session
    client.auth.set_session(session.access_token, session.refresh_token)
    return client
