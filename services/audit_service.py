"""
Writes admin-facing audit entries to the SystemLog table (separate from the
rotating file log in utils/logger.py, which is for developer debugging).
"""
from __future__ import annotations

from sqlalchemy import select

from database.db import get_session
from database.models import SystemLog
from utils.logger import get_logger

logger = get_logger(__name__)


def record_event(action: str, details: str = "", user_id: int | None = None, level: str = "INFO") -> None:
    """Persist an auditable event. Never raises — logging failures must not break the app."""
    try:
        with get_session() as session:
            session.add(SystemLog(user_id=user_id, action=action, details=details, level=level))
    except Exception:
        logger.exception("Failed to write system log entry for action=%s", action)


def get_recent_logs(limit: int = 200, level: str | None = None, action_contains: str | None = None) -> list[dict]:
    """Fetch recent audit log entries, most recent first, optionally filtered."""
    with get_session() as session:
        stmt = select(SystemLog).order_by(SystemLog.created_at.desc()).limit(limit)
        if level:
            stmt = stmt.where(SystemLog.level == level)
        if action_contains:
            stmt = stmt.where(SystemLog.action.ilike(f"%{action_contains}%"))
        rows = session.execute(stmt).scalars().all()
        return [
            {
                "id": row.id,
                "user_id": row.user_id,
                "action": row.action,
                "details": row.details,
                "level": row.level,
                "created_at": row.created_at,
            }
            for row in rows
        ]
