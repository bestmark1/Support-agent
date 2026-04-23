from __future__ import annotations

from pathlib import Path

from telethon import TelegramClient

from services.telegram_adapter.app.config import get_telegram_settings


def create_client() -> TelegramClient:
    settings = get_telegram_settings()
    if settings.telegram_api_id <= 0:
        raise ValueError("TELEGRAM_API_ID must be configured")
    if not settings.telegram_api_hash:
        raise ValueError("TELEGRAM_API_HASH must be configured")

    session_path: Path = settings.session_path
    session_path.parent.mkdir(parents=True, exist_ok=True)

    return TelegramClient(
        str(session_path),
        settings.telegram_api_id,
        settings.telegram_api_hash,
        device_model="FitMentor Telegram Adapter",
        system_version="Linux",
        app_version="0.1.0",
    )
