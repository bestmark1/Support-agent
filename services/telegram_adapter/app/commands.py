from __future__ import annotations

from typing import Any

from telethon import TelegramClient
from telethon.tl.custom.message import Message


def _message_to_dict(message: Message) -> dict[str, Any]:
    sender = getattr(message, "sender_id", None)
    return {
        "id": message.id,
        "chat_id": message.chat_id,
        "sender_id": sender,
        "text": message.message or "",
        "date": message.date.isoformat() if message.date else None,
        "reply_to_msg_id": message.reply_to_msg_id,
        "out": bool(message.out),
    }


async def telegram_get_me(client: TelegramClient, payload: dict[str, Any]) -> dict[str, Any]:
    del payload
    me = await client.get_me()
    return {
        "id": me.id,
        "username": me.username,
        "first_name": me.first_name,
        "last_name": me.last_name,
        "phone": me.phone,
    }


async def telegram_resolve_peer(
    client: TelegramClient, payload: dict[str, Any]
) -> dict[str, Any]:
    peer = payload["peer"]
    entity = await client.get_entity(peer)
    return {
        "id": entity.id,
        "username": getattr(entity, "username", None),
        "title": getattr(entity, "title", None),
        "first_name": getattr(entity, "first_name", None),
        "last_name": getattr(entity, "last_name", None),
        "is_channel": bool(getattr(entity, "broadcast", False)),
        "is_group": bool(getattr(entity, "megagroup", False)),
    }


async def telegram_get_messages(
    client: TelegramClient, payload: dict[str, Any]
) -> dict[str, Any]:
    peer = payload["peer"]
    limit = int(payload.get("limit", 20))
    messages = await client.get_messages(peer, limit=limit)
    return {"items": [_message_to_dict(message) for message in messages]}


async def telegram_send_message(
    client: TelegramClient, payload: dict[str, Any]
) -> dict[str, Any]:
    message = await client.send_message(payload["peer"], payload["text"])
    return _message_to_dict(message)


async def telegram_reply(client: TelegramClient, payload: dict[str, Any]) -> dict[str, Any]:
    message = await client.send_message(
        payload["peer"],
        payload["text"],
        reply_to=int(payload["reply_to_msg_id"]),
    )
    return _message_to_dict(message)


async def telegram_mark_read(
    client: TelegramClient, payload: dict[str, Any]
) -> dict[str, Any]:
    await client.send_read_acknowledge(
        payload["peer"],
        max_id=int(payload.get("max_id", 0)) or None,
        clear_mentions=bool(payload.get("clear_mentions", True)),
    )
    return {
        "peer": payload["peer"],
        "max_id": int(payload.get("max_id", 0)),
        "clear_mentions": bool(payload.get("clear_mentions", True)),
    }


async def telegram_get_channel_posts(
    client: TelegramClient, payload: dict[str, Any]
) -> dict[str, Any]:
    peer = payload["peer"]
    limit = int(payload.get("limit", 20))
    messages = await client.get_messages(peer, limit=limit)
    items = [item for item in messages if getattr(item, "post", False) or item.chat_id]
    return {"items": [_message_to_dict(message) for message in items]}


COMMANDS = {
    "telegram_get_me": telegram_get_me,
    "telegram_resolve_peer": telegram_resolve_peer,
    "telegram_get_messages": telegram_get_messages,
    "telegram_send_message": telegram_send_message,
    "telegram_reply": telegram_reply,
    "telegram_mark_read": telegram_mark_read,
    "telegram_get_channel_posts": telegram_get_channel_posts,
}
