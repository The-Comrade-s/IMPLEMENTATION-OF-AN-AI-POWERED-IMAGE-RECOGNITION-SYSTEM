"""
Admin System Settings: application-wide configuration (AIRS-004).
Stored in the same JSON config file as AI settings, under a separate key,
to avoid adding a single-row DB table for a handful of global values.
"""
from __future__ import annotations

import json

import streamlit as st

from components.admin.guard import require_admin
from components.ui import notify_success, page_header, section_card_end, section_card_start
from config.config import settings
from services.audit_service import record_event

_APP_CONFIG_PATH = settings.database_path.parent / "app_config.json"
_DEFAULTS = {
    "application_name": settings.app_name,
    "max_upload_mb": 15,
    "allowed_file_types": "jpg,jpeg,png,bmp,webp",
    "session_timeout_minutes": settings.session_timeout_minutes,
    "logging_level": settings.log_level,
}


def _read_app_config() -> dict:
    if not _APP_CONFIG_PATH.exists():
        _APP_CONFIG_PATH.write_text(json.dumps(_DEFAULTS, indent=2))
        return dict(_DEFAULTS)
    try:
        return {**_DEFAULTS, **json.loads(_APP_CONFIG_PATH.read_text())}
    except Exception:
        return dict(_DEFAULTS)


def _write_app_config(data: dict) -> None:
    _APP_CONFIG_PATH.write_text(json.dumps(data, indent=2))


def render_system_settings() -> None:
    if not require_admin():
        return

    page_header("System Settings", "Application-wide configuration.")

    config = _read_app_config()

    section_card_start("General")
    application_name = st.text_input("Application Name", value=config["application_name"])
    max_upload_mb = st.number_input("Maximum Upload Size (MB)", min_value=1, max_value=100, value=int(config["max_upload_mb"]))
    allowed_types = st.text_input("Allowed File Types (comma-separated)", value=config["allowed_file_types"])
    session_timeout = st.number_input("Session Timeout (minutes)", min_value=5, max_value=1440, value=int(config["session_timeout_minutes"]))
    logging_level = st.selectbox("Logging Level", ["DEBUG", "INFO", "WARNING", "ERROR"], index=["DEBUG", "INFO", "WARNING", "ERROR"].index(config["logging_level"]))

    if st.button("💾 Save System Settings"):
        new_config = {
            "application_name": application_name,
            "max_upload_mb": max_upload_mb,
            "allowed_file_types": allowed_types,
            "session_timeout_minutes": session_timeout,
            "logging_level": logging_level,
        }
        _write_app_config(new_config)
        record_event("system_settings_updated", str(new_config), user_id=st.session_state["user_id"])
        notify_success("System settings saved. Some changes (e.g. logging level) apply after a restart.")
    section_card_end()
