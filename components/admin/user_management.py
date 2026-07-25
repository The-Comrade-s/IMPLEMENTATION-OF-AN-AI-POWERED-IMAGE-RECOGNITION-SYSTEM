"""
Admin User Management: view, search, activate/deactivate, promote/demote,
reset password, and delete users (AIRS-004).
"""
from __future__ import annotations

import secrets
import string

import streamlit as st

from components.admin.guard import require_admin
from components.ui import empty_state, notify_error, notify_success, page_header, section_card_end, section_card_start
from services.admin_service import delete_user, list_users, reset_user_password, set_user_active, set_user_role
from services.auth_service import hash_password_for_admin


def render_user_management() -> None:
    if not require_admin():
        return

    page_header("User Management", "View and manage every registered account.")

    search = st.text_input("🔍 Search by name or email", "")
    users = list_users(search=search)

    if not users:
        empty_state("👥", "No users found", "Try a different search term.")
        return

    st.caption(f"{len(users)} user(s) found")
    admin_id = st.session_state["user_id"]

    for user in users:
        section_card_start()
        col1, col2, col3, col4 = st.columns([3, 1, 1, 2])
        with col1:
            st.markdown(f"**{user['full_name']}**  \n{user['email']}")
            st.caption(f"Joined {user['created_at'].strftime('%Y-%m-%d')}"
                       + (f" · Last login {user['last_login'].strftime('%Y-%m-%d %H:%M')}" if user["last_login"] else ""))
        with col2:
            st.markdown("🟢 Active" if user["is_active"] else "🔴 Inactive")
        with col3:
            st.markdown(f"**{user['role'].capitalize()}**")
        with col4:
            b1, b2, b3, b4 = st.columns(4)
            if user["id"] == admin_id:
                st.caption("This is you")
            else:
                with b1:
                    label = "Deactivate" if user["is_active"] else "Activate"
                    if st.button(label, key=f"toggle_{user['id']}"):
                        ok, msg = set_user_active(user["id"], not user["is_active"], admin_id)
                        notify_success(msg) if ok else notify_error(msg)
                        st.rerun()
                with b2:
                    new_role = "user" if user["role"] == "admin" else "admin"
                    if st.button(f"Make {new_role}", key=f"role_{user['id']}"):
                        ok, msg = set_user_role(user["id"], new_role, admin_id)
                        notify_success(msg) if ok else notify_error(msg)
                        st.rerun()
                with b3:
                    if st.button("Reset PW", key=f"reset_{user['id']}"):
                        temp_password = "".join(secrets.choice(string.ascii_letters + string.digits) for _ in range(10))
                        ok, msg = reset_user_password(user["id"], hash_password_for_admin(temp_password), admin_id)
                        if ok:
                            st.info(f"Temporary password for {user['email']}: `{temp_password}` (share securely)")
                        else:
                            notify_error(msg)
                with b4:
                    if st.button("Delete", key=f"del_{user['id']}"):
                        ok, msg = delete_user(user["id"], admin_id)
                        notify_success(msg) if ok else notify_error(msg)
                        st.rerun()
        section_card_end()
