#!/usr/bin/env python3
"""Narrow CLI bridge from OpenCrabs shell tools to kb_api HTTP endpoints."""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from typing import Any


KB_API_BASE_URL = os.environ.get("KB_API_BASE_URL", "http://127.0.0.1:8010").rstrip("/")


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
        raise ValueError("Expected JSON payload on stdin")
    data = json.loads(raw)
    if not isinstance(data, dict):
        raise ValueError("Expected JSON object payload on stdin")
    return data


def http_json(method: str, path: str, payload: dict[str, Any] | None = None) -> Any:
    url = f"{KB_API_BASE_URL}{path}"
    body: bytes | None = None
    headers = {"Accept": "application/json"}
    if payload is not None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        headers["Content-Type"] = "application/json"
    request = urllib.request.Request(url=url, data=body, headers=headers, method=method.upper())
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            text = response.read().decode("utf-8")
            return json.loads(text) if text else {}
    except urllib.error.HTTPError as exc:
        try:
            details = exc.read().decode("utf-8")
            parsed = json.loads(details) if details else None
        except Exception:
            parsed = details if "details" in locals() else None
        raise RuntimeError(
            json.dumps(
                {
                    "status": exc.code,
                    "reason": exc.reason,
                    "body": parsed,
                },
                ensure_ascii=False,
            )
        ) from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"kb_api unreachable: {exc.reason}") from exc


def handle_search_knowledge() -> int:
    payload = load_stdin_json()
    query = str(payload["query"])
    limit = int(payload.get("limit", 5))
    params: dict[str, Any] = {"query": query, "limit": limit}
    if payload.get("language"):
        params["language"] = str(payload["language"])
    path = f"/kb/search?{urllib.parse.urlencode(params)}"
    return success(http_json("GET", path))


def handle_create_proposed_update() -> int:
    return success(http_json("POST", "/kb/proposed-updates", load_stdin_json()))


def handle_ensure_support_thread() -> int:
    return success(http_json("POST", "/kb/support-threads", load_stdin_json()))


def handle_log_support_message() -> int:
    return success(http_json("POST", "/kb/support-messages", load_stdin_json()))


COMMANDS = {
    "search_knowledge": handle_search_knowledge,
    "create_proposed_update": handle_create_proposed_update,
    "ensure_support_thread": handle_ensure_support_thread,
    "log_support_message": handle_log_support_message,
}


def main() -> int:
    if len(sys.argv) != 2 or sys.argv[1] not in COMMANDS:
        return fail(
            "Usage: opencrabs_kb_bridge.py <search_knowledge|create_proposed_update|ensure_support_thread|log_support_message>"
        )
    try:
        return COMMANDS[sys.argv[1]]()
    except KeyError as exc:
        return fail(f"Missing required field: {exc.args[0]}")
    except ValueError as exc:
        return fail(str(exc))
    except RuntimeError as exc:
        details: Any
        try:
            details = json.loads(str(exc))
        except json.JSONDecodeError:
            details = str(exc)
        return fail("kb_api request failed", details=details)
    except json.JSONDecodeError as exc:
        return fail(f"Invalid JSON payload: {exc}")


if __name__ == "__main__":
    raise SystemExit(main())
