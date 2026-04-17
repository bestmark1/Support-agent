from packages.common.clients.ai_gateway import AIGatewayClient
from services.support_agent.app.services.kb_api import (
    create_proposed_update_via_api,
    ensure_support_thread_via_api,
    log_support_message_via_api,
    search_approved_knowledge_via_api,
)
from services.support_agent.app.services.prompting import (
    build_user_prompt,
    load_system_prompt,
)


async def build_support_reply(
    user_text: str,
    telegram_user_id: str,
    telegram_chat_id: str,
) -> str:
    thread_id = await ensure_support_thread_via_api(
        telegram_user_id=telegram_user_id,
        telegram_chat_id=telegram_chat_id,
    )
    await log_support_message_via_api(
        thread_id=thread_id,
        role="user",
        message_text=user_text,
    )

    results = await search_approved_knowledge_via_api(user_text, limit=3)
    if not results:
        await create_proposed_update_via_api(
            source="support_agent",
            suggested_category="faq",
            suggested_title="Unknown user support question",
            suggested_content=user_text,
            reason="No approved knowledge was found for the incoming support question.",
            evidence={"user_text": user_text},
        )
        return (
            "Я не нашёл уверенный ответ в базе знаний. "
            "Этот вопрос нужно добавить в review."
        )

    gateway = AIGatewayClient()
    if not gateway.enabled:
        top_hit = results[0]
        reply = (
            "AI gateway ещё не подключён. "
            f"Лучший найденный фрагмент: {top_hit['title'] or 'Без названия'}"
        )
        await log_support_message_via_api(
            thread_id=thread_id,
            role="assistant",
            message_text=reply,
            retrieval_context=results,
        )
        return reply

    system_prompt = load_system_prompt()
    user_prompt = build_user_prompt(user_text=user_text, knowledge_items=results)
    reply = await gateway.generate_reply(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
    )

    if not reply:
        await create_proposed_update_via_api(
            source="support_agent",
            suggested_category="faq",
            suggested_title="Empty AI reply for support question",
            suggested_content=user_text,
            reason="The AI gateway returned an empty reply for a support question.",
            evidence={"user_text": user_text},
        )
        reply = "Не удалось собрать уверенный ответ. Вопрос отправлен в review."
        await log_support_message_via_api(
            thread_id=thread_id,
            role="assistant",
            message_text=reply,
            retrieval_context=results,
        )
        return reply

    await log_support_message_via_api(
        thread_id=thread_id,
        role="assistant",
        message_text=reply,
        retrieval_context=results,
    )
    return reply
