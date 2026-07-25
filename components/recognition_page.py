"""
Image Recognition page: drag-and-drop upload, preview, YOLOv11 detection,
annotated results, summary stats, and downloads (image / CSV / JSON).
"""
from __future__ import annotations

import io
import json

import pandas as pd
import streamlit as st
from PIL import Image as PILImage

from ai.yolo_service import AVAILABLE_MODELS
from components.ui import (
    empty_state,
    metric_row,
    notify_error,
    notify_success,
    page_header,
    section_card_end,
    section_card_start,
    status_badge,
)
from services.image_service import process_and_store_detection, validate_upload
from services.settings_service import get_or_create_settings


def render_image_recognition() -> None:
    page_header("Image Recognition", "Upload an image and let AI detect every object in it.")

    user_settings = get_or_create_settings(st.session_state["user_id"])

    with st.expander("⚙️ Detection Settings", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            model_label = st.selectbox(
                "Model size",
                list(AVAILABLE_MODELS.keys()),
                index=list(AVAILABLE_MODELS.values()).index(user_settings["default_model"])
                if user_settings["default_model"] in AVAILABLE_MODELS.values() else 0,
            )
        with col2:
            confidence = st.slider("Confidence threshold", 0.05, 0.95, float(user_settings["default_confidence"]), 0.05)
    model_name = AVAILABLE_MODELS[model_label]

    section_card_start("Upload an Image")
    uploaded_file = st.file_uploader(
        "Drag and drop or browse a file",
        type=["jpg", "jpeg", "png", "bmp", "webp"],
        help="Maximum size: 15 MB",
    )
    section_card_end()

    if uploaded_file is None:
        empty_state("🖼️", "No image uploaded yet", "Upload a JPG, PNG, BMP, or WEBP file to get started.")
        return

    validation = validate_upload(uploaded_file.name, uploaded_file.size)
    if not validation.ok:
        notify_error(validation.message)
        return

    try:
        pil_image = PILImage.open(uploaded_file)
        pil_image.load()
    except Exception:
        notify_error("This file could not be read as an image. It may be corrupted.")
        return

    section_card_start("Preview")
    col1, col2 = st.columns([2, 1])
    with col1:
        st.image(pil_image, caption=uploaded_file.name, use_container_width=True)
    with col2:
        st.markdown(f"**File name:** {uploaded_file.name}")
        st.markdown(f"**Format:** {pil_image.format or 'Unknown'}")
        st.markdown(f"**Resolution:** {pil_image.width} × {pil_image.height}")
        st.markdown(f"**File size:** {uploaded_file.size / 1024:.1f} KB")
    section_card_end()

    if st.button("🔍 Recognize Image", use_container_width=True, type="primary"):
        with st.spinner("Running AI detection..."):
            outcome, image_id = process_and_store_detection(
                user_id=st.session_state["user_id"],
                original_filename=uploaded_file.name,
                pil_image=pil_image,
                file_size_bytes=uploaded_file.size,
                model_name=model_name,
                confidence=confidence,
            )
        st.session_state["last_detection_outcome"] = outcome
        st.session_state["last_detection_image_id"] = image_id

    outcome = st.session_state.get("last_detection_outcome")
    if outcome is None:
        return

    if not outcome.success:
        notify_error(outcome.message)
        return

    notify_success("Detection complete.")
    _render_results(outcome, uploaded_file.name)


def _render_results(outcome, filename: str) -> None:
    section_card_start("Detection Result")
    st.image(outcome.annotated_image, caption="Detected objects", use_container_width=True)
    section_card_end()

    confidences = [d.confidence for d in outcome.detections]
    metric_row(
        [
            {"label": "Total Objects", "value": str(len(outcome.detections)), "icon": "🎯"},
            {"label": "Processing Time", "value": f"{outcome.processing_time_ms:.0f} ms", "icon": "⏱️"},
            {"label": "Highest Confidence", "value": f"{max(confidences):.0%}" if confidences else "—", "icon": "📈"},
            {"label": "Average Confidence", "value": f"{(sum(confidences) / len(confidences)):.0%}" if confidences else "—", "icon": "📊"},
        ]
    )

    st.write("")
    section_card_start("Detected Objects")
    if not outcome.detections:
        empty_state("🔍", "No objects detected", "Try lowering the confidence threshold and running detection again.")
    else:
        df = pd.DataFrame(
            [
                {
                    "Object": d.class_name,
                    "Confidence": f"{d.confidence:.0%}",
                    "Box (x_min, y_min, x_max, y_max)": f"({d.x_min:.0f}, {d.y_min:.0f}, {d.x_max:.0f}, {d.y_max:.0f})",
                }
                for d in outcome.detections
            ]
        )
        st.dataframe(df, use_container_width=True, hide_index=True)
    section_card_end()

    if outcome.detections:
        _render_downloads(outcome, filename)


def _render_downloads(outcome, filename: str) -> None:
    section_card_start("Download Results")
    col1, col2, col3 = st.columns(3)

    with col1:
        buffer = io.BytesIO()
        outcome.annotated_image.save(buffer, format="PNG")
        st.download_button(
            "⬇️ Annotated Image", buffer.getvalue(), file_name=f"detected_{filename}.png", mime="image/png",
            use_container_width=True,
        )

    with col2:
        df = pd.DataFrame(
            [
                {"object": d.class_name, "confidence": d.confidence, "x_min": d.x_min, "y_min": d.y_min, "x_max": d.x_max, "y_max": d.y_max}
                for d in outcome.detections
            ]
        )
        st.download_button(
            "⬇️ CSV Report", df.to_csv(index=False).encode("utf-8"), file_name="detection_report.csv", mime="text/csv",
            use_container_width=True,
        )

    with col3:
        payload = {
            "filename": filename,
            "processing_time_ms": outcome.processing_time_ms,
            "objects": [
                {"class": d.class_name, "confidence": d.confidence, "box": [d.x_min, d.y_min, d.x_max, d.y_max]}
                for d in outcome.detections
            ],
        }
        st.download_button(
            "⬇️ JSON Report", json.dumps(payload, indent=2).encode("utf-8"), file_name="detection_report.json",
            mime="application/json", use_container_width=True,
        )
    section_card_end()
