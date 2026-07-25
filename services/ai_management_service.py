"""
Admin-configurable, system-wide AI settings (active model, default confidence
threshold). Stored as JSON rather than a DB table since it is a single
config record, not a per-row entity — keeps schema changes minimal.
"""
from __future__ import annotations

import json
import time
from pathlib import Path

from ai.yolo_service import AVAILABLE_MODELS, is_model_available
from config.config import settings
from services.audit_service import record_event
from utils.logger import get_logger

logger = get_logger(__name__)

_CONFIG_PATH = settings.database_path.parent / "ai_config.json"
_DEFAULTS = {"model_name": "yolo11n.pt", "confidence_threshold": 0.25, "last_reload": None}


def _read() -> dict:
    if not _CONFIG_PATH.exists():
        _write(_DEFAULTS)
        return dict(_DEFAULTS)
    try:
        return {**_DEFAULTS, **json.loads(_CONFIG_PATH.read_text())}
    except Exception:
        logger.exception("Failed to read AI config; falling back to defaults.")
        return dict(_DEFAULTS)


def _write(data: dict) -> None:
    _CONFIG_PATH.write_text(json.dumps(data, indent=2, default=str))


def get_ai_config() -> dict:
    return _read()


def update_ai_config(model_name: str | None = None, confidence_threshold: float | None = None, admin_id: int | None = None) -> tuple[bool, str]:
    config = _read()
    if model_name and model_name not in AVAILABLE_MODELS.values():
        return False, "Unknown model."
    if confidence_threshold is not None and not (0.0 < confidence_threshold <= 1.0):
        return False, "Confidence threshold must be between 0 and 1."

    if model_name:
        config["model_name"] = model_name
    if confidence_threshold is not None:
        config["confidence_threshold"] = confidence_threshold
    _write(config)
    record_event("ai_config_updated", str(config), user_id=admin_id)
    return True, "AI configuration updated."


def reload_model(admin_id: int | None = None) -> tuple[bool, str]:
    config = _read()
    from ai.yolo_service import load_model

    try:
        load_model.clear()  # clear Streamlit's cache_resource so the model reloads fresh
    except Exception:
        pass
    ok, error = is_model_available(config["model_name"])
    config["last_reload"] = time.strftime("%Y-%m-%d %H:%M:%S")
    _write(config)
    record_event("ai_model_reloaded", f"model={config['model_name']} ok={ok}", user_id=admin_id)
    return (True, "Model reloaded successfully.") if ok else (False, f"Model reload failed: {error}")


def test_model(admin_id: int | None = None) -> tuple[bool, str]:
    config = _read()
    ok, error = is_model_available(config["model_name"])
    record_event("ai_model_tested", f"model={config['model_name']} ok={ok}", user_id=admin_id)
    return (True, "Model is loaded and healthy.") if ok else (False, f"Model health check failed: {error}")
