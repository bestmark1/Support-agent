import json

from sqlalchemy import text

from packages.common.db.session import get_session


async def get_or_create_support_thread(
    telegram_user_id: str,
    telegram_chat_id: str,
    preferred_language: str | None = None,
    priority_support: bool = False,
    is_test: bool = False,
) -> tuple[str, str | None, bool, bool, str]:
    async with get_session() as session:
        select_sql = text(
            """
            select id, preferred_language, priority_support, is_test, case_status
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
        row = existing.first()
        if row:
            thread_id = row.id
            current_language = row.preferred_language
            current_priority_support = bool(row.priority_support)
            current_is_test = bool(row.is_test)
            current_case_status = str(row.case_status or "open")
            update_sql = text(
                """
                update support_threads
                set last_message_at = now(),
                    preferred_language = coalesce(:preferred_language, preferred_language),
                    priority_support = (:priority_support or priority_support),
                    is_test = (:is_test or is_test),
                    case_status = case
                      when case_status = 'resolved' then 'open'
                      else case_status
                    end,
                    resolution_note = case
                      when case_status = 'resolved' then null
                      else resolution_note
                    end,
                    resolved_at = case
                      when case_status = 'resolved' then null
                      else resolved_at
                    end,
                    reviewed_by = case
                      when case_status = 'resolved' then null
                      else reviewed_by
                    end
                where id = :thread_id
                """
            )
            await session.execute(
                update_sql,
                {
                    "thread_id": thread_id,
                    "preferred_language": preferred_language,
                    "priority_support": priority_support,
                    "is_test": is_test,
                },
            )
            await session.commit()
            return (
                str(thread_id),
                preferred_language or current_language,
                (priority_support or current_priority_support),
                (is_test or current_is_test),
                ("open" if current_case_status == "resolved" else current_case_status),
            )

        insert_sql = text(
            """
            insert into support_threads (
              telegram_user_id,
              telegram_chat_id,
              preferred_language,
              priority_support,
              is_test,
              case_status
            )
            values (
              :telegram_user_id,
              :telegram_chat_id,
              :preferred_language,
              :priority_support,
              :is_test,
              'open'
            )
            returning id, preferred_language, priority_support, is_test, case_status
            """
        )
        created = await session.execute(
            insert_sql,
            {
                "telegram_user_id": telegram_user_id,
                "telegram_chat_id": telegram_chat_id,
                "preferred_language": preferred_language,
                "priority_support": priority_support,
                "is_test": is_test,
            },
        )
        await session.commit()
        created_row = created.first()
        return (
            str(created_row.id),
            created_row.preferred_language,
            bool(created_row.priority_support),
            bool(created_row.is_test),
            str(created_row.case_status or "open"),
        )


async def create_support_message(
    thread_id: str,
    role: str,
    message_text: str,
    retrieval_context: list[dict[str, object]] | None = None,
    preferred_language: str | None = None,
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
            set last_message_at = now(),
                preferred_language = coalesce(:preferred_language, preferred_language)
            where id = :thread_id
            """
        )
        await session.execute(
            update_sql,
            {
                "thread_id": thread_id,
                "preferred_language": preferred_language,
            },
        )
        await session.commit()
        return str(result.scalar_one())


async def update_support_thread_status(
    *,
    thread_id: str,
    case_status: str,
    resolution_note: str | None = None,
    reviewed_by: str | None = None,
) -> dict[str, str | None]:
    async with get_session() as session:
        sql = text(
            """
            update support_threads
            set case_status = :case_status,
                resolution_note = :resolution_note,
                reviewed_by = :reviewed_by,
                resolved_at = case
                  when :case_status = 'resolved' then now()
                  else null
                end
            where id = :thread_id
            returning id, case_status, resolution_note, reviewed_by,
              case when resolved_at is not null then resolved_at::text else null end as resolved_at
            """
        )
        result = await session.execute(
            sql,
            {
                "thread_id": thread_id,
                "case_status": case_status,
                "resolution_note": resolution_note,
                "reviewed_by": reviewed_by,
            },
        )
        await session.commit()
        row = result.mappings().first()
        if row is None:
            raise ValueError("Support thread not found")
        return {
            "thread_id": str(row["id"]),
            "case_status": str(row["case_status"]),
            "resolution_note": row["resolution_note"],
            "reviewed_by": row["reviewed_by"],
            "resolved_at": row["resolved_at"],
        }
