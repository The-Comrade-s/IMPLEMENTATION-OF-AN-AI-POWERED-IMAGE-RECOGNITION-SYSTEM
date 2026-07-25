"""
Unit tests for dependency-light business logic: input validation, upload
validation, and the YOLO annotation-drawing helper. These do not touch the
database, so they run fast and don't require a YOLO model download.

Run with:
    pytest tests/test_core_logic.py -v
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PIL import Image

from ai.yolo_service import Detection, draw_boxes, _color_for_class
from services.image_service import MAX_FILE_SIZE_BYTES, _resize_if_needed, validate_upload
from utils.validators import is_valid_email, is_valid_full_name, passwords_match, validate_password


class TestValidators:
    def test_valid_email_accepted(self):
        assert is_valid_email("user@example.com") is True

    def test_invalid_email_rejected(self):
        assert is_valid_email("not-an-email") is False
        assert is_valid_email("") is False

    def test_full_name_minimum_length(self):
        assert is_valid_full_name("Jo") is True
        assert is_valid_full_name("J") is False
        assert is_valid_full_name("") is False

    def test_password_strength_rules(self):
        ok, _ = validate_password("weak")
        assert ok is False
        ok, _ = validate_password("alllowercase1")
        assert ok is False
        ok, _ = validate_password("StrongPass1")
        assert ok is True

    def test_passwords_match(self):
        assert passwords_match("abc", "abc") is True
        assert passwords_match("abc", "abd") is False


class TestUploadValidation:
    def test_accepts_supported_extensions(self):
        for ext in ("jpg", "jpeg", "png", "bmp", "webp"):
            assert validate_upload(f"photo.{ext}", 1000).ok is True

    def test_rejects_unsupported_extension(self):
        assert validate_upload("malware.exe", 1000).ok is False

    def test_rejects_empty_file(self):
        assert validate_upload("photo.jpg", 0).ok is False

    def test_rejects_oversized_file(self):
        assert validate_upload("photo.jpg", MAX_FILE_SIZE_BYTES + 1).ok is False


class TestImageResizing:
    def test_large_image_is_downscaled(self):
        big = Image.new("RGB", (5000, 3000))
        resized = _resize_if_needed(big)
        assert max(resized.size) <= 4000

    def test_small_image_is_unchanged(self):
        small = Image.new("RGB", (100, 100))
        assert _resize_if_needed(small).size == (100, 100)


class TestYoloDrawing:
    def test_draw_boxes_preserves_image_size(self):
        image = Image.new("RGB", (200, 200), color="white")
        detections = [
            Detection("cat", 0.87, 20, 20, 100, 100),
            Detection("dog", 0.55, 50, 50, 180, 180),
        ]
        annotated = draw_boxes(image, detections)
        assert annotated.size == (200, 200)

    def test_draw_boxes_handles_no_detections(self):
        image = Image.new("RGB", (100, 100))
        annotated = draw_boxes(image, [])
        assert annotated.size == (100, 100)

    def test_color_assignment_is_deterministic(self):
        assert _color_for_class("cat") == _color_for_class("cat")
