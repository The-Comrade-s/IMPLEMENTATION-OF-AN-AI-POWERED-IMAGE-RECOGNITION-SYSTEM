"""
Handles saving uploaded images to disk, validating them, running detection,
persisting results to the database, and querying detection history.
"""
from __future__ import annotations

import datetime as dt
import uuid
from dataclasses import dataclass
from pathlib import Path

from PIL import Image as PILImage
from sqlalchemy import select, func

from ai.yolo_service import DetectionOutcome, run_detection
from config.config import settings
from database.db import get_session
from database.models import DetectionResult, Image
from utils.logger import get_logger

logger = get_logger(__name__)

ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "bmp", "webp"}
MAX_FILE_SIZE_BYTES = 15 * 1024 * 1024  # 15 MB
MAX_DIMENSION = 4000  # px, longest side before we downscale for inference


@dataclass
class UploadValidation:
    ok: bool
    message: str = ""


def validate_upload(filename: str, size_bytes: int) -> UploadValidation:
    """Validate a file before it is opened/processed."""
    extension = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if extension not in ALLOWED_EXTENSIONS:
        return UploadValidation(False, f"Unsupported file type '.{extension}'. Allowed: JPG, JPEG, PNG, BMP, WEBP.")
    if size_bytes <= 0:
        return UploadValidation(False, "The uploaded file appears to be empty.")
    if size_bytes > MAX_FILE_SIZE_BYTES:
        return UploadValidation(False, f"File is too large ({size_bytes / 1_048_576:.1f} MB). Maximum is 15 MB.")
    return UploadValidation(True)


def _safe_filename(original_filename: str) -> str:
    extension = original_filename.rsplit(".", 1)[-1].lower() if "." in original_filename else "jpg"
    return f"{uuid.uuid4().hex}.{extension}"


def _resize_if_needed(image: PILImage.Image) -> PILImage.Image:
    """Downscale very large images to keep inference responsive and memory-safe."""
    if max(image.size) <= MAX_DIMENSION:
        return image
    ratio = MAX_DIMENSION / max(image.size)
    new_size = (int(image.width * ratio), int(image.height * ratio))
    logger.info("Resizing oversized image from %s to %s", image.size, new_size)
    return image.resize(new_size, PILImage.LANCZOS)


def process_and_store_detection(
    user_id: int,
    original_filename: str,
    pil_image: PILImage.Image,
    file_size_bytes: int,
    model_name: str,
    confidence: float,
) -> tuple[DetectionOutcome, int | None]:
    """
    Run detection on an uploaded image, save both the original and annotated
    images to disk, and persist the Image + DetectionResult rows.

    Returns (DetectionOutcome, image_id or None on failure).
    """
    try:
        pil_image = _resize_if_needed(pil_image.convert("RGB"))
        outcome = run_detection(pil_image, model_name=model_name, confidence=confidence)
        if not outcome.success:
            return outcome, None

        stored_name = _safe_filename(original_filename)
        original_path = settings.uploads_dir / stored_name
        pil_image.save(original_path)

        annotated_name = f"annotated_{stored_name}"
        annotated_path = settings.history_dir / annotated_name
        outcome.annotated_image.save(annotated_path)

        with get_session() as session:
            image_row = Image(
                user_id=user_id,
                original_filename=original_filename,
                stored_path=str(original_path),
                annotated_path=str(annotated_path),
                file_size_bytes=file_size_bytes,
                width=pil_image.width,
                height=pil_image.height,
                image_format=pil_image.format or original_filename.rsplit(".", 1)[-1].upper(),
                uploaded_at=dt.datetime.utcnow(),
                processing_time_ms=outcome.processing_time_ms,
                object_count=len(outcome.detections),
                confidence_threshold=confidence,
                model_name=model_name,
            )
            session.add(image_row)
            session.flush()

            for det in outcome.detections:
                session.add(
                    DetectionResult(
                        image_id=image_row.id,
                        class_name=det.class_name,
                        confidence=det.confidence,
                        x_min=det.x_min, y_min=det.y_min, x_max=det.x_max, y_max=det.y_max,
                        box_color=det.color,
                    )
                )
            image_id = image_row.id

        logger.info("Stored detection for user_id=%s image_id=%s objects=%s", user_id, image_id, len(outcome.detections))
        return outcome, image_id
    except Exception as exc:
        logger.exception("Failed to process and store detection.")
        return DetectionOutcome(False, f"Could not save this detection: {exc}"), None


