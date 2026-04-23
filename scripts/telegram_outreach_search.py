#!/usr/bin/env python3
from __future__ import annotations

import argparse
import asyncio
import json

from services.partnership_research.app.services.telegram_outreach import (
    DEFAULT_OUTREACH_QUERIES,
    search_telegram_outreach,
)
from services.telegram_adapter.app.client import create_client

async def run_search(queries: list[str], limit_per_query: int, post_limit: int) -> dict[str, object]:
    client = create_client()
    await client.connect()
    try:
        if not await client.is_user_authorized():
            raise RuntimeError("Telegram session is not authorized. Run the Telethon login first.")
        return await search_telegram_outreach(
            client,
            queries=queries,
            limit_per_query=limit_per_query,
            post_limit=post_limit,
        )
    finally:
        await client.disconnect()


def main() -> int:
    parser = argparse.ArgumentParser(description="Telegram outreach discovery for FitMentor.")
    parser.add_argument("--queries", nargs="*", default=DEFAULT_OUTREACH_QUERIES)
    parser.add_argument("--limit-per-query", type=int, default=20)
    parser.add_argument("--post-limit", type=int, default=8)
    args = parser.parse_args()

    result = asyncio.run(
        run_search(
            queries=args.queries,
            limit_per_query=max(1, args.limit_per_query),
            post_limit=max(1, args.post_limit),
        )
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
