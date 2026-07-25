"""
Administrator-only operations: user management, system-wide statistics,
database maintenance. All functions here assume the caller has already
verified the requesting user has the 'admin' role (enforced in the UI layer
via components/admin/guard.py).
"""
from __future__ import annotations

import datetime as dt
import shutil
from pathlib import Path

from sqlalchemy import func, select

from config.config import settings
from database.db import engine, get_session
from database.models import DetectionResult, Image, User
from services.audit_service import record_event
from utils.logger import get_logger

logger = get_logger(__name__)

BACKUP_DIR = settings.database_path.parent / "backups"
BACKUP_DIR.mkdir(parents=True, exist_ok=True)


# ---------- User management ----------

def list_users(search: str = "") -> list[dict]:
    with get_session() as session:
        stmt = select(User).order_by(User.created_at.desc())
        rows = session.execute(stmt).scalars().all()
        results = []
        for u in rows:
            if search and search.lower() not in f"{u.full_name} {u.email}".lower():
                continue
            results.append(
                {
                    "id": u.id,
                    "full_name": u.full_name,
                    "email": u.email,
                    "role": u.role,
                    "is_active": u.is_active,
                    "created_at": u.created_at,
                    "last_login": u.last_login,
                }
            )
        return results


def set_user_active(user_id: int, is_active: bool, admin_id: int) -> tuple[bool, str]:
    with get_session() as session:
        user = session.get(User, user_id)
        if user is None:
            return False, "User not found."
        user.is_active = is_active
        session.add(user)
    record_event("user_status_changed", f"user_id={user_id} active={is_active}", user_id=admin_id)
    return True, f"User has been {'activated' if is_active else 'deactivated'}."


def set_user_role(user_id: int, role: str, admin_id: int) -> tuple[bool, str]:
    if role not in ("user", "admin"):
        return False, "Invalid role."
    with get_session() as session:
        user = session.get(User, user_id)
        if user is None:
            return False, "User not found."
        user.role = role
        session.add(user)
    record_event("user_role_changed", f"user_id={user_id} role={role}", user_id=admin_id)
    return True, f"User role updated to {role}."


def delete_user(user_id: int, admin_id: int) -> tuple[bool, str]:
    with get_session() as session:
        user = session.get(User, user_id)
        if user is None:
            return False, "User not found."
        session.delete(user)
    record_event("user_deleted", f"user_id={user_id}", user_id=admin_id, level="WARNING")
    return True, "User deleted."


def reset_user_password(user_id: int, new_password_hash: str, admin_id: int) -> tuple[bool, str]:
    with get_session() as session:
        user = session.get(User, user_id)
        if user is None:
            return False, "User not found."
        user.password_hash = new_password_hash
        session.add(user)
    record_event("user_password_reset", f"user_id={user_id}", user_id=admin_id, level="WARNING")
    return True, "Password reset successfully."


# ---------- Image management ----------

def list_all_images(search: str = "", limit: int = 300) -> list[dict]:
    with get_session() as session:
        stmt = (
            select(Image, User.email)
            .join(User, User.id == Image.user_id)
            .order_by(Image.uploaded_at.desc())
            .limit(limit)
        )
        rows = session.execute(stmt).all()
        results = []
        for image, email in rows:
            if search and search.lower() not in f"{image.original_filename} {email}".lower():
                continue
            results.append(
                {
                    "id": image.id,
                    "filename": image.original_filename,
                    "user_email": email,
                    "uploaded_at": image.uploaded_at,
                    "object_count": image.object_count,
                    "stored_path": image.stored_path,
                    "annotated_path": image.annotated_path,
                }
            )
        return results


def admin_delete_image(image_id: int, admin_id: int) -> bool:
    with get_session() as session:
        row = session.get(Image, image_id)
        if row is None:
            return False
        for path_str in (row.stored_path, row.annotated_path):
            if path_str:
                Path(path_str).unlink(missing_ok=True)
        session.delete(row)
    record_event("admin_deleted_image", f"image_id={image_id}", user_id=admin_id)
    return True


# ---------- System stats ----------

def get_system_stats() -> dict:
    with get_session() as session:
        total_users = session.execute(select(func.count()).select_from(User)).scalar_one()
        active_users = session.execute(select(func.count()).select_from(User).where(User.is_active.is_(True))).scalar_one()
        total_images = session.execute(select(func.count()).select_from(Image)).scalar_one()
        total_objects = session.execute(select(func.coalesce(func.sum(Image.object_count), 0))).scalar_one()
        avg_processing = session.execute(select(func.avg(Image.processing_time_ms))).scalar_one()

    db_size_bytes = settings.database_path.stat().st_size if settings.database_path.exists() else 0
    storage_bytes = sum(f.stat().st_size for f in settings.uploads_dir.glob("**/*") if f.is_file())
    storage_bytes += sum(f.stat().st_size for f in settings.history_dir.glob("**/*") if f.is_file())

    return {
        "total_users": total_users or 0,
        "active_users": active_users or 0,
        "total_images": total_images or 0,
        "total_objects": int(total_objects or 0),
        "avg_processing_ms": float(avg_processing) if avg_processing is not None else None,
        "database_size_mb": db_size_bytes / 1_048_576,
        "storage_used_mb": storage_bytes / 1_048_576,
    }


# ---------- Database maintenance ----------

def backup_database(admin_id: int) -> tuple[bool, str, Path | None]:
    try:
        timestamp = dt.datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        backup_path = BACKUP_DIR / f"airs_backup_{timestamp}.db"
        engine.dispose()  # flush any pending writes before copying the file
        shutil.copy2(settings.database_path, backup_path)
        record_event("database_backup", str(backup_path), user_id=admin_id)
        return True, "Backup created successfully.", backup_path
    except Exception as exc:
        logger.exception("Database backup failed.")
        return False, f"Backup failed: {exc}", None


def list_backups() -> list[dict]:
    backups = sorted(BACKUP_DIR.glob("*.db"), key=lambda p: p.stat().st_mtime, reverse=True)
    return [
        {"name": p.name, "path": str(p), "size_mb": p.stat().st_size / 1_048_576, "created": dt.datetime.fromtimestamp(p.stat().st_mtime)}
        for p in backups
    ]


def restore_database(backup_path: str, admin_id: int) -> tuple[bool, str]:
    try:
        source = Path(backup_path)
        if not source.exists():
            return False, "Backup file not found."
        engine.dispose()
        shutil.copy2(source, settings.database_path)
        record_event("database_restore", backup_path, user_id=admin_id, level="WARNING")
        return True, "Database restored. Please restart the application."
    except Exception as exc:
        logger.exception("Database restore failed.")
        return False, f"Restore failed: {exc}"


def check_database_integrity() -> tuple[bool, str]:
    try:
        with engine.connect() as conn:
            result = conn.exec_driver_sql("PRAGMA integrity_check;").scalar()
        ok = result == "ok"
        return ok, result or "unknown"
    except Exception as exc:
        logger.exception("Database integrity check failed.")
        return False, str(exc)
