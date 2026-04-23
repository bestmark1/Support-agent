#!/usr/bin/env python3
from __future__ import annotations

import argparse
import asyncio
import json
from telethon.tl.custom.message import Message

from services.telegram_adapter.app.client import create_client
from services.telegram_adapter.app.commands import (
    telegram_get_messages,
)
from services.telegram_adapter.app.support_flow import process_support_message


def choose_latest_inbound(items: list[dict[str, Any]]) -> dict[str, Any] | None:
    inbound = [item for item in items if not item.get("out") and (item.get("text") or "").strip()]
    if not inbound:
        return None
    inbound.sort(key=lambda item: int(item.get("id") or 0))
    return inbound[-1]


async def run_once(peer: str, limit: int, send: bool) -> int:
    tg_client = create_client()
    await tg_client.connect()
    if not await tg_client.is_user_authorized():
        raise RuntimeError("Telegram session is not authorized. Run the Telethon login first.")

    try:
        result = await telegram_get_messages(tg_client, {"peer": peer, "limit": limit})
        message = choose_latest_inbound(result["items"])
        if message is None:
            print(
                json.dumps(
                    {"ok": True, "status": "no_inbound_messages", "peer": peer},
                    ensure_ascii=False,
                )
            )
            return 0

        pseudo_message = Message.__new__(Message)
        pseudo_message.id = int(message["id"])
        pseudo_message.chat_id = message.get("chat_id")
        pseudo_message.sender_id = message.get("sender_id")
        pseudo_message.message = message.get("text") or ""
        pseudo_message.out = bool(message.get("out"))
        pseudo_message.chat = None
        result = await process_support_message(
            tg_client,
            pseudo_message,
            send=send,
            source="support_loop_run_once",
        )
        print(json.dumps(result, ensure_ascii=False))
        return 0
    finally:
        await tg_client.disconnect()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run one support-loop pass for a Telegram peer.")
    parser.add_argument("--peer", required=True, help="Telegram peer identifier, username, or chat id")
    parser.add_argument("--limit", type=int, default=20, help="How many recent messages to inspect")
    parser.add_argument(
        "--send",
        action="store_true",
        help="Actually send the reply. Without this flag the script only drafts/logs.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    return asyncio.run(run_once(peer=args.peer, limit=args.limit, send=args.send))


if __name__ == "__main__":
    raise SystemExit(main())
