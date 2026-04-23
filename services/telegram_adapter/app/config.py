from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class TelegramAdapterSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    telegram_api_id: int = 0
    telegram_api_hash: str = ""
    telegram_phone: str = ""
    telegram_session_path: str = ".secrets/telethon_support.session"
    telegram_session_name: str = "fitmentor-support"
    telegram_owner_user_id: int | None = Field(default=None)
    telegram_test_user_ids: str = ""
    fitmentor_internal_base_url: str = ""
    fitmentor_support_internal_token: str = ""

    @property
    def session_path(self) -> Path:
        return Path(self.telegram_session_path).expanduser().resolve()

    def is_trusted_operator(self, user_id: int | None) -> bool:
        if user_id is None or self.telegram_owner_user_id is None:
            return False
        return int(user_id) == int(self.telegram_owner_user_id)

    @property
    def test_user_ids(self) -> set[int]:
        values: set[int] = set()
        for raw in self.telegram_test_user_ids.split(","):
            candidate = raw.strip()
            if not candidate:
                continue
            try:
                values.add(int(candidate))
            except ValueError:
                continue
        return values

    def is_test_user(self, user_id: int | None) -> bool:
        if user_id is None:
            return False
        return int(user_id) in self.test_user_ids


@lru_cache(maxsize=1)
def get_telegram_settings() -> TelegramAdapterSettings:
    return TelegramAdapterSettings()
