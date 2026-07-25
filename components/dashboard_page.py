"""
Dashboard page — now driven by real detection data (AIRS-003), replacing the
AIRS-001 placeholder metrics.
"""
from __future__ import annotations

import datetime as dt

import streamlit as st

from components.ui import empty_state, metric_row, page_header, section_card_end, section_card_start
from services.image_service import get_dashboard_stats


def render_dashboard() -> None:
    page_header(
        f"Welcome, {st.session_state.get('full_name', 'there')} 👋",
        f"{dt.datetime.now().strftime('%A, %d %B %Y — %H:%M')}",
    )

    stats = get_dashboard_stats(st.session_state["user_id"])

    metric_row(
        [
            {"label": "Images Processed", "value": str(stats["total_images"]), "icon": "🖼️"},
            {"label": "Objects Detected", "value": str(stats["total_objects"]), "icon": "🎯"},
            {
                "label": "Avg. Confidence",
                "value": f"{stats['avg_confidence']:.0%}" if stats["avg_confidence"] is not None else "—",
                "icon": "📈",
            },
            {
                "label": "Avg. Processing Time",
                "value": f"{stats['avg_processing_ms']:.0f} ms" if stats["avg_processing_ms"] is not None else "—",
                "icon": "⏱️",
            },
        ]
    )
    st.write("")
    metric_row(
        [
            {"label": "Detections Today", "value": str(stats["detections_today"]), "icon": "📅"},
            {"label": "Detections This Week", "value": str(stats["detections_week"]), "icon": "🗓️"},
            {"label": "Most Detected Object", "value": stats["top_object"] or "—", "icon": "🏆"},
        ]
    )

    st.write("")
    section_card_start("Recent Activity")
    if not stats["recent"]:
        empty_state(
            icon="📭",
            title="No activity yet",
            description="Head to Image Recognition to run your first AI detection.",
        )
    else:
        for item in stats["recent"]:
            st.markdown(
                f"**{item['filename']}** · {item['object_count']} object(s) · "
                f"{item['uploaded_at'].strftime('%Y-%m-%d %H:%M')}"
            )
    section_card_end()
