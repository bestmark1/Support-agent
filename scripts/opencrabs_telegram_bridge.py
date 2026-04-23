#!/usr/bin/env python3
"""Narrow OpenCrabs bridge for a real-user Telegram account via Telethon."""

from __future__ import annotations

import asyncio
import json
import sys
from typing import Any

from services.telegram_adapter.app.client import create_client
from services.telegram_adapter.app.commands import COMMANDS


def fail(message: str, *, details: Any | None = None, status_code: int = 1) -> int:
    payload: dict[str, Any] = {"ok": False, "error": message}
    if details is not None:
        payload["details"] = details
    print(json.dumps(payload, ensure_ascii=False))
    return status_code


def success(payload: Any) -> int:
    print(json.dumps({"ok": True, "result": payload}, ensure_ascii=False))
    return 0


def load_stdin_json() -> dict[str, Any]:
    raw = sys.stdin.read()
    if not raw.strip():
        return {}
    payload = json.loads(raw)
    if not isinstance(payload, dict):
        raise ValueError("Expected JSON object payload on stdin")
    return payload


async def run_command(name: str, payload: dict[str, Any]) -> Any:
    client = create_client()
    await client.connect()
    try:
        if not await client.is_user_authorized():
            raise RuntimeError(
                "Telegram session is not authorized. Run `python3 -m services.telegram_adapter.app.login` first."
            )
        command = COMMANDS[name]
        return await command(client, payload)
    finally:
        await client.disconnect()


def main() -> int:
    if len(sys.argv) != 2 or sys.argv[1] not in COMMANDS:
        return fail(
            "Usage: opencrabs_telegram_bridge.py <telegram_get_me|telegram_resolve_peer|telegram_get_messages|telegram_send_message|telegram_reply|telegram_mark_read|telegram_get_channel_posts>"
        )

    try:
        payload = load_stdin_json()
        result = asyncio.run(run_command(sys.argv[1], payload))
        return success(result)
    except KeyError as exc:
        return fail(f"Missing required field: {exc.args[0]}")
    except ValueError as exc:
        return fail(str(exc))
    except Exception as exc:
        return fail("telegram adapter request failed", details=str(exc))


if __name__ == "__main__":
    raise SystemExit(main())
