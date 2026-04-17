import json

from sqlalchemy import text

from packages.common.db.session import get_session


async def get_or_create_support_thread(
    telegram_user_id: str,
    telegram_chat_id: str,
) -> str:
    async with get_session() as session:
        select_sql = text(
            """
            select id
            from support_threads
            where telegram_user_id = :telegram_user_id
              and telegram_chat_id = :telegram_chat_id
            limit 1
            """
        )
        existing = await session.execute(
            select_sql,
            {
                "telegram_user_id": telegram_user_id,
                "telegram_chat_id": telegram_chat_id,
            },
        )
        thread_id = existing.scalar_one_or_none()
        if thread_id:
            update_sql = text(
                """
                update support_threads
                set last_message_at = now()
                where id = :thread_id
                """
            )
            await session.execute(update_sql, {"thread_id": thread_id})
            await session.commit()
            return str(thread_id)

        insert_sql = text(
            """
            insert into support_threads (
              telegram_user_id,
              telegram_chat_id
            )
            values (
              :telegram_user_id,
              :telegram_chat_id
            )
            returning id
            """
        )
        created = await session.execute(
            insert_sql,
            {
                "telegram_user_id": telegram_user_id,
                "telegram_chat_id": telegram_chat_id,
            },
        )
        await session.commit()
        return str(created.scalar_one())


async def create_support_message(
    thread_id: str,
    role: str,
    message_text: str,
    retrieval_context: list[dict[str, object]] | None = None,
) -> str:
    async with get_session() as session:
        sql = text(
            """
            insert into support_messages (
              thread_id,
              role,
              message_text,
              retrieval_context
            )
            values (
              :thread_id,
              :role,
              :message_text,
              cast(:retrieval_context as jsonb)
            )
            returning id
            """
        )
        result = await session.execute(
            sql,
            {
                "thread_id": thread_id,
                "role": role,
                "message_text": message_text,
                "retrieval_context": json.dumps(retrieval_context or []),
            },
        )
        update_sql = text(
            """
            update support_threads
            set last_message_at = now()
            where id = :thread_id
            """
        )
        await session.execute(update_sql, {"thread_id": thread_id})
        await session.commit()
        return str(result.scalar_one())
