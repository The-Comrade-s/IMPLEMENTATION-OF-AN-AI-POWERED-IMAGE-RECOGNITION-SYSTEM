"""
Admin System Logs: search, filter, and export the audit trail (AIRS-004).
"""
from __future__ import annotations

import pandas as pd
import streamlit as st

from components.admin.guard import require_admin
from components.ui import empty_state, page_header, section_card_end, section_card_start
from services.audit_service import get_recent_logs


def render_system_logs() -> None:
    if not require_admin():
        return

    page_header("System Logs", "Audit trail of security-relevant and administrative actions.")

    col1, col2 = st.columns(2)
    with col1:
        level = st.selectbox("Level", ["All", "INFO", "WARNING", "ERROR"])
    with col2:
        action_filter = st.text_input("Filter by action contains", "")

    logs = get_recent_logs(limit=300, level=None if level == "All" else level, action_contains=action_filter or None)

    if not logs:
        empty_state("📜", "No logs found", "Logged actions will appear here as the system is used.")
        return

    section_card_start(f"{len(logs)} log entries")
    df = pd.DataFrame(logs)
    st.dataframe(df, use_container_width=True, hide_index=True)
    st.download_button("⬇️ Export Logs (CSV)", df.to_csv(index=False).encode("utf-8"), file_name="system_logs.csv", mime="text/csv")
    section_card_end()
