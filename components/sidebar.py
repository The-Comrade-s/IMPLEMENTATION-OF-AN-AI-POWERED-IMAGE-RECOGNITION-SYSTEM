"""
Sidebar navigation, rendered only for authenticated users. Admin-only items
(AIRS-004) are appended dynamically for users with the 'admin' role, without
altering the base menu built in AIRS-001.
"""
from __future__ import annotations

import streamlit as st
from streamlit_option_menu import option_menu

from config.config import settings

USER_OPTIONS = ["Dashboard", "Image Recognition", "History", "Analytics", "Settings", "Logout"]
USER_ICONS = ["speedometer2", "camera", "clock-history", "bar-chart-line", "gear", "box-arrow-right"]

ADMIN_OPTIONS = [
    "Admin Dashboard", "User Management", "Image Management", "AI Management",
    "System Logs", "Database Management", "System Settings",
]
ADMIN_ICONS = ["shield-lock", "people", "images", "cpu", "journal-text", "hdd-stack", "sliders"]


def render_sidebar() -> str:
    """Render the sidebar and return the selected page key."""
    with st.sidebar:
        st.markdown(
            f"""
            <div class="airs-sidebar-brand">
                <div class="airs-sidebar-icon">{settings.app_icon}</div>
                <div class="airs-sidebar-title">AIRS</div>
                <div class="airs-sidebar-subtitle">AI Image Recognition</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            f"""
            <div class="airs-sidebar-user">
                <div class="airs-sidebar-user-name">👤 {st.session_state.get('full_name', '')}</div>
                <div class="airs-sidebar-user-role">{st.session_state.get('role', 'user').upper()}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        is_admin = st.session_state.get("role") == "admin"
        options = USER_OPTIONS[:-1] + (ADMIN_OPTIONS if is_admin else []) + [USER_OPTIONS[-1]]
        icons = USER_ICONS[:-1] + (ADMIN_ICONS if is_admin else []) + [USER_ICONS[-1]]

        selected = option_menu(
            menu_title=None,
            options=options,
            icons=icons,
            default_index=0,
            styles={
                "container": {"padding": "0", "background-color": "transparent"},
                "icon": {"font-size": "16px"},
                "nav-link": {
                    "font-size": "14px",
                    "text-align": "left",
                    "margin": "3px 0",
                    "border-radius": "10px",
                },
                "nav-link-selected": {"background-color": "#2952e3"},
            },
        )
        return selected
