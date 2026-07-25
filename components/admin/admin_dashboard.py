"""
Admin Dashboard: system-wide metrics and health overview (AIRS-004).
"""
from __future__ import annotations

import streamlit as st

from components.admin.guard import require_admin
from components.ui import metric_row, page_header, section_card_end, section_card_start
from services.admin_service import get_system_stats
from services.ai_management_service import get_ai_config


def render_admin_dashboard() -> None:
    if not require_admin():
        return

    page_header("Admin Dashboard", "System-wide health and usage overview.")

    stats = get_system_stats()
    ai_config = get_ai_config()

    metric_row(
        [
            {"label": "Total Users", "value": str(stats["total_users"]), "icon": "👥"},
            {"label": "Active Users", "value": str(stats["active_users"]), "icon": "✅"},
            {"label": "Images Processed", "value": str(stats["total_images"]), "icon": "🖼️"},
            {"label": "Objects Detected", "value": str(stats["total_objects"]), "icon": "🎯"},
        ]
    )
    st.write("")
    metric_row(
        [
            {"label": "Database Size", "value": f"{stats['database_size_mb']:.2f} MB", "icon": "🗄️"},
            {"label": "Storage Used", "value": f"{stats['storage_used_mb']:.2f} MB", "icon": "💾"},
            {
                "label": "Avg. Processing Time",
                "value": f"{stats['avg_processing_ms']:.0f} ms" if stats["avg_processing_ms"] else "—",
                "icon": "⏱️",
            },
            {"label": "Active AI Model", "value": ai_config["model_name"], "icon": "🧠"},
        ]
    )

    st.write("")
    section_card_start("System Status")
    st.markdown("🟢 Application: **Running**")
    st.markdown(f"🧠 AI Model: **{ai_config['model_name']}** (confidence ≥ {ai_config['confidence_threshold']:.0%})")
    st.markdown(f"🗄️ Database: **SQLite** ({stats['database_size_mb']:.2f} MB)")
    section_card_end()
