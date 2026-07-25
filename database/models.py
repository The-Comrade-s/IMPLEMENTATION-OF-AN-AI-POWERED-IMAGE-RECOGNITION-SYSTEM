"""
SQLAlchemy ORM models.

AIRS-001 defined User. AIRS-002 adds Image + DetectionResult for the
detection engine and history. AIRS-003 adds UserSettings + Notification
for preferences and the in-app notification center. AIRS-004 adds
SystemLog for admin auditing. No existing column on User/Image/
DetectionResult is renamed or removed by later phases — only appended to.
"""
from __future__ import annotations

import datetime as dt

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Declarative base shared by all ORM models."""


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    full_name: Mapped[str] = mapped_column(String(150), nullable=False)
    email: Mapped[str] = mapped_column(String(150), nullable=False, unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False, default="user")
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime, default=dt.datetime.utcnow)
    last_login: Mapped[dt.datetime | None] = mapped_column(DateTime, nullable=True)
    # AIRS-003 additions (nullable so AIRS-001 rows remain valid):
    avatar_path: Mapped[str | None] = mapped_column(String(500), nullable=True)

    images: Mapped[list["Image"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    settings: Mapped["UserSettings | None"] = relationship(back_populates="user", uselist=False, cascade="all, delete-orphan")
    notifications: Mapped[list["Notification"]] = relationship(back_populates="user", cascade="all, delete-orphan")

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return f"<User id={self.id} email={self.email!r} role={self.role!r}>"


class Image(Base):
    """An uploaded image and its detection run (AIRS-002)."""

    __tablename__ = "images"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    stored_path: Mapped[str] = mapped_column(String(500), nullable=False)
    annotated_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    file_size_bytes: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    width: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    height: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    image_format: Mapped[str] = mapped_column(String(20), nullable=False, default="")
    uploaded_at: Mapped[dt.datetime] = mapped_column(DateTime, default=dt.datetime.utcnow)
    processing_time_ms: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    object_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    confidence_threshold: Mapped[float] = mapped_column(Float, nullable=False, default=0.25)
    model_name: Mapped[str] = mapped_column(String(50), nullable=False, default="yolo11n.pt")

    user: Mapped["User"] = relationship(back_populates="images")
    detections: Mapped[list["DetectionResult"]] = relationship(back_populates="image", cascade="all, delete-orphan")

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Image id={self.id} file={self.original_filename!r} objects={self.object_count}>"


class DetectionResult(Base):
    """A single detected object within an Image (AIRS-002)."""

    __tablename__ = "detection_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    image_id: Mapped[int] = mapped_column(ForeignKey("images.id"), nullable=False, index=True)
    class_name: Mapped[str] = mapped_column(String(100), nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    x_min: Mapped[float] = mapped_column(Float, nullable=False)
    y_min: Mapped[float] = mapped_column(Float, nullable=False)
    x_max: Mapped[float] = mapped_column(Float, nullable=False)
    y_max: Mapped[float] = mapped_column(Float, nullable=False)
    box_color: Mapped[str] = mapped_column(String(20), nullable=False, default="#2952e3")

    image: Mapped["Image"] = relationship(back_populates="detections")


class UserSettings(Base):
    """Per-user preferences (AIRS-003)."""

    __tablename__ = "user_settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, unique=True)
    theme: Mapped[str] = mapped_column(String(20), nullable=False, default="light")
    default_confidence: Mapped[float] = mapped_column(Float, nullable=False, default=0.25)
    default_model: Mapped[str] = mapped_column(String(50), nullable=False, default="yolo11n.pt")
    export_format: Mapped[str] = mapped_column(String(10), nullable=False, default="csv")
    notifications_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    user: Mapped["User"] = relationship(back_populates="settings")


class Notification(Base):
    """In-app notification for a user or admin (AIRS-003/004)."""

    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    category: Mapped[str] = mapped_column(String(30), nullable=False, default="info")  # success|error|warning|info
    message: Mapped[str] = mapped_column(String(500), nullable=False)
    is_read: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime, default=dt.datetime.utcnow)

    user: Mapped["User"] = relationship(back_populates="notifications")


class SystemLog(Base):
    """Admin-facing audit log (AIRS-004). Separate from the rotating file log."""

    __tablename__ = "system_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    action: Mapped[str] = mapped_column(String(50), nullable=False)
    details: Mapped[str] = mapped_column(Text, nullable=False, default="")
    level: Mapped[str] = mapped_column(String(20), nullable=False, default="INFO")
    created_at: Mapped[dt.datetime] = mapped_column(DateTime, default=dt.datetime.utcnow)
