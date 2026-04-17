from packages.common.schemas.support_logs import (
    SupportMessageCreate,
    SupportThreadCreate,
)
from services.kb_api.app.repositories.support_logs import (
    create_support_message,
    get_or_create_support_thread,
)


async def ensure_support_thread(payload: SupportThreadCreate) -> dict[str, str]:
    thread_id = await get_or_create_support_thread(
        telegram_user_id=payload.telegram_user_id,
        telegram_chat_id=payload.telegram_chat_id,
    )
    return {"thread_id": thread_id}


async def log_support_message(payload: SupportMessageCreate) -> dict[str, str]:
    message_id = await create_support_message(
        thread_id=payload.thread_id,
        role=payload.role,
        message_text=payload.message_text,
        retrieval_context=payload.retrieval_context,
    )
    return {"message_id": message_id}
