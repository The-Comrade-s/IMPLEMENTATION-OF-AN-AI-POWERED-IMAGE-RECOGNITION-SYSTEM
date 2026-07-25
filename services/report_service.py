"""
Generates downloadable reports (CSV / Excel / PDF) for a user's detection
history. All functions return raw bytes suitable for st.download_button.
"""
from __future__ import annotations

import datetime as dt
import io

import pandas as pd
from sqlalchemy import select

from config.config import settings
from database.db import get_session
from database.models import DetectionResult, Image, User


def _history_dataframe(user_id: int) -> pd.DataFrame:
    with get_session() as session:
        rows = session.execute(
            select(
                Image.original_filename,
                Image.uploaded_at,
                Image.processing_time_ms,
                Image.object_count,
                DetectionResult.class_name,
                DetectionResult.confidence,
            )
            .join(DetectionResult, DetectionResult.image_id == Image.id, isouter=True)
            .where(Image.user_id == user_id)
            .order_by(Image.uploaded_at.desc())
        ).all()
    return pd.DataFrame(
        rows,
        columns=["filename", "detected_at", "processing_time_ms", "object_count", "detected_object", "confidence"],
    )


def generate_csv_report(user_id: int) -> bytes:
    df = _history_dataframe(user_id)
    return df.to_csv(index=False).encode("utf-8")


def generate_excel_report(user_id: int) -> bytes:
    df = _history_dataframe(user_id)
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Detection History")
    return buffer.getvalue()


def generate_pdf_report(user_id: int) -> bytes:
    """Build a simple, professional PDF summary report using reportlab."""
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

    with get_session() as session:
        user = session.get(User, user_id)
        user_name = user.full_name if user else "Unknown User"
        user_email = user.email if user else ""

    df = _history_dataframe(user_id)

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    story = [
        Paragraph(settings.app_name, styles["Title"]),
        Paragraph("Detection Report", styles["Heading2"]),
        Spacer(1, 12),
        Paragraph(f"User: {user_name} ({user_email})", styles["Normal"]),
        Paragraph(f"Generated: {dt.datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}", styles["Normal"]),
        Paragraph(f"Total detection records: {len(df)}", styles["Normal"]),
        Spacer(1, 16),
    ]

    if df.empty:
        story.append(Paragraph("No detection history available.", styles["Normal"]))
    else:
        table_data = [["Filename", "Object", "Confidence", "Detected At"]]
        for _, row in df.head(200).iterrows():
            table_data.append(
                [
                    str(row["filename"])[:30],
                    str(row["detected_object"]) if pd.notna(row["detected_object"]) else "-",
                    f"{row['confidence']:.0%}" if pd.notna(row["confidence"]) else "-",
                    str(row["detected_at"])[:19],
                ]
            )
        table = Table(table_data, repeatRows=1)
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2952e3")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTSIZE", (0, 0), (-1, -1), 8),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f5f7fb")]),
                ]
            )
        )
        story.append(table)

    doc.build(story)
    return buffer.getvalue()
