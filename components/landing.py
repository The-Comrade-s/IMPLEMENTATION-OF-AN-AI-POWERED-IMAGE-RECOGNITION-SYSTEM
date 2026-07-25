"""
Public landing page shown before login.
"""
from __future__ import annotations

import streamlit as st

from config.config import settings


def render_landing() -> None:
    st.markdown(
        f"""
        <div class="airs-hero">
            <div style="font-size:52px;">{settings.app_icon}</div>
            <h1>{settings.app_name}</h1>
            <p>Upload an image and let state-of-the-art computer vision detect, label, and
            score every object in it — in seconds, with a professional dashboard to track
            every result over time.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("🚀 Get Started", use_container_width=True):
            st.session_state.auth_view = "login"
            st.rerun()

    st.markdown("### Why Choose Our AI")
    features = [
        ("⚡", "Fast Detection", "Optimized inference pipeline built for quick, responsive results."),
        ("🎯", "High Accuracy", "Powered by a modern object-detection architecture."),
        ("📊", "Rich Analytics", "Track detections, confidence trends, and history over time."),
        ("🔒", "Secure by Design", "Bcrypt password hashing and protected sessions throughout."),
    ]
    cols = st.columns(4)
    for col, (icon, title, desc) in zip(cols, features):
        with col:
            st.markdown(
                f"""
                <div class="airs-feature-card">
                    <div style="font-size:28px;">{icon}</div>
                    <div style="font-weight:700; margin:8px 0 4px 0;">{title}</div>
                    <div style="color:#6b7280; font-size:13.5px;">{desc}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown(
        f"""
        <div class="airs-footer">
            © {2026} {settings.app_name} · Built with Python & Streamlit
        </div>
        """,
        unsafe_allow_html=True,
    )
