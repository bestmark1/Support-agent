from __future__ import annotations

import httpx

from packages.common.settings.config import get_settings
from services.support_agent.app.services.types import KnowledgeItem


def _kb_api_base_url() -> str:
    settings = get_settings()
    return settings.kb_api_base_url.rstrip("/")


async def create_proposed_update_via_api(
    source: str,
    suggested_category: str,
    suggested_title: str,
    suggested_content: str,
    reason: str,
    evidence: dict[str, object] | None = None,
) -> dict[str, str]:
    payload = {
        "source": source,
        "suggested_category": suggested_category,
        "suggested_title": suggested_title,
        "suggested_content": suggested_content,
        "reason": reason,
        "evidence": evidence or {},
    }
    async with httpx.AsyncClient(timeout=20.0) as client:
        response = await client.post(
            f"{_kb_api_base_url()}/kb/proposed-updates",
            json=payload,
        )
        response.raise_for_status()
        return response.json()


async def search_approved_knowledge_via_api(
    query: str,
    limit: int = 5,
) -> list[KnowledgeItem]:
    async with httpx.AsyncClient(timeout=20.0) as client:
        response = await client.get(
            f"{_kb_api_base_url()}/kb/search",
            params={"query": query, "limit": limit},
        )
        response.raise_for_status()
        payload = response.json()
        return payload.get("items", [])


async def ensure_support_thread_via_api(
    telegram_user_id: str,
    telegram_chat_id: str,
) -> str:
    async with httpx.AsyncClient(timeout=20.0) as client:
        response = await client.post(
            f"{_kb_api_base_url()}/kb/support-threads",
            json={
                "telegram_user_id": telegram_user_id,
                "telegram_chat_id": telegram_chat_id,
            },
        )
        response.raise_for_status()
        payload = response.json()
        return payload["thread_id"]


async def log_support_message_via_api(
    thread_id: str,
    role: str,
    message_text: str,
    retrieval_context: list[KnowledgeItem] | None = None,
) -> str:
    async with httpx.AsyncClient(timeout=20.0) as client:
        response = await client.post(
            f"{_kb_api_base_url()}/kb/support-messages",
            json={
                "thread_id": thread_id,
                "role": role,
                "message_text": message_text,
                "retrieval_context": retrieval_context or [],
            },
        )
        response.raise_for_status()
        payload = response.json()
        return payload["message_id"]
