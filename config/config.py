"""
Application configuration.
Loads environment variables and exposes typed settings used across the app.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


@dataclass(frozen=True)
class Settings:
    """Central, immutable application settings."""

    app_name: str = os.getenv("APP_NAME", "AI-Powered Image Recognition System")
    app_icon: str = os.getenv("APP_ICON", "🧠")
    secret_key: str = os.getenv("SECRET_KEY", "dev-secret-change-me")
    database_path: Path = BASE_DIR / "database" / "airs.db"
    database_url: str = f"sqlite:///{BASE_DIR / 'database' / 'airs.db'}"
    uploads_dir: Path = BASE_DIR / "uploads"
    history_dir: Path = BASE_DIR / "history"
    logs_dir: Path = BASE_DIR / "logs"
    assets_dir: Path = BASE_DIR / "assets"
    css_path: Path = BASE_DIR / "css" / "style.css"
    session_timeout_minutes: int = int(os.getenv("SESSION_TIMEOUT_MINUTES", "60"))
    min_password_length: int = 8
    log_level: str = os.getenv("LOG_LEVEL", "INFO")

    def ensure_directories(self) -> None:
        for directory in (self.uploads_dir, self.history_dir, self.logs_dir, self.database_path.parent):
            directory.mkdir(parents=True, exist_ok=True)


settings = Settings()
settings.ensure_directories()
