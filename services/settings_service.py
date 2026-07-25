"""
Per-user settings (theme, default confidence/model, export format) and the
in-app notification center. Both are simple CRUD wrappers around their
respective tables.
"""
from __future__ import annotations

from sqlalchemy import select, update

from database.db import get_session
from database.models import Notification, UserSettings


def get_or_create_settings(user_id: int) -> dict:
    with get_session() as session:
        row = session.execute(select(UserSettings).where(UserSettings.user_id == user_id)).scalar_one_or_none()
        if row is None:
            row = UserSettings(user_id=user_id)
            session.add(row)
            session.flush()
        return {
            "theme": row.theme,
            "default_confidence": row.default_confidence,
            "default_model": row.default_model,
            "export_format": row.export_format,
            "notifications_enabled": row.notifications_enabled,
        }


def update_settings(user_id: int, **fields) -> None:
    with get_session() as session:
        row = session.execute(select(UserSettings).where(UserSettings.user_id == user_id)).scalar_one_or_none()
        if row is None:
            row = UserSettings(user_id=user_id)
            session.add(row)
            session.flush()
        for key, value in fields.items():
            if hasattr(row, key) and value is not None:
                setattr(row, key, value)


def reset_settings(user_id: int) -> None:
    update_settings(
        user_id,
        theme="light",
        default_confidence=0.25,
        default_model="yolo11n.pt",
        export_format="csv",
        notifications_enabled=True,
    )


def add_notification(user_id: int, message: str, category: str = "info") -> None:
    with get_session() as session:
        session.add(Notification(user_id=user_id, message=message, category=category))


def get_notifications(user_id: int, unread_only: bool = False, limit: int = 20) -> list[dict]:
    with get_session() as session:
        stmt = select(Notification).where(Notification.user_id == user_id)
        if unread_only:
            stmt = stmt.where(Notification.is_read.is_(False))
        stmt = stmt.order_by(Notification.created_at.desc()).limit(limit)
        rows = session.execute(stmt).scalars().all()
        return [
            {"id": r.id, "message": r.message, "category": r.category, "is_read": r.is_read, "created_at": r.created_at}
            for r in rows
        ]


def mark_all_read(user_id: int) -> None:
    with get_session() as session:
        session.execute(
            update(Notification).where(Notification.user_id == user_id).values(is_read=True)
        )
