"""
Analytics page: interactive Plotly charts driven by services/analytics_service.py.
"""
from __future__ import annotations

import plotly.express as px
import streamlit as st

from components.ui import empty_state, page_header, section_card_end, section_card_start
from services.analytics_service import (
    confidence_distribution,
    detections_by_day,
    detections_by_month,
    object_category_breakdown,
    processing_time_trend,
    top_detected_objects,
)


def render_analytics() -> None:
    page_header("Analytics", "Track trends across all of your detections.")

    user_id = st.session_state["user_id"]
    top_objects = top_detected_objects(user_id)

    if top_objects.empty:
        empty_state("📊", "Not enough data yet", "Run a few detections to unlock analytics charts.")
        return

    col1, col2 = st.columns(2)

    with col1:
        section_card_start("Top 10 Detected Objects")
        fig = px.bar(top_objects, x="object", y="count", color="count", color_continuous_scale="Blues")
        fig.update_layout(showlegend=False, height=320, margin=dict(t=10, b=10))
        st.plotly_chart(fig, use_container_width=True)
        section_card_end()

    with col2:
        section_card_start("Object Category Breakdown")
        breakdown = object_category_breakdown(user_id)
        fig = px.pie(breakdown, names="object", values="count", hole=0.45)
        fig.update_layout(height=320, margin=dict(t=10, b=10))
        st.plotly_chart(fig, use_container_width=True)
        section_card_end()

    col3, col4 = st.columns(2)

    with col3:
        section_card_start("Daily Detection Activity")
        by_day = detections_by_day(user_id)
        if by_day.empty:
            empty_state("📅", "No recent activity", "Detections from the last 14 days will appear here.")
        else:
            fig = px.line(by_day, x="day", y="count", markers=True)
            fig.update_layout(height=300, margin=dict(t=10, b=10))
            st.plotly_chart(fig, use_container_width=True)
        section_card_end()

    with col4:
        section_card_start("Confidence Score Distribution")
        conf = confidence_distribution(user_id)
        fig = px.histogram(conf, x="confidence", nbins=20)
        fig.update_layout(height=300, margin=dict(t=10, b=10))
        st.plotly_chart(fig, use_container_width=True)
        section_card_end()

    col5, col6 = st.columns(2)

    with col5:
        section_card_start("Detection Frequency by Month")
        by_month = detections_by_month(user_id)
        fig = px.bar(by_month, x="month", y="count")
        fig.update_layout(height=300, margin=dict(t=10, b=10))
        st.plotly_chart(fig, use_container_width=True)
        section_card_end()

    with col6:
        section_card_start("Processing Time Trend")
        trend = processing_time_trend(user_id)
        fig = px.line(trend, x=trend.index, y="processing_time_ms", markers=True)
        fig.update_layout(height=300, margin=dict(t=10, b=10), xaxis_title="Recent detections")
        st.plotly_chart(fig, use_container_width=True)
        section_card_end()
