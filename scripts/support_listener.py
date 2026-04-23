#!/usr/bin/env python3
from __future__ import annotations

import asyncio
import json

from telethon import events

from services.telegram_adapter.app.client import create_client
from services.telegram_adapter.app.support_flow import process_support_message


async def main() -> int:
    client = create_client()
    await client.connect()
    if not await client.is_user_authorized():
        raise RuntimeError("Telegram session is not authorized. Run the Telethon login first.")

    @client.on(events.NewMessage(incoming=True))
    async def handle_new_message(event: events.NewMessage.Event) -> None:
        try:
            result = await process_support_message(
                client,
                event.message,
                send=True,
                source="support_listener",
            )
            print(json.dumps(result, ensure_ascii=False), flush=True)
        except Exception as exc:  # pragma: no cover
            print(
                json.dumps(
                    {
                        "ok": False,
                        "status": "listener_error",
                        "error": str(exc),
                    },
                    ensure_ascii=False,
                ),
                flush=True,
            )

    print(
        json.dumps(
            {
                "ok": True,
                "status": "listener_started",
            },
            ensure_ascii=False,
        ),
        flush=True,
    )
    await client.run_until_disconnected()
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
