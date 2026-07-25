"""
Admin AI Management: view/change the active YOLO model and default
confidence threshold, reload, and health-check the model (AIRS-004).
"""
from __future__ import annotations

import streamlit as st

from ai.yolo_service import AVAILABLE_MODELS
from components.admin.guard import require_admin
from components.ui import notify_error, notify_success, page_header, section_card_end, section_card_start
from services.ai_management_service import get_ai_config, reload_model, test_model, update_ai_config


def render_ai_management() -> None:
    if not require_admin():
        return

    page_header("AI Management", "Configure and monitor the object detection engine.")

    config = get_ai_config()
    section_card_start("Current Configuration")
    st.markdown(f"**Active model:** `{config['model_name']}`")
    st.markdown(f"**Default confidence threshold:** {config['confidence_threshold']:.0%}")
    st.markdown(f"**Last reload:** {config['last_reload'] or 'Never'}")
    section_card_end()

    section_card_start("Update Configuration")
    model_labels = list(AVAILABLE_MODELS.keys())
    model_values = list(AVAILABLE_MODELS.values())
    current_index = model_values.index(config["model_name"]) if config["model_name"] in model_values else 0

    new_model_label = st.selectbox("YOLO model size", model_labels, index=current_index)
    new_threshold = st.slider("Default confidence threshold", 0.05, 0.95, float(config["confidence_threshold"]), 0.05)

    if st.button("💾 Save Configuration"):
        ok, message = update_ai_config(
            model_name=AVAILABLE_MODELS[new_model_label],
            confidence_threshold=new_threshold,
            admin_id=st.session_state["user_id"],
        )
        notify_success(message) if ok else notify_error(message)
    section_card_end()

    section_card_start("Model Health")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Reload Model", use_container_width=True):
            with st.spinner("Reloading model..."):
                ok, message = reload_model(admin_id=st.session_state["user_id"])
            notify_success(message) if ok else notify_error(message)
    with col2:
        if st.button("🩺 Test Model", use_container_width=True):
            with st.spinner("Running health check..."):
                ok, message = test_model(admin_id=st.session_state["user_id"])
            notify_success(message) if ok else notify_error(message)
    st.caption("Reloading downloads model weights automatically if they are not already cached locally.")
    section_card_end()
