from __future__ import annotations

from typing import Any

from services.kb_api.app.repositories.support_summary import get_support_summary


async def fetch_support_summary(*, days: int = 1, include_tests: bool = False) -> dict[str, Any]:
    return await get_support_summary(days=days, include_tests=include_tests)
