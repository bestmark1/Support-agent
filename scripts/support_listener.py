#!/usr/bin/env python3
from __future__ import annotations

import asyncio
import json
import traceback

from telethon import events

from services.telegram_adapter.app.client import create_client
from services.telegram_adapter.app.support_flow import process_support_message


def should_ignore_message(*, message_sender_id: int | None, message_out: bool, self_user_id: int | None) -> bool:
    if message_out:
        return True
    if self_user_id is not None and message_sender_id is not None and int(message_sender_id) == int(self_user_id):
        return True
    return False


async def main() -> int:
    client = create_client()
    await client.connect()
    if not await client.is_user_authorized():
        raise RuntimeError("Telegram session is not authorized. Run the Telethon login first.")
    me = await client.get_me()
    self_user_id = getattr(me, "id", None)

    @client.on(events.NewMessage(incoming=True))
    async def handle_new_message(event: events.NewMessage.Event) -> None:
        try:
            sender_id = getattr(event.message, "sender_id", None)
            if should_ignore_message(
                message_sender_id=sender_id,
                message_out=bool(getattr(event.message, "out", False)),
                self_user_id=self_user_id,
            ):
                print(
                    json.dumps(
                        {
                            "ok": True,
                            "status": "message_ignored",
                            "reason": "self_or_outgoing",
                            "message_id": event.message.id,
                            "sender_id": sender_id,
                        },
                        ensure_ascii=False,
                    ),
                    flush=True,
                )
                return

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
                        "error_type": type(exc).__name__,
                        "error": str(exc),
                        "traceback": traceback.format_exc(),
                        "message_id": getattr(event.message, "id", None),
                        "sender_id": getattr(event.message, "sender_id", None),
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
