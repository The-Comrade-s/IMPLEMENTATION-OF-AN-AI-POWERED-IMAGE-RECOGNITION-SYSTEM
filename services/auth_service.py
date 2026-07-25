"""
Authentication business logic: registration, login, password hashing.
Kept separate from Streamlit UI code so it can be tested independently.

Audit-log calls (record_event) are always made AFTER the surrounding
`with get_session()` block has closed and committed. record_event opens its
own session/transaction, and SQLite only allows a single writer at a time —
calling it while an outer write transaction is still open risks a
"database is locked" error, so every write here fully commits first.
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass

import bcrypt
from sqlalchemy import select

from database.db import get_session
from database.models import User
from services.audit_service import record_event
from utils.logger import get_logger
from utils.validators import (
    is_valid_email,
    is_valid_full_name,
    passwords_match,
    validate_password,
)

logger = get_logger(__name__)


@dataclass(frozen=True)
class AuthResult:
    """Outcome of an auth operation, safe to display directly to the user."""

    success: bool
    message: str
    user_id: int | None = None
    full_name: str | None = None
    email: str | None = None
    role: str | None = None


def _hash_password(plain_password: str) -> str:
    return bcrypt.hashpw(plain_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def _verify_password(plain_password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), password_hash.encode("utf-8"))
    except ValueError:
        logger.warning("Encountered a malformed password hash during verification.")
        return False


def hash_password_for_admin(plain_password: str) -> str:
    """Public wrapper so admin flows (e.g. password reset) can hash without reaching into internals."""
    return _hash_password(plain_password)


def register_user(full_name: str, email: str, password: str, confirm_password: str) -> AuthResult:
    """Validate input, prevent duplicate emails, and create a new user with a hashed password."""
    full_name = full_name.strip()
    email = email.strip().lower()

    if not is_valid_full_name(full_name):
        return AuthResult(False, "Please enter your full name (at least 2 characters).")
    if not is_valid_email(email):
        return AuthResult(False, "Please enter a valid email address.")

    password_ok, password_message = validate_password(password)
    if not password_ok:
        return AuthResult(False, password_message)
    if not passwords_match(password, confirm_password):
        return AuthResult(False, "Passwords do not match.")

    try:
        with get_session() as session:
            existing = session.execute(select(User).where(User.email == email)).scalar_one_or_none()
            if existing is not None:
                return AuthResult(False, "An account with this email already exists.")

            user = User(
                full_name=full_name,
                email=email,
                password_hash=_hash_password(password),
                role="user",
                is_active=True,
            )
            session.add(user)
            session.flush()
            new_user_id = user.id
            result = AuthResult(
                True,
                "Account created successfully. You can now log in.",
                user_id=user.id,
                full_name=user.full_name,
                email=user.email,
                role=user.role,
            )
        # Session has committed by this point — safe to write a separate audit entry.
        logger.info("New user registered: %s", email)
        record_event("user_registered", f"email={email}", user_id=new_user_id)
        return result
    except Exception:
        logger.exception("Registration failed unexpectedly for email=%s", email)
        return AuthResult(False, "Something went wrong while creating your account. Please try again.")


def login_user(email: str, password: str) -> AuthResult:
    """Verify credentials and return an AuthResult usable to populate the session state."""
    email = email.strip().lower()

    if not email or not password:
        return AuthResult(False, "Please enter both email and password.")

    try:
        with get_session() as session:
            user = session.execute(select(User).where(User.email == email)).scalar_one_or_none()

            if user is None or not _verify_password(password, user.password_hash):
                outcome = ("login_failed", f"email={email}", None, "WARNING")
                result = AuthResult(False, "Invalid email or password.")
            elif not user.is_active:
                outcome = ("login_blocked_inactive", f"email={email}", user.id, "WARNING")
                result = AuthResult(False, "This account has been deactivated. Contact an administrator.")
            else:
                user.last_login = dt.datetime.utcnow()
                session.add(user)
                session.flush()
                outcome = ("user_login", f"email={email}", user.id, "INFO")
                result = AuthResult(
                    True,
                    f"Welcome back, {user.full_name}!",
                    user_id=user.id,
                    full_name=user.full_name,
                    email=user.email,
                    role=user.role,
                )

        # Session has committed by this point — safe to write a separate audit entry.
        action, details, actor_id, level = outcome
        logger.info("%s: %s", action, email)
        record_event(action, details, user_id=actor_id, level=level)
        return result
    except Exception:
        logger.exception("Login failed unexpectedly for email=%s", email)
        return AuthResult(False, "Something went wrong while logging in. Please try again.")


def change_password(user_id: int, current_password: str, new_password: str, confirm_password: str) -> AuthResult:
    """Change a logged-in user's password after verifying their current one."""
    password_ok, password_message = validate_password(new_password)
    if not password_ok:
        return AuthResult(False, password_message)
    if not passwords_match(new_password, confirm_password):
        return AuthResult(False, "New passwords do not match.")

    try:
        with get_session() as session:
            user = session.get(User, user_id)
            if user is None:
                return AuthResult(False, "User not found.")
            if not _verify_password(current_password, user.password_hash):
                return AuthResult(False, "Current password is incorrect.")

            user.password_hash = _hash_password(new_password)
            session.add(user)

        # Session has committed by this point — safe to write a separate audit entry.
        logger.info("Password changed for user_id=%s", user_id)
        record_event("password_changed", user_id=user_id)
        return AuthResult(True, "Password updated successfully.")
    except Exception:
        logger.exception("Password change failed for user_id=%s", user_id)
        return AuthResult(False, "Something went wrong while updating your password.")
