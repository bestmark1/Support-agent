from __future__ import annotations

from collections import Counter
from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy import text

from packages.common.db.session import get_session


def _bucket_issue(text_value: str) -> str:
    text = " ".join((text_value or "").strip().lower().split())
    if not text:
        return "other"
    if any(
        token in text
        for token in (
            "приоритетная поддержка",
            "priority support",
            "@fitmentor_support",
            "получаешь приоритетный ответ",
            "you get priority support",
            "пиши напрямую",
            "write directly",
        )
    ):
        return "other"
    if any(token in text for token in ("refund", "возврат", "верните деньги")):
        return "refund"
    if any(token in text for token in ("charged twice", "double charge", "списали дважды", "двойное списание")):
        return "duplicate_charge"
    if any(token in text for token in ("payment failed", "can't pay", "не проходит оплата", "оплата не прошла")):
        return "payment_failed"
    if any(
        token in text
        for token in (
            "subscription inactive",
            "did not activate",
            "подписка неактивна",
            "неактивна подписка",
            "не активировалась",
        )
    ):
        return "activation_issue"
    if any(
        token in text
        for token in (
            "premium",
            "лимит ai",
            "лимит сообщений",
            "weekly report",
            "рецепты",
            "premium-функ",
            "premium feature",
        )
    ):
        if any(
            token in text
            for token in (
                "остался старый",
                "не обновил",
                "не обновился",
                "не изменил",
                "не изменился",
                "ограничен",
                "не открылись",
                "недоступ",
                "это баг",
                "still old",
                "did not update",
                "not updated",
                "still limited",
                "still unavailable",
                "still locked",
                "not available",
                "bug",
            )
        ):
            return "premium_entitlement"
        return "other"
    if any(token in text for token in ("how to subscribe", "subscribe", "как подписаться", "оформить подписку")):
        return "subscribe"
    if any(token in text for token in ("cancel subscription", "unsubscribe", "отменить подписку", "отписаться")):
        return "cancel"
    if any(token in text for token in ("operator", "human support", "живой человек", "оператор")):
        return "human_support"
    return "other"


def _needs_manual_review(*, latest_user_message: str, latest_assistant_message: str) -> bool:
    user_text = " ".join((latest_user_message or "").strip().lower().split())
    assistant_text = " ".join((latest_assistant_message or "").strip().lower().split())
    bucket = _bucket_issue(user_text)
    if any(
        token in assistant_text
        for token in (
            "ручн",
            "manual",
            "проверит специалист",
            "поддержка проверит",
            "needs manual",
            "manual verification",
        )
    ):
        return bucket != "other"
    return bucket in {
        "refund",
        "duplicate_charge",
        "activation_issue",
        "premium_entitlement",
        "human_support",
    }


