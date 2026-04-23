from __future__ import annotations

from typing import Any

from telethon import functions
from telethon import TelegramClient

from services.partnership_research.app.services.leads import score_lead

DEFAULT_OUTREACH_QUERIES = ["питание", "похудение", "ПП", "калории", "ЗОЖ"]

QUERY_EXPANSIONS: dict[str, list[str]] = {
    "правильное питание": [
        "правильное питание",
        "пп",
        "пп рецепты",
        "полезное питание",
        "кбжу",
        "рацион",
        "меню на день",
    ],
    "питание": [
        "питание",
        "правильное питание",
        "пп",
        "пп рецепты",
        "полезное питание",
        "рацион",
        "кбжу",
    ],
    "похудение": [
        "похудение",
        "худеем",
        "худеем вместе",
        "снижение веса",
        "дефицит калорий",
        "марафон похудения",
        "похудение без срывов",
    ],
    "зож": [
        "зож",
        "здоровый образ жизни",
        "правильное питание",
        "полезные привычки",
        "wellness",
    ],
    "нутрициология": [
        "нутрициолог",
        "нутрициология",
        "диетолог",
        "рацион",
        "питание",
    ],
    "нутрициолог": [
        "нутрициолог",
        "нутрициология",
        "диетолог",
        "рацион",
        "питание",
    ],
    "кбжу": [
        "кбжу",
        "калории",
        "дефицит калорий",
        "рацион",
        "пп рецепты",
    ],
    "калории": [
        "калории",
        "кбжу",
        "дефицит калорий",
        "похудение",
        "рацион",
    ],
}


def expand_outreach_queries(queries: list[str]) -> list[str]:
    expanded: list[str] = []
    seen: set[str] = set()

    for query in queries:
        normalized = " ".join(str(query).strip().lower().split())
        if not normalized:
            continue

        candidates = QUERY_EXPANSIONS.get(normalized)
        if candidates is None:
            candidates = [normalized]
            for key, values in QUERY_EXPANSIONS.items():
                if normalized in key or key in normalized:
                    candidates.extend(values)

        for candidate in candidates:
            cleaned = " ".join(candidate.strip().split())
            lowered = cleaned.lower()
            if not cleaned or lowered in seen:
                continue
            seen.add(lowered)
            expanded.append(cleaned)

    return expanded or list(DEFAULT_OUTREACH_QUERIES)


def _entity_type(entity: Any) -> str:
    if bool(getattr(entity, "broadcast", False)):
        return "channel"
    if bool(getattr(entity, "megagroup", False)) or bool(getattr(entity, "gigagroup", False)):
        return "chat"
    return "other"


def _build_link(username: str | None) -> str | None:
    if not username:
        return None
    return f"https://t.me/{username}"


async def _recent_text(client: TelegramClient, entity: Any, limit: int) -> tuple[list[dict[str, Any]], str]:
    messages = await client.get_messages(entity, limit=limit)
    items: list[dict[str, Any]] = []
    text_parts: list[str] = []
    for message in messages:
        text = (message.message or "").strip()
        if not text:
            continue
        items.append(
            {
                "id": message.id,
                "date": message.date.isoformat() if message.date else None,
                "text": text[:500],
            }
        )
        text_parts.append(text)
    return items, "\n".join(text_parts)


async def search_telegram_outreach(
    client: TelegramClient,
    *,
    queries: list[str],
    limit_per_query: int,
    post_limit: int,
) -> dict[str, Any]:
    expanded_queries = expand_outreach_queries(queries)
    results: dict[int, dict[str, Any]] = {}
    for query in expanded_queries:
        response = await client(functions.contacts.SearchRequest(q=query, limit=limit_per_query))
        for chat in response.chats:
            entity_type = _entity_type(chat)
            if entity_type not in {"channel", "chat"}:
                continue

            entity_id = int(chat.id)
            if entity_id in results:
                results[entity_id]["matched_queries"].append(query)
                continue

            recent_posts, recent_text = await _recent_text(client, chat, post_limit)
            lead = {
                "id": entity_id,
                "title": getattr(chat, "title", None),
                "description": getattr(chat, "about", None) or "",
                "type": entity_type,
                "username": getattr(chat, "username", None),
                "link": _build_link(getattr(chat, "username", None)),
                "member_count": getattr(chat, "participants_count", None) or 0,
                "recent_posts_count": len(recent_posts),
                "recent_posts": recent_posts,
                "recent_text": recent_text,
                "matched_queries": [query],
            }
            lead.update(score_lead(lead))
            results[entity_id] = lead

    shortlist = sorted(
        results.values(),
        key=lambda item: (float(item.get("score") or 0.0), int(item.get("member_count") or 0)),
        reverse=True,
    )
    return {
        "queries": expanded_queries,
        "total_found": len(shortlist),
        "shortlist": shortlist,
    }
