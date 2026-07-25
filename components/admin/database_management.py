"""
Admin Database Management: backup, restore, and integrity checks (AIRS-004).
"""
from __future__ import annotations

import streamlit as st

from components.admin.guard import require_admin
from components.ui import empty_state, notify_error, notify_success, page_header, section_card_end, section_card_start
from services.admin_service import backup_database, check_database_integrity, get_system_stats, list_backups, restore_database


def render_database_management() -> None:
    if not require_admin():
        return

    page_header("Database Management", "Backup, restore, and monitor the application database.")

    stats = get_system_stats()
    section_card_start("Database Overview")
    st.markdown(f"**Size:** {stats['database_size_mb']:.2f} MB")
    st.markdown(f"**Total users:** {stats['total_users']}")
    st.markdown(f"**Total images:** {stats['total_images']}")
    section_card_end()

    section_card_start("Backup & Restore")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("💾 Create Backup Now", use_container_width=True):
            ok, message, path = backup_database(st.session_state["user_id"])
            notify_success(message) if ok else notify_error(message)
    with col2:
        if st.button("🔍 Run Integrity Check", use_container_width=True):
            ok, result = check_database_integrity()
            notify_success(f"Integrity check passed: {result}") if ok else notify_error(f"Integrity issue: {result}")

    backups = list_backups()
    if not backups:
        empty_state("🗄️", "No backups yet", "Create your first backup above.")
    else:
        st.markdown("**Available backups**")
        for backup in backups:
            col_a, col_b, col_c = st.columns([3, 1, 1])
            with col_a:
                st.markdown(f"`{backup['name']}` — {backup['created'].strftime('%Y-%m-%d %H:%M')}")
            with col_b:
                st.caption(f"{backup['size_mb']:.2f} MB")
            with col_c:
                if st.button("Restore", key=f"restore_{backup['name']}"):
                    ok, message = restore_database(backup["path"], st.session_state["user_id"])
                    notify_success(message) if ok else notify_error(message)
    section_card_end()

    st.caption("Automatic scheduled backups can be configured by running this page's backup action from a cron job or task scheduler outside of Streamlit, since Streamlit itself has no built-in scheduler.")
