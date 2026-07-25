"""
Login and Registration page UI. Delegates all business logic to auth_service.
"""
from __future__ import annotations

import streamlit as st

from components.ui import notify_error, notify_success
from config.config import settings
from services.auth_service import login_user, register_user


def _set_authenticated_session(result) -> None:
    st.session_state.authenticated = True
    st.session_state.user_id = result.user_id
    st.session_state.full_name = result.full_name
    st.session_state.email = result.email
    st.session_state.role = result.role


def render_login() -> None:
    st.markdown(
        f"""<div class="airs-header"><h1>Welcome Back</h1>
        <p class="airs-header-subtitle">Log in to {settings.app_name}</p></div>""",
        unsafe_allow_html=True,
    )

    _, mid, _ = st.columns([1, 2, 1])
    with mid:
        with st.form("login_form", clear_on_submit=False):
            email = st.text_input("Email", placeholder="you@example.com")
            password = st.text_input("Password", type="password", placeholder="••••••••")
            submitted = st.form_submit_button("Log In", use_container_width=True)

        if submitted:
            result = login_user(email, password)
            if result.success:
                _set_authenticated_session(result)
                notify_success(result.message)
                st.rerun()
            else:
                notify_error(result.message)

        st.markdown("<div style='text-align:center; margin-top:14px;'>Don't have an account?</div>", unsafe_allow_html=True)
        if st.button("Create one here", use_container_width=True):
            st.session_state.auth_view = "register"
            st.rerun()
        if st.button("← Back to home", use_container_width=True):
            st.session_state.auth_view = "landing"
            st.rerun()


def render_register() -> None:
    st.markdown(
        f"""<div class="airs-header"><h1>Create Your Account</h1>
        <p class="airs-header-subtitle">Join {settings.app_name} in a few seconds</p></div>""",
        unsafe_allow_html=True,
    )

    _, mid, _ = st.columns([1, 2, 1])
    with mid:
        with st.form("register_form", clear_on_submit=False):
            full_name = st.text_input("Full Name", placeholder="Jane Doe")
            email = st.text_input("Email", placeholder="you@example.com")
            password = st.text_input("Password", type="password", placeholder="At least 8 characters")
            confirm_password = st.text_input("Confirm Password", type="password")
            submitted = st.form_submit_button("Create Account", use_container_width=True)

        if submitted:
            result = register_user(full_name, email, password, confirm_password)
            if result.success:
                notify_success(result.message)
                st.session_state.auth_view = "login"
                st.rerun()
            else:
                notify_error(result.message)

        st.markdown("<div style='text-align:center; margin-top:14px;'>Already have an account?</div>", unsafe_allow_html=True)
        if st.button("Log in here", use_container_width=True):
            st.session_state.auth_view = "login"
            st.rerun()
        if st.button("← Back to home", key="back_home_register", use_container_width=True):
            st.session_state.auth_view = "landing"
            st.rerun()
