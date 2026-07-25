"""
Reusable input validation helpers for forms across the application.
"""
from __future__ import annotations

import re

from config.config import settings

EMAIL_PATTERN = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")


def is_valid_email(email: str) -> bool:
    """Check that the email has a valid, well-formed structure."""
    return bool(email) and bool(EMAIL_PATTERN.match(email.strip()))


def is_valid_full_name(name: str) -> bool:
    """Require a non-trivial name with at least two characters."""
    return bool(name) and len(name.strip()) >= 2


def validate_password(password: str) -> tuple[bool, str]:
    """
    Validate password strength.

    Returns:
        (is_valid, message) where message explains the failure if any.
    """
    if not password or len(password) < settings.min_password_length:
        return False, f"Password must be at least {settings.min_password_length} characters long."
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter."
    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter."
    if not re.search(r"\d", password):
        return False, "Password must contain at least one number."
    return True, ""


def passwords_match(password: str, confirm_password: str) -> bool:
    return password == confirm_password
