from packages.common.schemas.proposed_updates import ProposedUpdateCreate
from services.kb_api.app.repositories.proposed_updates import create_proposed_update


async def submit_proposed_update(payload: ProposedUpdateCreate) -> dict[str, str]:
    proposed_update_id = await create_proposed_update(
        source=payload.source,
        suggested_category=payload.suggested_category,
        suggested_title=payload.suggested_title,
        suggested_content=payload.suggested_content,
        reason=payload.reason,
        evidence=payload.evidence,
    )
    return {
        "id": proposed_update_id,
        "status": "pending",
    }