def get_user_history(user_id: int, search: str = "", limit: int = 100) -> list[dict]:
    """Return a user's detection history, newest first, optionally filtered by filename/object."""
    with get_session() as session:
        stmt = select(Image).where(Image.user_id == user_id).order_by(Image.uploaded_at.desc()).limit(limit)
        rows = session.execute(stmt).scalars().all()

        history = []
        for row in rows:
            object_names = [d.class_name for d in row.detections]
            if search:
                haystack = (row.original_filename + " " + " ".join(object_names)).lower()
                if search.lower() not in haystack:
                    continue
            history.append(
                {
                    "id": row.id,
                    "filename": row.original_filename,
                    "annotated_path": row.annotated_path,
                    "stored_path": row.stored_path,
                    "uploaded_at": row.uploaded_at,
                    "object_count": row.object_count,
                    "processing_time_ms": row.processing_time_ms,
                    "objects": object_names,
                }
            )
        return history


def delete_image(user_id: int, image_id: int) -> bool:
    """Delete a single detection record (and its files) belonging to user_id."""
    with get_session() as session:
        row = session.get(Image, image_id)
        if row is None or row.user_id != user_id:
            return False
        for path_str in (row.stored_path, row.annotated_path):
            if path_str:
                Path(path_str).unlink(missing_ok=True)
        session.delete(row)
        return True


def delete_all_history(user_id: int) -> int:
    """Delete every detection record for a user. Returns the number of records removed."""
    with get_session() as session:
        rows = session.execute(select(Image).where(Image.user_id == user_id)).scalars().all()
        count = len(rows)
        for row in rows:
            for path_str in (row.stored_path, row.annotated_path):
                if path_str:
                    Path(path_str).unlink(missing_ok=True)
            session.delete(row)
        return count


def get_dashboard_stats(user_id: int) -> dict:
    """Aggregate stats for a user's dashboard."""
    with get_session() as session:
        total_images = session.execute(
            select(func.count()).select_from(Image).where(Image.user_id == user_id)
        ).scalar_one()
        total_objects = session.execute(
            select(func.coalesce(func.sum(Image.object_count), 0)).where(Image.user_id == user_id)
        ).scalar_one()
        avg_confidence = session.execute(
            select(func.avg(DetectionResult.confidence))
            .join(Image, Image.id == DetectionResult.image_id)
            .where(Image.user_id == user_id)
        ).scalar_one()
        avg_processing = session.execute(
            select(func.avg(Image.processing_time_ms)).where(Image.user_id == user_id)
        ).scalar_one()

        today = dt.datetime.utcnow().date()
        week_start = today - dt.timedelta(days=today.weekday())
        detections_today = session.execute(
            select(func.count()).select_from(Image)
            .where(Image.user_id == user_id, func.date(Image.uploaded_at) == today.isoformat())
        ).scalar_one()
        detections_week = session.execute(
            select(func.count()).select_from(Image)
            .where(Image.user_id == user_id, Image.uploaded_at >= dt.datetime.combine(week_start, dt.time.min))
        ).scalar_one()

        top_object_row = session.execute(
            select(DetectionResult.class_name, func.count().label("cnt"))
            .join(Image, Image.id == DetectionResult.image_id)
            .where(Image.user_id == user_id)
            .group_by(DetectionResult.class_name)
            .order_by(func.count().desc())
            .limit(1)
        ).first()

        recent = session.execute(
            select(Image).where(Image.user_id == user_id).order_by(Image.uploaded_at.desc()).limit(5)
        ).scalars().all()

        return {
            "total_images": total_images or 0,
            "total_objects": int(total_objects or 0),
            "avg_confidence": float(avg_confidence) if avg_confidence is not None else None,
            "avg_processing_ms": float(avg_processing) if avg_processing is not None else None,
            "detections_today": detections_today or 0,
            "detections_week": detections_week or 0,
            "top_object": top_object_row[0] if top_object_row else None,
            "recent": [
                {"filename": r.original_filename, "uploaded_at": r.uploaded_at, "object_count": r.object_count}
                for r in recent
            ],
        }
