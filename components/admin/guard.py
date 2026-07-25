"""
Simple role-based access guard for admin-only pages.
"""
from __future__ import annotations

import streamlit as st


def require_admin() -> bool:
    """Return True if the current session belongs to an admin; otherwise render a denial message."""
    if st.session_state.get("role") != "admin":
        st.error("🚫 You do not have permission to access this page. Administrator access required.")
        return False
    return True
