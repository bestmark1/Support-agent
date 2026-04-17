from fastapi import APIRouter

from packages.common.schemas.proposed_updates import ProposedUpdateCreate
from packages.common.schemas.support_logs import (
    SupportMessageCreate,
    SupportThreadCreate,
)
from services.kb_api.app.services.proposed_updates import submit_proposed_update
from services.kb_api.app.services.search import search_approved_knowledge
from services.kb_api.app.services.support_logs import (
    ensure_support_thread,
    log_support_message,
)

router = APIRouter(prefix="/kb", tags=["knowledge"])


@router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/search")
async def search(query: str, limit: int = 5) -> dict[str, object]:
    items = await search_approved_knowledge(query=query, limit=limit)
    return {
        "items": items,
        "query": query,
        "limit": limit,
    }


@router.post("/proposed-updates")
async def create_update(payload: ProposedUpdateCreate) -> dict[str, str]:
    return await submit_proposed_update(payload)


@router.post("/support-threads")
async def create_thread(payload: SupportThreadCreate) -> dict[str, str]:
    return await ensure_support_thread(payload)


@router.post("/support-messages")
async def create_message(payload: SupportMessageCreate) -> dict[str, str]:
    return await log_support_message(payload)
