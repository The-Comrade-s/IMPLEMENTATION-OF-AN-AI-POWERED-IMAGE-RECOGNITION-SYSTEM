"""
YOLOv11 inference engine.

Wraps Ultralytics YOLO with Streamlit's resource cache so the model is loaded
into memory once per process, not on every rerun. Falls back gracefully with
a user-friendly error if the model or its dependencies are unavailable.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field

import numpy as np
import streamlit as st
from PIL import Image as PILImage, ImageDraw, ImageFont

from utils.logger import get_logger

logger = get_logger(__name__)

AVAILABLE_MODELS = {
    "Nano (fastest)": "yolo11n.pt",
    "Small (balanced)": "yolo11s.pt",
    "Medium (accurate)": "yolo11m.pt",
    "Large (most accurate)": "yolo11l.pt",
}

# Deterministic, readable palette so the same class always gets the same colour.
_PALETTE = [
    "#2952e3", "#12b981", "#f59e0b", "#ef4444", "#8b5cf6",
    "#06b6d4", "#ec4899", "#84cc16", "#f97316", "#0ea5e9",
]


@dataclass
class Detection:
    class_name: str
    confidence: float
    x_min: float
    y_min: float
    x_max: float
    y_max: float
    color: str = "#2952e3"


@dataclass
class DetectionOutcome:
    success: bool
    message: str = ""
    detections: list[Detection] = field(default_factory=list)
    annotated_image: "PILImage.Image | None" = None
    processing_time_ms: float = 0.0


def _color_for_class(class_name: str) -> str:
    index = abs(hash(class_name)) % len(_PALETTE)
    return _PALETTE[index]


@st.cache_resource(show_spinner=False)
def load_model(model_name: str = "yolo11n.pt"):
    """
    Load (and cache) a YOLOv11 model. Ultralytics auto-downloads weights on
    first use if they are not already present locally.
    """
    from ultralytics import YOLO  # imported lazily so the rest of the app works without it installed

    logger.info("Loading YOLO model: %s", model_name)
    return YOLO(model_name)


def is_model_available(model_name: str = "yolo11n.pt") -> tuple[bool, str]:
    """Attempt to load the model, returning (ok, error_message)."""
    try:
        load_model(model_name)
        return True, ""
    except Exception as exc:  # pragma: no cover - depends on environment/network
        logger.exception("YOLO model failed to load: %s", model_name)
        return False, str(exc)


def run_detection(image: "PILImage.Image", model_name: str = "yolo11n.pt", confidence: float = 0.25) -> DetectionOutcome:
    """Run YOLOv11 inference on a PIL image and return detections + an annotated copy."""
    start = time.perf_counter()
    try:
        model = load_model(model_name)
        results = model.predict(source=np.array(image.convert("RGB")), conf=confidence, verbose=False)
        result = results[0]

        detections: list[Detection] = []
        names = result.names
        for box in result.boxes:
            cls_id = int(box.cls[0])
            class_name = names.get(cls_id, str(cls_id)) if isinstance(names, dict) else names[cls_id]
            conf = float(box.conf[0])
            x1, y1, x2, y2 = [float(v) for v in box.xyxy[0]]
            detections.append(
                Detection(
                    class_name=class_name,
                    confidence=conf,
                    x_min=x1, y_min=y1, x_max=x2, y_max=y2,
                    color=_color_for_class(class_name),
                )
            )

        annotated = draw_boxes(image, detections)
        elapsed_ms = (time.perf_counter() - start) * 1000

        return DetectionOutcome(
            success=True,
            detections=detections,
            annotated_image=annotated,
            processing_time_ms=elapsed_ms,
        )
    except MemoryError:
        logger.exception("Out of memory during YOLO inference.")
        return DetectionOutcome(False, "The image is too large to process with available memory. Try a smaller image.")
    except Exception as exc:
        logger.exception("YOLO inference failed.")
        return DetectionOutcome(False, f"Detection failed: {exc}")


def draw_boxes(image: "PILImage.Image", detections: list[Detection]) -> "PILImage.Image":
    """Draw bounding boxes, labels, and confidence scores onto a copy of the image."""
    annotated = image.convert("RGB").copy()
    draw = ImageDraw.Draw(annotated)

    try:
        font = ImageFont.load_default(size=16)
    except TypeError:
        font = ImageFont.load_default()

    for det in detections:
        draw.rectangle([det.x_min, det.y_min, det.x_max, det.y_max], outline=det.color, width=3)
        label = f"{det.class_name} {det.confidence:.0%}"
        text_bbox = draw.textbbox((0, 0), label, font=font)
        text_w, text_h = text_bbox[2] - text_bbox[0], text_bbox[3] - text_bbox[1]
        draw.rectangle(
            [det.x_min, max(0, det.y_min - text_h - 8), det.x_min + text_w + 10, det.y_min],
            fill=det.color,
        )
        draw.text((det.x_min + 5, max(0, det.y_min - text_h - 6)), label, fill="white", font=font)

    return annotated
