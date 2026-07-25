"""
Admin Image Management: browse, search, and delete any user's uploaded
images (AIRS-004).
"""
from __future__ import annotations

import streamlit as st

from components.admin.guard import require_admin
from components.ui import empty_state, notify_success, page_header, section_card_end, section_card_start
from services.admin_service import admin_delete_image, list_all_images


def render_image_management() -> None:
    if not require_admin():
        return

    page_header("Image Management", "Browse and manage every image uploaded across the system.")

    search = st.text_input("🔍 Search by filename or uploader email", "")
    images = list_all_images(search=search)

    if not images:
        empty_state("🖼️", "No images found", "Try a different search term.")
        return

    st.caption(f"{len(images)} image(s) found")

    for image in images:
        section_card_start()
        col_img, col_info, col_action = st.columns([1, 3, 1])
        with col_img:
            if image["annotated_path"]:
                st.image(image["annotated_path"], use_container_width=True)
        with col_info:
            st.markdown(f"**{image['filename']}**")
            st.caption(f"Uploaded by {image['user_email']} · {image['uploaded_at'].strftime('%Y-%m-%d %H:%M')}")
            st.caption(f"{image['object_count']} object(s) detected")
        with col_action:
            if st.button("🗑️ Delete", key=f"admin_del_img_{image['id']}", use_container_width=True):
                admin_delete_image(image["id"], st.session_state["user_id"])
                notify_success("Image deleted.")
                st.rerun()
        section_card_end()
