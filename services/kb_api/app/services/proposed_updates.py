from packages.common.schemas.proposed_updates import ProposedUpdateCreate, ProposedUpdateCreateResult, ProposedUpdateReview
from services.kb_api.app.repositories.proposed_updates import create_proposed_update, review_proposed_update


async def submit_proposed_update(payload: ProposedUpdateCreate) -> ProposedUpdateCreateResult:
    proposed_update_id, created = await create_proposed_update(
        source=payload.source,
        suggested_category=payload.suggested_category,
        suggested_title=payload.suggested_title,
        suggested_content=payload.suggested_content,
        reason=payload.reason,
        evidence=payload.evidence,
    )
    return ProposedUpdateCreateResult(id=proposed_update_id, status="pending", created=created)


async def submit_proposed_update_review(payload: ProposedUpdateReview) -> dict[str, object]:
    return await review_proposed_update(
        proposed_update_id=payload.id,
        action=payload.action,
        reviewed_by=payload.reviewed_by,
        edited_content=payload.edited_content,
    )
