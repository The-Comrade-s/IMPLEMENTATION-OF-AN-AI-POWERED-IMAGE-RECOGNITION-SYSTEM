"""
AI-Powered Image Recognition System — main entry point.

Run with:
    streamlit run app.py

Phases implemented:
  AIRS-001 — Foundation, auth, session management, landing page, dashboard, settings
  AIRS-002 — YOLOv11 detection engine, upload/preview/results, detection history
  AIRS-003 — Real dashboard/analytics data, reports, profile, preferences, notifications
  AIRS-004 — Admin panel: users, images, AI management, system logs, database, settings
  AIRS-005 — Hardening, testing, documentation, deployment configuration
"""
from __future__ import annotations

import streamlit as st

from components.admin.admin_dashboard import render_admin_dashboard
from components.admin.ai_management import render_ai_management
from components.admin.database_management import render_database_management
from components.admin.image_management import render_image_management
from components.admin.system_logs import render_system_logs
from components.admin.system_settings import render_system_settings
from components.admin.user_management import render_user_management
from components.analytics_page import render_analytics
from components.auth_pages import render_login, render_register
from components.dashboard_page import render_dashboard
from components.history_page import render_history
from components.landing import render_landing
from components.recognition_page import render_image_recognition
from components.settings_page import render_settings
from components.sidebar import render_sidebar
from components.ui import load_css
from config.config import settings
from database.db import init_db
from services.audit_service import record_event
from utils.logger import get_logger

logger = get_logger(__name__)


def configure_page() -> None:
    # The sidebar holds ALL post-login navigation (Dashboard, Image Recognition,
    # History, Analytics, Settings, Logout, Admin pages). If it starts collapsed
    # after login, desktop users only see a tiny ">" arrow with no obvious way
    # to reach any feature. "auto" solves that on desktop (it expands
    # automatically on wide viewports) while still letting mobile use its
    # normal, working hamburger-toggle behavior instead of a forced full-screen
    # overlay, which is what "expanded" was doing on narrow screens.
    is_authenticated = st.session_state.get("authenticated", False)
    st.set_page_config(
        page_title=settings.app_name,
        page_icon=settings.app_icon,
        layout="wide",
        initial_sidebar_state="auto" if is_authenticated else "collapsed",
    )
    load_css(settings.css_path)


def init_session_state() -> None:
    defaults = {
        "authenticated": False,
        "user_id": None,
        "full_name": None,
        "email": None,
        "role": None,
        "auth_view": "landing",  # landing | login | register
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


ROUTES = {
    "Dashboard": render_dashboard,
    "Image Recognition": render_image_recognition,
    "History": render_history,
    "Analytics": render_analytics,
    "Settings": render_settings,
    "Admin Dashboard": render_admin_dashboard,
    "User Management": render_user_management,
    "Image Management": render_image_management,
    "AI Management": render_ai_management,
    "System Logs": render_system_logs,
    "Database Management": render_database_management,
    "System Settings": render_system_settings,
}


def render_authenticated_app() -> None:
    selected = render_sidebar()

    if selected == "Logout":
        record_event("user_logout", user_id=st.session_state.get("user_id"))
        for key in ("authenticated", "user_id", "full_name", "email", "role"):
            st.session_state[key] = False if key == "authenticated" else None
        st.session_state.auth_view = "landing"
        st.rerun()
        return

    page_fn = ROUTES.get(selected)
    if page_fn is None:
        st.error("Unknown page. Please choose an option from the sidebar.")
        return

    try:
        page_fn()
    except Exception:
        logger.exception("Unhandled error while rendering page: %s", selected)
        st.error("Something went wrong loading this page. The issue has been logged.")


def render_public_app() -> None:
    view = st.session_state.auth_view
    if view == "login":
        render_login()
    elif view == "register":
        render_register()
    else:
        render_landing()


def main() -> None:
    init_session_state()
    configure_page()

    try:
        init_db()
    except Exception:
        st.error("A database error occurred while starting the application. Please check the logs.")
        st.stop()

    if st.session_state.authenticated:
        render_authenticated_app()
    else:
        render_public_app()


if __name__ == "__main__":
    main()
