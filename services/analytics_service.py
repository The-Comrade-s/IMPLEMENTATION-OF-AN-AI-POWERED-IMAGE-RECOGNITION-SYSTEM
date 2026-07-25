"""
Aggregation queries for the Analytics page. Kept separate from image_service
(which handles per-image CRUD) since these are read-only reporting queries.
"""
from __future__ import annotations

import datetime as dt

import pandas as pd
from sqlalchemy import func, select

from database.db import get_session
from database.models import DetectionResult, Image


def top_detected_objects(user_id: int, limit: int = 10) -> pd.DataFrame:
    with get_session() as session:
        rows = session.execute(
            select(DetectionResult.class_name, func.count().label("count"))
            .join(Image, Image.id == DetectionResult.image_id)
            .where(Image.user_id == user_id)
            .group_by(DetectionResult.class_name)
            .order_by(func.count().desc())
            .limit(limit)
        ).all()
        return pd.DataFrame(rows, columns=["object", "count"])


def confidence_distribution(user_id: int) -> pd.DataFrame:
    with get_session() as session:
        rows = session.execute(
            select(DetectionResult.confidence)
            .join(Image, Image.id == DetectionResult.image_id)
            .where(Image.user_id == user_id)
        ).all()
        return pd.DataFrame(rows, columns=["confidence"])


def detections_by_day(user_id: int, days: int = 14) -> pd.DataFrame:
    since = dt.datetime.utcnow() - dt.timedelta(days=days)
    with get_session() as session:
        rows = session.execute(
            select(func.date(Image.uploaded_at).label("day"), func.count().label("count"))
            .where(Image.user_id == user_id, Image.uploaded_at >= since)
            .group_by(func.date(Image.uploaded_at))
            .order_by("day")
        ).all()
        return pd.DataFrame(rows, columns=["day", "count"])


def detections_by_month(user_id: int) -> pd.DataFrame:
    with get_session() as session:
        rows = session.execute(
            select(func.strftime("%Y-%m", Image.uploaded_at).label("month"), func.count().label("count"))
            .where(Image.user_id == user_id)
            .group_by("month")
            .order_by("month")
        ).all()
        return pd.DataFrame(rows, columns=["month", "count"])


def processing_time_trend(user_id: int, limit: int = 50) -> pd.DataFrame:
    with get_session() as session:
        rows = session.execute(
            select(Image.uploaded_at, Image.processing_time_ms)
            .where(Image.user_id == user_id)
            .order_by(Image.uploaded_at.desc())
            .limit(limit)
        ).all()
        df = pd.DataFrame(rows, columns=["uploaded_at", "processing_time_ms"])
        return df.iloc[::-1].reset_index(drop=True)


def object_category_breakdown(user_id: int, limit: int = 8) -> pd.DataFrame:
    return top_detected_objects(user_id, limit=limit)
