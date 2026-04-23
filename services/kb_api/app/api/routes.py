from fastapi import APIRouter

from packages.common.schemas.proposed_updates import ProposedUpdateCreate, ProposedUpdateCreateResult, ProposedUpdateReview
from packages.common.schemas.support_logs import (
    SupportMessageCreate,
    SupportThreadCreate,
    SupportThreadStatusUpdate,
)
from services.kb_api.app.services.proposed_updates import submit_proposed_update, submit_proposed_update_review
from services.kb_api.app.services.search import search_approved_knowledge
from services.kb_api.app.services.support_logs import (
    ensure_support_thread,
    log_support_message,
    set_support_thread_status,
)
from services.kb_api.app.services.support_summary import fetch_support_summary

router = APIRouter(prefix="/kb", tags=["knowledge"])


@router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/search")
async def search(query: str, limit: int = 5, language: str | None = None) -> dict[str, object]:
    items = await search_approved_knowledge(query=query, limit=limit, language=language)
    return {
        "items": items,
        "query": query,
        "limit": limit,
        "language": language,
    }


@router.post("/proposed-updates")
async def create_update(payload: ProposedUpdateCreate) -> ProposedUpdateCreateResult:
    return await submit_proposed_update(payload)


@router.post("/proposed-updates/review")
async def review_update(payload: ProposedUpdateReview) -> dict[str, object]:
    return await submit_proposed_update_review(payload)


@router.post("/support-threads")
async def create_thread(payload: SupportThreadCreate) -> dict[str, str | None | bool]:
    return await ensure_support_thread(payload)


@router.post("/support-threads/status")
async def update_thread_status(payload: SupportThreadStatusUpdate) -> dict[str, str | None]:
    return await set_support_thread_status(payload)


@router.post("/support-messages")
async def create_message(payload: SupportMessageCreate) -> dict[str, str]:
    return await log_support_message(payload)


@router.get("/support-summary")
async def support_summary(days: int = 1, include_tests: bool = False) -> dict[str, object]:
    return await fetch_support_summary(days=days, include_tests=include_tests)
