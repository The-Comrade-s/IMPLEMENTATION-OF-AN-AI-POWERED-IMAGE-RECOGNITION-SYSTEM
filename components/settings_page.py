"""
Settings page: profile (view/edit/avatar), password, preferences, reports,
notifications, and about. Extends AIRS-001's settings page (password change
logic is unchanged) with AIRS-003 features.
"""
from __future__ import annotations

from PIL import Image as PILImage
import streamlit as st

from ai.yolo_service import AVAILABLE_MODELS
from components.ui import notify_error, notify_success, page_header, section_card_end, section_card_start
from config.config import settings
from services.auth_service import change_password
from services.profile_service import update_avatar, update_full_name
from services.report_service import generate_csv_report, generate_excel_report, generate_pdf_report
from services.settings_service import get_or_create_settings, mark_all_read, get_notifications, reset_settings, update_settings


def render_settings() -> None:
    page_header("Settings", "Manage your profile, security, preferences, and reports.")

    tabs = st.tabs(["👤 Profile", "🔒 Password", "🎨 Preferences", "📄 Reports", "🔔 Notifications", "ℹ️ About"])

    with tabs[0]:
        _render_profile_tab()
    with tabs[1]:
        _render_password_tab()
    with tabs[2]:
        _render_preferences_tab()
    with tabs[3]:
        _render_reports_tab()
    with tabs[4]:
        _render_notifications_tab()
    with tabs[5]:
        _render_about_tab()


def _render_profile_tab() -> None:
    section_card_start("Profile Information")
    col1, col2 = st.columns([1, 2])
    with col1:
        st.text_input("Email", value=st.session_state.get("email", ""), disabled=True)
        st.text_input("Role", value=st.session_state.get("role", "user").capitalize(), disabled=True)
    with col2:
        with st.form("update_name_form"):
            new_name = st.text_input("Full Name", value=st.session_state.get("full_name", ""))
            if st.form_submit_button("Update Name"):
                ok, message = update_full_name(st.session_state["user_id"], new_name)
                if ok:
                    st.session_state["full_name"] = new_name.strip()
                    notify_success(message)
                else:
                    notify_error(message)
    section_card_end()

    section_card_start("Profile Picture")
    avatar_file = st.file_uploader("Upload a new profile picture", type=["jpg", "jpeg", "png"], key="avatar_upload")
    if avatar_file is not None and st.button("Save Profile Picture"):
        try:
            image = PILImage.open(avatar_file)
            ok, message = update_avatar(st.session_state["user_id"], image)
            notify_success(message) if ok else notify_error(message)
        except Exception:
            notify_error("Could not read that image file.")
    section_card_end()


def _render_password_tab() -> None:
    section_card_start("Change Password")
    with st.form("change_password_form"):
        current_password = st.text_input("Current Password", type="password")
        new_password = st.text_input("New Password", type="password")
        confirm_password = st.text_input("Confirm New Password", type="password")
        submitted = st.form_submit_button("Update Password")

    if submitted:
        result = change_password(st.session_state["user_id"], current_password, new_password, confirm_password)
        notify_success(result.message) if result.success else notify_error(result.message)
    section_card_end()


def _render_preferences_tab() -> None:
    user_id = st.session_state["user_id"]
    prefs = get_or_create_settings(user_id)

    section_card_start("Detection Preferences")
    model_names = list(AVAILABLE_MODELS.values())
    model_labels = list(AVAILABLE_MODELS.keys())
    current_index = model_names.index(prefs["default_model"]) if prefs["default_model"] in model_names else 0

    col1, col2 = st.columns(2)
    with col1:
        theme = st.selectbox("Theme", ["light", "dark (coming soon)"], index=0 if prefs["theme"] == "light" else 1)
        default_model_label = st.selectbox("Default model", model_labels, index=current_index)
    with col2:
        default_confidence = st.slider("Default confidence threshold", 0.05, 0.95, float(prefs["default_confidence"]), 0.05)
        export_format = st.selectbox("Preferred export format", ["csv", "excel", "pdf"], index=["csv", "excel", "pdf"].index(prefs["export_format"]))

    notifications_enabled = st.toggle("Enable notifications", value=prefs["notifications_enabled"])

    col_save, col_reset = st.columns(2)
    with col_save:
        if st.button("💾 Save Preferences", use_container_width=True):
            update_settings(
                user_id,
                theme="light",
                default_model=AVAILABLE_MODELS[default_model_label],
                default_confidence=default_confidence,
                export_format=export_format,
                notifications_enabled=notifications_enabled,
            )
            notify_success("Preferences saved.")
    with col_reset:
        if st.button("↺ Reset to Defaults", use_container_width=True):
            reset_settings(user_id)
            notify_success("Preferences reset to defaults.")
            st.rerun()
    section_card_end()


def _render_reports_tab() -> None:
    user_id = st.session_state["user_id"]
    section_card_start("Export Detection Reports")
    st.caption("Reports include your image, object, confidence, and timing history.")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.download_button("⬇️ CSV Report", generate_csv_report(user_id), file_name="detection_report.csv", mime="text/csv", use_container_width=True)
    with col2:
        st.download_button(
            "⬇️ Excel Report", generate_excel_report(user_id), file_name="detection_report.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True,
        )
    with col3:
        if st.button("⬇️ Generate PDF Report", use_container_width=True):
            try:
                pdf_bytes = generate_pdf_report(user_id)
                st.download_button("Download PDF", pdf_bytes, file_name="detection_report.pdf", mime="application/pdf", use_container_width=True)
            except Exception as exc:
                notify_error(f"Could not generate PDF report: {exc}")
    section_card_end()


def _render_notifications_tab() -> None:
    user_id = st.session_state["user_id"]
    section_card_start("Notifications")
    notifications = get_notifications(user_id)
    if not notifications:
        st.caption("No notifications yet.")
    else:
        if st.button("Mark all as read"):
            mark_all_read(user_id)
            st.rerun()
        for note in notifications:
            icon = {"success": "✅", "error": "⚠️", "warning": "🔔", "info": "ℹ️"}.get(note["category"], "ℹ️")
            read_marker = "" if note["is_read"] else " **(new)**"
            st.markdown(f"{icon} {note['message']}{read_marker}  \n<span style='font-size:12px;color:#6b7280;'>{note['created_at'].strftime('%Y-%m-%d %H:%M')}</span>", unsafe_allow_html=True)
    section_card_end()


def _render_about_tab() -> None:
    section_card_start("About This System")
    st.markdown(
        f"""
        **{settings.app_name}**

        A final-year Computer Science project delivering AI-powered object
        detection through a professional, secure web application.

        - **Framework:** Streamlit
        - **AI Engine:** Ultralytics YOLOv11
        - **Database:** SQLite via SQLAlchemy
        - **Security:** bcrypt password hashing, session-based auth, role-based access control
        """
    )
    section_card_end()
