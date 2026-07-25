"""
Reusable, presentation-only Streamlit UI components.
Keeping these separate from page logic avoids duplicated markup across pages.
"""
from __future__ import annotations

import streamlit as st


def load_css(css_path) -> None:
    """Inject the custom stylesheet into the current Streamlit page."""
    with open(css_path, "r", encoding="utf-8") as css_file:
        st.markdown(f"<style>{css_file.read()}</style>", unsafe_allow_html=True)


def page_header(title: str, subtitle: str = "") -> None:
    """Render a gradient page header used at the top of every page."""
    subtitle_html = f'<p class="airs-header-subtitle">{subtitle}</p>' if subtitle else ""
    st.markdown(
        f"""
        <div class="airs-header">
            <h1>{title}</h1>
            {subtitle_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def metric_card(label: str, value: str, icon: str = "📊", delta: str = "") -> None:
    """Render a single premium metric card."""
    delta_html = f'<div class="airs-metric-delta">{delta}</div>' if delta else ""
    st.markdown(
        f"""
        <div class="airs-metric-card">
            <div class="airs-metric-icon">{icon}</div>
            <div class="airs-metric-value">{value}</div>
            <div class="airs-metric-label">{label}</div>
            {delta_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def metric_row(items: list[dict]) -> None:
    """Render a row of metric cards. Each item: {label, value, icon, delta}."""
    columns = st.columns(len(items))
    for column, item in zip(columns, items):
        with column:
            metric_card(
                label=item.get("label", ""),
                value=item.get("value", ""),
                icon=item.get("icon", "📊"),
                delta=item.get("delta", ""),
            )


def status_badge(text: str, kind: str = "info") -> str:
    """Return HTML for a colour-coded status badge. kind: success|error|warning|info."""
    return f'<span class="airs-badge airs-badge-{kind}">{text}</span>'


def empty_state(icon: str, title: str, description: str) -> None:
    """Render a friendly empty state placeholder."""
    st.markdown(
        f"""
        <div class="airs-empty-state">
            <div class="airs-empty-icon">{icon}</div>
            <div class="airs-empty-title">{title}</div>
            <div class="airs-empty-desc">{description}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def notify_success(message: str) -> None:
    st.markdown(f'<div class="airs-alert airs-alert-success">✅ {message}</div>', unsafe_allow_html=True)


def notify_error(message: str) -> None:
    st.markdown(f'<div class="airs-alert airs-alert-error">⚠️ {message}</div>', unsafe_allow_html=True)


def section_card_start(title: str = "") -> None:
    title_html = f'<div class="airs-card-title">{title}</div>' if title else ""
    st.markdown(f'<div class="airs-card">{title_html}', unsafe_allow_html=True)


def section_card_end() -> None:
    st.markdown("</div>", unsafe_allow_html=True)
