from packages.common.schemas.support_logs import (
    SupportMessageCreate,
    SupportThreadCreate,
    SupportThreadStatusUpdate,
)
from services.kb_api.app.repositories.support_logs import (
    create_support_message,
    get_or_create_support_thread,
    update_support_thread_status,
)
from services.kb_api.app.services.language import detect_language, normalize_language


async def ensure_support_thread(payload: SupportThreadCreate) -> dict[str, str | None | bool]:
    preferred_language = normalize_language(payload.preferred_language)
    thread_id, resolved_language, priority_support, is_test, case_status = await get_or_create_support_thread(
        telegram_user_id=payload.telegram_user_id,
        telegram_chat_id=payload.telegram_chat_id,
        preferred_language=preferred_language,
        priority_support=payload.priority_support,
        is_test=payload.is_test,
    )
    return {
        "thread_id": thread_id,
        "preferred_language": resolved_language,
        "priority_support": priority_support,
        "is_test": is_test,
        "case_status": case_status,
    }


async def log_support_message(payload: SupportMessageCreate) -> dict[str, str]:
    preferred_language = normalize_language(payload.preferred_language)
    if payload.role == "user" and preferred_language is None:
        preferred_language = detect_language(payload.message_text)
    message_id = await create_support_message(
        thread_id=payload.thread_id,
        role=payload.role,
        message_text=payload.message_text,
        retrieval_context=payload.retrieval_context,
        preferred_language=preferred_language,
    )
    return {"message_id": message_id}


async def set_support_thread_status(payload: SupportThreadStatusUpdate) -> dict[str, str | None]:
    return await update_support_thread_status(
        thread_id=payload.thread_id,
        case_status=payload.case_status,
        resolution_note=payload.resolution_note,
        reviewed_by=payload.reviewed_by,
    )