def _dedupe_threads_by_message(threads: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    deduped: list[dict[str, Any]] = []
    for item in threads:
        normalized_message = " ".join(str(item.get("latest_user_message") or "").strip().lower().split())
        dedupe_key = normalized_message or str(item.get("id") or "")
        if dedupe_key in seen:
            continue
        seen.add(dedupe_key)
        deduped.append(item)
    return deduped


async def get_support_summary(*, days: int = 1, include_tests: bool = False) -> dict[str, Any]:
    days = max(1, min(days, 30))
    since = datetime.now(timezone.utc) - timedelta(days=days)

    async with get_session() as session:
        counts_result = await session.execute(
            text(
                """
                select
                  (select count(*)
                   from support_threads
                   where last_message_at >= :since
                     and (:include_tests or is_test = false)) as threads_total,
                  (select count(*)
                   from support_threads
                   where case_status = 'open' and last_message_at >= :since
                     and (:include_tests or is_test = false)) as open_threads_total,
                  (select count(*)
                   from support_threads
                   where case_status = 'manual_review' and last_message_at >= :since
                     and (:include_tests or is_test = false)) as manual_review_threads_total,
                  (select count(*)
                   from support_threads
                   where case_status = 'resolved' and last_message_at >= :since
                     and (:include_tests or is_test = false)) as resolved_threads_total,
                  (select count(*)
                   from support_messages
                   where role = 'user' and created_at >= :since
                     and thread_id in (
                       select id
                       from support_threads
                       where :include_tests or is_test = false
                     )) as user_messages_total,
                  (select count(*)
                   from support_threads
                   where priority_support = true and last_message_at >= :since
                     and (:include_tests or is_test = false)) as priority_threads_total,
                  (select count(*)
                   from proposed_updates
                   where status = 'pending' and created_at >= :since) as pending_candidates_total
                """
            ),
            {"since": since, "include_tests": include_tests},
        )
        counts = counts_result.mappings().one()

        recent_threads_result = await session.execute(
            text(
                """
                with ranked_user_messages as (
                  select
                    sm.thread_id,
                    sm.message_text,
                    sm.created_at,
                    row_number() over (partition by sm.thread_id order by sm.created_at desc) as rn
                  from support_messages sm
                  where sm.role = 'user'
                ),
                ranked_assistant_messages as (
                  select
                    sm.thread_id,
                    sm.message_text,
                    sm.created_at,
                    row_number() over (partition by sm.thread_id order by sm.created_at desc) as rn
                  from support_messages sm
                  where sm.role = 'assistant'
                )
                select
                  st.id,
                  st.telegram_user_id,
                  st.telegram_chat_id,
                  st.preferred_language,
                  st.priority_support,
                  st.is_test,
                  st.case_status,
                  st.resolution_note,
                  st.resolved_at,
                  st.last_message_at,
                  rum.message_text as latest_user_message,
                  ram.message_text as latest_assistant_message
                from support_threads st
                left join ranked_user_messages rum
                  on rum.thread_id = st.id and rum.rn = 1
                left join ranked_assistant_messages ram
                  on ram.thread_id = st.id and ram.rn = 1
                where st.last_message_at >= :since
                  and (:include_tests or st.is_test = false)
                order by st.last_message_at desc
                limit 20
                """
            ),
            {"since": since, "include_tests": include_tests},
        )
        recent_threads = [dict(row) for row in recent_threads_result.mappings().all()]

        recent_user_messages_result = await session.execute(
            text(
                """
                select sm.message_text
                from support_messages sm
                where sm.role = 'user'
                  and sm.created_at >= :since
                  and sm.thread_id in (
                    select id
                    from support_threads
                    where :include_tests or is_test = false
                  )
                order by sm.created_at desc
                limit 200
                """
            ),
            {"since": since, "include_tests": include_tests},
        )
        messages = [str(row.message_text or "") for row in recent_user_messages_result.all()]

        pending_candidates_result = await session.execute(
            text(
                """
                select
                  id,
                  suggested_category,
                  suggested_title,
                  suggested_content,
                  reason,
                  created_at,
                  evidence
                from proposed_updates
                where status = 'pending'
                order by created_at desc
                limit 20
                """
            )
        )
        pending_candidates = [dict(row) for row in pending_candidates_result.mappings().all()]

    issue_counter = Counter(_bucket_issue(message) for message in messages)
    top_issues = [
        {"bucket": bucket, "count": count}
        for bucket, count in issue_counter.most_common(10)
        if count > 0 and bucket != "other"
    ][:5]

    for item in recent_threads:
        latest_user_message = str(item.get("latest_user_message") or "")
        latest_assistant_message = str(item.get("latest_assistant_message") or "")
        item["issue_bucket"] = _bucket_issue(latest_user_message)
        explicit_status = str(item.get("case_status") or "open")
        if explicit_status == "resolved":
            item["needs_manual_review"] = False
        else:
            item["needs_manual_review"] = explicit_status == "manual_review" or _needs_manual_review(
                latest_user_message=latest_user_message,
                latest_assistant_message=latest_assistant_message,
            )

    manual_review_threads = _dedupe_threads_by_message(
        [item for item in recent_threads if item.get("needs_manual_review")]
    )
    kb_gap_counter = Counter(str(item.get("suggested_title") or "").strip() for item in pending_candidates if str(item.get("suggested_title") or "").strip())
    top_kb_gaps = [
        {"title": title, "count": count}
        for title, count in kb_gap_counter.most_common(5)
        if count > 0
    ]

    return {
        "days": days,
        "since": since.isoformat(),
        "threads_total": int(counts["threads_total"] or 0),
        "open_threads_total": int(counts["open_threads_total"] or 0),
        "manual_review_threads_total": int(counts["manual_review_threads_total"] or 0),
        "resolved_threads_total": int(counts["resolved_threads_total"] or 0),
        "user_messages_total": int(counts["user_messages_total"] or 0),
        "priority_threads_total": int(counts["priority_threads_total"] or 0),
        "pending_candidates_total": int(counts["pending_candidates_total"] or 0),
        "include_tests": include_tests,
        "top_issues": top_issues,
        "recent_threads": recent_threads,
        "manual_review_threads": manual_review_threads[:10],
        "pending_candidates": pending_candidates[:10],
        "top_kb_gaps": top_kb_gaps,
    }
