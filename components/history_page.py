"""
Detection History page. Search by filename/object, delete individual or all
records, and re-download prior results.
"""
from __future__ import annotations

import streamlit as st

from components.ui import empty_state, notify_success, page_header, section_card_end, section_card_start, status_badge
from services.image_service import delete_all_history, delete_image, get_user_history


def render_history() -> None:
    page_header("Detection History", "Review, search, and manage your past detections.")

    col1, col2 = st.columns([3, 1])
    with col1:
        search = st.text_input("🔍 Search by filename or detected object", "")
    with col2:
        sort_desc = st.selectbox("Sort", ["Newest first", "Oldest first"]) == "Newest first"

    history = get_user_history(st.session_state["user_id"], search=search)
    if not sort_desc:
        history = list(reversed(history))

    if not history:
        empty_state("🕒", "No detection history", "Run your first detection from the Image Recognition page.")
        return

    col_a, col_b = st.columns([1, 4])
    with col_a:
        if st.button("🗑️ Delete All History"):
            st.session_state["confirm_delete_all"] = True
    if st.session_state.get("confirm_delete_all"):
        st.warning("This will permanently delete all detection history. Are you sure?")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Yes, delete everything", type="primary"):
                count = delete_all_history(st.session_state["user_id"])
                st.session_state["confirm_delete_all"] = False
                notify_success(f"Deleted {count} record(s).")
                st.rerun()
        with c2:
            if st.button("Cancel"):
                st.session_state["confirm_delete_all"] = False
                st.rerun()

    st.caption(f"{len(history)} record(s) found")

    for record in history:
        section_card_start()
        col_img, col_info, col_actions = st.columns([1, 3, 1])
        with col_img:
            if record["annotated_path"]:
                st.image(record["annotated_path"], use_container_width=True)
        with col_info:
            st.markdown(f"**{record['filename']}**")
            st.caption(f"{record['uploaded_at'].strftime('%Y-%m-%d %H:%M')} · {record['processing_time_ms']:.0f} ms")
            objects_preview = ", ".join(record["objects"][:6]) or "No objects detected"
            st.markdown(status_badge(f"{record['object_count']} objects", "info"), unsafe_allow_html=True)
            st.caption(objects_preview)
        with col_actions:
            if record["annotated_path"]:
                with open(record["annotated_path"], "rb") as f:
                    st.download_button(
                        "⬇️ Image", f.read(), file_name=f"result_{record['filename']}.png",
                        key=f"dl_{record['id']}", use_container_width=True,
                    )
            if st.button("🗑️ Delete", key=f"del_{record['id']}", use_container_width=True):
                delete_image(st.session_state["user_id"], record["id"])
                notify_success("Record deleted.")
                st.rerun()
        section_card_end()
