from __future__ import annotations

from typing import Any

import httpx

from packages.common.settings.config import get_settings


class EmbeddingClient:
    async def embed(self, text: str) -> list[float]:
        raise NotImplementedError


class OpenAIEmbeddingClient(EmbeddingClient):
    def __init__(self, base_url: str, api_key: str, model: str) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model = model

    async def embed(self, text: str) -> list[float]:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "input": text,
            "model": self.model,
        }
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.base_url}/embeddings",
                headers=headers,
                json=payload,
            )
            response.raise_for_status()
            data: dict[str, Any] = response.json()
            return data["data"][0]["embedding"]


def get_embedding_client() -> EmbeddingClient | None:
    settings = get_settings()
    if settings.embedding_provider == "openai" and settings.embedding_api_key:
        return OpenAIEmbeddingClient(
            base_url=settings.embedding_base_url,
            api_key=settings.embedding_api_key,
            model=settings.embedding_model,
        )
    return None
