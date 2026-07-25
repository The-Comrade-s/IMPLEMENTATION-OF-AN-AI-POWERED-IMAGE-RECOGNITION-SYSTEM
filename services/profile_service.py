"""
Profile management: editing display name and avatar, separate from
credential changes which stay in auth_service.
"""
from __future__ import annotations

import uuid
from pathlib import Path

from PIL import Image as PILImage

from config.config import settings
from database.db import get_session
from database.models import User
from utils.logger import get_logger
from utils.validators import is_valid_full_name

logger = get_logger(__name__)

AVATAR_DIR = settings.assets_dir / "avatars"
AVATAR_DIR.mkdir(parents=True, exist_ok=True)


def update_full_name(user_id: int, new_full_name: str) -> tuple[bool, str]:
    if not is_valid_full_name(new_full_name):
        return False, "Please enter a valid name (at least 2 characters)."
    try:
        with get_session() as session:
            user = session.get(User, user_id)
            if user is None:
                return False, "User not found."
            user.full_name = new_full_name.strip()
            session.add(user)
        return True, "Name updated successfully."
    except Exception:
        logger.exception("Failed to update full name for user_id=%s", user_id)
        return False, "Something went wrong while updating your name."


def update_avatar(user_id: int, pil_image: PILImage.Image) -> tuple[bool, str]:
    try:
        pil_image = pil_image.convert("RGB")
        pil_image.thumbnail((256, 256))
        filename = f"{user_id}_{uuid.uuid4().hex[:8]}.jpg"
        path = AVATAR_DIR / filename
        pil_image.save(path, format="JPEG", quality=88)

        with get_session() as session:
            user = session.get(User, user_id)
            if user is None:
                return False, "User not found."
            old_avatar = user.avatar_path
            user.avatar_path = str(path)
            session.add(user)

        if old_avatar:
            Path(old_avatar).unlink(missing_ok=True)

        return True, "Profile picture updated."
    except Exception:
        logger.exception("Failed to update avatar for user_id=%s", user_id)
        return False, "Something went wrong while uploading your profile picture."
