from __future__ import annotations

from typing import Any

import httpx

from packages.common.settings.config import get_settings


class AIGatewayClient:
    def __init__(self) -> None:
        settings = get_settings()
        self.base_url = settings.ai_gateway_base_url.rstrip("/")
        self.api_key = settings.ai_gateway_api_key
        self.model = settings.ai_gateway_model
        self.timeout = settings.ai_gateway_timeout_seconds

    @property
    def enabled(self) -> bool:
        return bool(self.base_url and self.api_key and self.model)

    async def generate_reply(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> str:
        if not self.enabled:
            raise RuntimeError("AI gateway is not configured.")

        payload = {
            "model": self.model,
            "system": system_prompt,
            "messages": [
                {
                    "role": "user",
                    "content": user_prompt,
                }
            ],
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/messages",
                headers=headers,
                json=payload,
            )
            response.raise_for_status()
            data: dict[str, Any] = response.json()

        content = data.get("content", [])
        if isinstance(content, list):
            parts = [
                item.get("text", "")
                for item in content
                if isinstance(item, dict) and item.get("type") == "text"
            ]
            return "\n".join(part for part in parts if part).strip()

        if isinstance(content, str):
            return content.strip()

        raise RuntimeError("AI gateway returned an unsupported response shape.")
