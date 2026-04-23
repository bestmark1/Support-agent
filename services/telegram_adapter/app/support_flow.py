from __future__ import annotations

import json
import os
import re
from typing import Any

import httpx
from telethon import TelegramClient
from telethon.tl.custom.message import Message

from services.partnership_research.app.services.telegram_outreach import (
    DEFAULT_OUTREACH_QUERIES,
    search_telegram_outreach,
)
from services.kb_api.app.services.language import detect_language, normalize_language
from services.telegram_adapter.app.config import get_telegram_settings
from services.telegram_adapter.app.commands import telegram_reply


KB_API_BASE_URL = os.environ.get("KB_API_BASE_URL", "http://127.0.0.1:8010").rstrip("/")

RU_GREETINGS = {
    "привет",
    "здравствуйте",
    "добрый день",
    "добрый вечер",
    "доброе утро",
    "салют",
}
EN_GREETINGS = {
    "hi",
    "hello",
    "hey",
    "good morning",
    "good afternoon",
    "good evening",
}

RU_GENERIC_FALLBACK_REPLIES = {
    "я пока не нашёл точного утверждённого ответа. пришлите, пожалуйста, ваш telegram-аккаунт, дату платежа, сумму и, если есть, подтверждение оплаты, чтобы поддержка могла проверить это вручную.",
    "я проверил статус для этого telegram-аккаунта и пока не вижу активной подписки или найденного платежа. пришлите, пожалуйста, дату платежа, сумму и подтверждение оплаты или чек, чтобы поддержка могла проверить кейс вручную.",
}
EN_GENERIC_FALLBACK_REPLIES = {
    "i could not find a clear approved answer yet. please send your telegram account, payment date, amount, and any payment confirmation details so support can review this manually.",
    "i checked the status for this telegram account and do not see an active subscription or a recorded payment yet. please send the payment date, amount, and any payment confirmation or receipt so support can review the case manually.",
}


def _normalized(text: str) -> str:
    return " ".join(text.strip().lower().split())


def _normalized_simple_phrase(text: str) -> str:
    normalized = _normalized(text)
    return normalized.strip(".,!?;:()[]{}\"'")


def _contains_any(text: str, tokens: tuple[str, ...]) -> bool:
    return any(token in text for token in tokens)


def _is_payment_failed(text: str, language: str) -> bool:
    if language == "en":
        return _contains_any(
            text,
            (
                "payment failed",
                "could not pay",
                "can't pay",
                "cannot pay",
                "payment did not go through",
                "card declined",
                "declined",
            ),
        )
    return _contains_any(
        text,
        (
            "оплата не прошла",
            "оплата не проходит",
            "не могу оплатить",
            "не получается оплатить",
            "платеж не прошел",
            "платёж не прошёл",
            "карта отклонена",
            "не проходит оплата",
        ),
    )


def _is_duplicate_charge(text: str, language: str) -> bool:
    if language == "en":
        return _contains_any(
            text,
            (
                "charged twice",
                "double charge",
                "duplicate charge",
                "charged two times",
            ),
        )
    return _contains_any(
        text,
        (
            "списали дважды",
            "двойное списание",
            "дважды списали",
            "списание два раза",
        ),
    )


def _is_refund_request(text: str, language: str) -> bool:
    if language == "en":
        return _contains_any(
            text,
            (
                "refund",
                "money back",
                "return my money",
                "cancel and refund",
            ),
        )
    return _contains_any(
        text,
        (
            "возврат",
            "верните деньги",
            "хочу вернуть деньги",
            "оформить возврат",
        ),
    )


def _is_how_to_subscribe(text: str, language: str) -> bool:
    if language == "en":
        return _contains_any(
            text,
            ("how to subscribe", "how can i subscribe", "how to pay", "want to subscribe", "buy subscription"),
        )
    return _contains_any(
        text,
        (
            "как подписаться",
            "как оформить подписку",
            "хочу подписку",
            "как оплатить",
            "оформить подписку",
        ),
    )


def _is_how_to_cancel(text: str, language: str) -> bool:
    if language == "en":
        return _contains_any(
            text,
            ("cancel subscription", "how to cancel", "unsubscribe", "stop subscription"),
        )
    return _contains_any(
        text,
        (
            "отменить подписку",
            "как отменить",
            "отписаться",
            "отключить подписку",
        ),
    )


def _is_subscription_status_check(text: str, language: str) -> bool:
    if language == "en":
        return _contains_any(
            text,
            ("is my subscription active", "check subscription", "subscription status", "is premium active"),
        )
    return _contains_any(
        text,
        (
            "активна ли подписка",
            "проверить подписку",
            "статус подписки",
            "подписка активна",
        ),
    )


def _is_human_support_request(text: str, language: str) -> bool:
    if language == "en":
        return _contains_any(
            text,
            ("human support", "talk to a person", "real person", "operator", "manager"),
        )
    return _contains_any(
        text,
        (
            "оператор",
            "живой человек",
            "свяжите с поддержкой",
            "менеджер",
            "человек из поддержки",
        ),
    )


def _is_thanks(text: str, language: str) -> bool:
    text = _normalized_simple_phrase(text)
    if language == "en":
        return text in {"thanks", "thank you", "thx"}
    return text in {"спасибо", "благодарю", "спс"}


def _is_goodbye(text: str, language: str) -> bool:
    text = _normalized_simple_phrase(text)
    if language == "en":
        return text in {"bye", "goodbye", "see you"}
    return text in {"пока", "до свидания", "всего доброго"}


def _is_subscription_activation_issue(text: str, language: str) -> bool:
    normalized = _normalized(text)
    if not normalized:
        return False

    if language == "en":
        has_payment = any(
            token in normalized
            for token in ("paid", "payment", "charged", "charge", "paid for", "paid but")
        )
        has_activation_problem = any(
            token in normalized
            for token in (
                "subscription is inactive",
                "subscription inactive",
                "did not activate",
                "not activated",
                "no access",
                "still inactive",
            )
        )
        return has_payment and has_activation_problem

    has_payment = any(
        token in normalized
        for token in ("заплатил", "оплатил", "оплата", "списали", "списание", "платеж", "платёж")
    )
    has_activation_problem = any(
        token in normalized
        for token in (
            "подписка неактивна",
            "неактивна подписка",
            "не активировалась",
            "не активна",
            "не активна подписка",
            "нет доступа",
            "доступа нет",
        )
    )
    return has_payment and has_activation_problem


def _is_premium_entitlement_issue(text: str, language: str) -> bool:
    normalized = _normalized(text)
    if not normalized:
        return False

    if language == "en":
        has_premium_context = any(
            token in normalized
            for token in (
                "premium",
                "ai limit",
                "weekly report",
                "recipes",
                "premium feature",
                "premium features",
            )
        )
        has_access_problem = any(
            token in normalized
            for token in (
                "still old",
                "did not update",
                "not updated",
                "still limited",
                "still unavailable",
                "still locked",
                "not available",
                "bug",
            )
        )
        return has_premium_context and has_access_problem

    has_premium_context = any(
        token in normalized
        for token in (
            "premium",
            "премиум",
            "лимит ai",
            "лимит сообщений",
            "weekly report",
            "рецепт",
            "рецепты",
            "премиум-функц",
        )
    )
    has_access_problem = any(
        token in normalized
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
        )
    )
    return has_premium_context and has_access_problem


def _extract_premium_feature_hint(text: str, language: str) -> str | None:
    normalized = _normalized(text)
    if not normalized:
        return None

    if language == "en":
        if any(token in normalized for token in ("ai limit", "ai message limit", "message limit", "ai messages")):
            return "ai_limit"
        if any(token in normalized for token in ("weekly report", "weekly reports")):
            return "weekly_report"
        if any(token in normalized for token in ("recipe", "recipes")):
            return "recipes"
        return None

    if any(
        token in normalized
        for token in ("лимит ai", "лимит ai-сообщений", "лимит сообщений", "ai-сообщений", "ai сообщений")
    ):
        return "ai_limit"
    if "weekly report" in normalized:
        return "weekly_report"
    if any(token in normalized for token in ("рецепт", "рецепты")):
        return "recipes"
    return None


def _is_priority_support(support_check: dict[str, Any] | None) -> bool:
    subscription = (support_check or {}).get("subscription") or {}
    effective_tier = _normalized(str(subscription.get("effective_tier") or ""))
    current_tier = _normalized(str(subscription.get("current_tier") or ""))
    return effective_tier == "premium" or current_tier == "premium"


def _is_payment_or_access_context(text: str, language: str) -> bool:
    normalized = _normalized(text)
    return (
        _is_payment_failed(normalized, language)
        or _is_duplicate_charge(normalized, language)
        or _is_refund_request(normalized, language)
        or _is_how_to_subscribe(normalized, language)
        or _is_how_to_cancel(normalized, language)
        or _is_subscription_status_check(normalized, language)
        or _is_subscription_activation_issue(text, language)
        or _is_premium_entitlement_issue(text, language)
        or _is_human_support_request(normalized, language)
    )


def should_create_candidate_knowledge(
    *,
    user_text: str,
    reply_text: str,
    language: str,
    kb_items: list[dict[str, Any]],
    support_check: dict[str, Any] | None,
) -> bool:
    normalized_user = _normalized(user_text)
    normalized_reply = _normalized(reply_text)

    if not normalized_user or not normalized_reply:
        return False
    if kb_items:
        return False
    if any(
        (
            _is_payment_failed(normalized_user, language),
            _is_duplicate_charge(normalized_user, language),
            _is_refund_request(normalized_user, language),
            _is_how_to_subscribe(normalized_user, language),
            _is_how_to_cancel(normalized_user, language),
            _is_subscription_status_check(normalized_user, language),
            _is_subscription_activation_issue(user_text, language),
            _is_premium_entitlement_issue(user_text, language),
            _is_human_support_request(normalized_user, language),
        )
    ):
        return False
    if _is_thanks(normalized_user, language) or _is_goodbye(normalized_user, language):
        return False
    if normalized_reply in (EN_GENERIC_FALLBACK_REPLIES if language == "en" else RU_GENERIC_FALLBACK_REPLIES):
        return False
    diagnosis = str((support_check or {}).get("diagnosis") or "")
    if diagnosis in {"no_payment_found", "payment_pending", "subscription_active", "payment_confirmed_and_access_granted"}:
        return False
    if len(normalized_user) < 20:
        return False
    return True


def build_candidate_knowledge_draft(
    *,
    user_text: str,
    reply_text: str,
    language: str,
    support_check: dict[str, Any] | None,
) -> dict[str, str] | None:
    diagnosis = str((support_check or {}).get("diagnosis") or "")

    if _is_premium_entitlement_issue(user_text, language):
        if language == "en":
            return {
                "category": "product",
                "title": "What to do if Premium is paid but limits or Premium features did not update",
                "content": (
                    "If a user says Premium payment succeeded but AI limits, reports, recipes, or other Premium features still look old, "
                    "support should first check the subscription status and the latest payment state. "
                    "If Premium access is active but the limits or features did not refresh, the case needs manual verification of Premium entitlement application. "
                    "If no payment is found, support should request the payment date, amount, and payment confirmation."
                ),
                "reason": "New support pattern: Premium entitlement looks active, but limits or Premium features may not refresh correctly.",
            }
        return {
            "category": "product",
            "title": "Что делать, если Premium оплачен, но лимиты или Premium-функции не обновились",
            "content": (
                "Если пользователь пишет, что Premium оплачен, но лимиты AI, weekly report, рецепты или другие Premium-функции остались старыми, "
                "поддержка сначала проверяет статус подписки и состояние последнего платежа. "
                "Если Premium уже активен, но лимиты или функции не обновились, кейс требует ручной проверки применения Premium-прав и лимитов. "
                "Если платёж не найден, нужно запросить дату платежа, сумму и подтверждение оплаты."
            ),
            "reason": "Новый support-сценарий: Premium может быть активен, но лимиты или Premium-функции обновляются некорректно.",
        }

    if _is_subscription_activation_issue(user_text, language):
        if language == "en":
            content = (
                "If a user says payment succeeded but the subscription did not activate, support should first check the latest payment and current subscription status. "
                "If payment is confirmed but access is still missing, the case requires manual activation review. "
                "If no payment is found yet, support should ask for the payment date, amount, and payment confirmation."
            )
            if diagnosis == "payment_pending":
                content += " If the latest payment is still pending, the user should be asked to wait a little or complete the payment flow."
            return {
                "category": "faq",
                "title": "What to do if payment succeeded but the subscription did not activate",
                "content": content,
                "reason": "Repeated support scenario around paid subscription activation.",
            }
        content = (
            "Если пользователь пишет, что оплата прошла, но подписка не активировалась, поддержка сначала проверяет последний платёж и текущий статус подписки. "
            "Если платёж подтверждён, но доступ не применился, кейс требует ручной проверки активации. "
            "Если платёж не найден, нужно запросить дату платежа, сумму и подтверждение оплаты."
        )
        if diagnosis == "payment_pending":
            content += " Если последний платёж ещё в обработке, пользователю нужно предложить подождать немного или завершить сценарий оплаты."
        return {
            "category": "faq",
            "title": "Что делать, если оплата прошла, но подписка не активировалась",
            "content": content,
            "reason": "Повторяющийся support-сценарий по активации оплаченной подписки.",
        }

    if _is_how_to_cancel(_normalized(user_text), language):
        if language == "en":
            return {
                "category": "faq",
                "title": "How support handles subscription cancellation requests",
                "content": (
                    "If a user asks to cancel a subscription, support should first clarify which subscription is meant and check the current subscription state. "
                    "The next step depends on the active plan, payment status, and current access state."
                ),
                "reason": "Current KB answer for cancellation is still too thin and procedural.",
            }
        return {
            "category": "faq",
            "title": "Как поддержка обрабатывает запросы на отмену подписки",
            "content": (
                "Если пользователь просит отменить подписку, поддержка сначала уточняет, какую именно подписку он имеет в виду, и проверяет текущий статус доступа. "
                "Дальнейший шаг зависит от активного тарифа, статуса оплаты и текущего состояния подписки."
            ),
            "reason": "Текущий KB-ответ по отмене подписки пока слишком короткий и процедурный.",
        }

    return None


async def kb_get(client: httpx.AsyncClient, path: str, params: dict[str, Any]) -> dict[str, Any]:
    response = await client.get(f"{KB_API_BASE_URL}{path}", params=params, timeout=20.0)
    response.raise_for_status()
    return response.json()


async def kb_post(client: httpx.AsyncClient, path: str, payload: dict[str, Any]) -> dict[str, Any]:
    response = await client.post(f"{KB_API_BASE_URL}{path}", json=payload, timeout=20.0)
    response.raise_for_status()
    return response.json()


def extract_candidate_id(text: str) -> str | None:
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.lower().startswith("id:"):
            candidate_id = stripped.split(":", 1)[1].strip()
            return candidate_id or None
    return None


def parse_owner_review_action(text: str) -> tuple[str | None, str | None]:
    normalized = _normalized(text)
    if not normalized:
        return None, None
    if normalized.startswith("исправь так:"):
        return "edit", text.split(":", 1)[1].strip()
    if normalized.startswith("edit like this:"):
        return "edit", text.split(":", 1)[1].strip()
    if normalized in {"подтверждаю", "добавляй", "ок, добавь", "ок добавь", "approve", "approved", "да"}:
        return "approve", None
    if normalized in {"не добавляй", "отклоняю", "reject", "rejected", "нет", "не надо"}:
        return "reject", None
    return None, None


def _is_operator_summary_request(text: str) -> bool:
    normalized = _normalized(text)
    return any(
        token in normalized
        for token in (
            "сколько человек",
            "сколько сегодня",
            "кто написал",
            "сводка",
            "summary",
            "support today",
            "today support",
            "сегодня написало",
            "что по поддержке",
            "как дела у поддержки",
        )
    )


def _is_operator_premium_request(text: str) -> bool:
    normalized = _normalized(text)
    return any(
        token in normalized
        for token in (
            "premium-кейс",
            "premium кейс",
            "premium case",
            "priority support",
            "priority support кейс",
            "priority support cases",
            "премиум-кейс",
            "премиум кейс",
            "приоритетный кейс",
            "приоритетные кейсы",
            "платные пользователи",
            "платные кейсы",
        )
    )


def _is_owner_support_like_request(text: str, language: str) -> bool:
    normalized = _normalized(text)
    if not normalized:
        return False
    return any(
        (
            _is_payment_failed(normalized, language),
            _is_duplicate_charge(normalized, language),
            _is_refund_request(normalized, language),
            _is_how_to_subscribe(normalized, language),
            _is_how_to_cancel(normalized, language),
            _is_subscription_status_check(normalized, language),
            _is_subscription_activation_issue(text, language),
            _is_premium_entitlement_issue(text, language),
            _is_human_support_request(normalized, language),
        )
    )


def _is_operator_issues_request(text: str) -> bool:
    normalized = _normalized(text)
    return any(
        token in normalized
        for token in (
            "частые проблемы",
            "что спрашивают",
            "какие проблемы",
            "common issues",
            "top issues",
            "frequent issues",
            "с чем чаще приходят",
            "что чаще всего спрашивают",
        )
    )


def _is_operator_manual_review_request(text: str) -> bool:
    normalized = _normalized(text)
    return any(
        token in normalized
        for token in (
            "ручной проверки",
            "ручная проверка",
            "требует ручной",
            "manual review",
            "needs manual",
            "нужна проверка",
        )
    )


def _is_operator_unresolved_request(text: str) -> bool:
    normalized = _normalized(text)
    return any(
        token in normalized
        for token in (
            "висят без решения",
            "без решения",
            "что висит",
            "unresolved",
            "open cases",
            "pending cases",
        )
    )


def _is_operator_daily_digest_request(text: str) -> bool:
    normalized = _normalized(text)
    return any(
        token in normalized
        for token in (
            "сводку за день",
            "итог за день",
            "дай сводку",
            "daily digest",
            "daily summary",
            "short summary",
            "короткую сводку",
        )
    )


def _is_operator_candidate_queue_request(text: str) -> bool:
    normalized = _normalized(text)
    return any(
        token in normalized
        for token in (
            "knowledge-кандидат",
            "knowledge candidate",
            "knowledge queue",
            "kb-кандидат",
            "kb candidate",
            "что я ещё не подтвердил",
            "что не подтверждено",
            "pending candidate",
            "pending candidates",
            "какие кандидаты ждут решения",
            "что ждёт подтверждения",
            "что ждёт моего решения",
            "что ещё на просмотре",
        )
    )


def _is_operator_kb_gap_request(text: str) -> bool:
    normalized = _normalized(text)
    return any(
        token in normalized
        for token in (
            "kb gaps",
            "knowledge gaps",
            "пробелы в kb",
            "пробелы в базе",
            "что чаще всего уходит в kb",
            "что чаще всего уходит в knowledge",
            "какие пробелы повторяются",
            "где у нас пробелы",
        )
    )


def _is_operator_last_manual_case_request(text: str) -> bool:
    normalized = _normalized(text)
    return any(
        token in normalized
        for token in (
            "последний ручной кейс",
            "последний кейс на ручную проверку",
            "какой последний кейс требует ручной проверки",
            "latest manual case",
        )
    )


def _is_operator_last_manual_case_details_request(text: str) -> bool:
    normalized = _normalized(text)
    return any(
        token in normalized
        for token in (
            "детали последнего ручного кейса",
            "покажи детали последнего ручного кейса",
            "подробно последний ручной кейс",
            "details of the latest manual case",
        )
    )


def _is_operator_last_support_reply_request(text: str) -> bool:
    normalized = _normalized(text)
    return any(
        token in normalized
        for token in (
            "что именно ответила поддержка",
            "что ответила поддержка",
            "последний ответ поддержки",
            "what did support reply",
            "latest support reply",
        )
    )


def _is_operator_last_premium_case_request(text: str) -> bool:
    normalized = _normalized(text)
    return any(
        token in normalized
        for token in (
            "последний премиум-кейс",
            "последний premium-кейс",
            "какой последний платный кейс",
            "latest premium case",
        )
    )


def _is_operator_recent_manual_cases_request(text: str) -> bool:
    normalized = _normalized(text)
    return any(
        token in normalized
        for token in (
            "последние ручные кейсы",
            "последние кейсы на ручную проверку",
            "покажи последние ручные кейсы",
            "recent manual cases",
        )
    )


def _is_operator_recent_premium_cases_request(text: str) -> bool:
    normalized = _normalized(text)
    return any(
        token in normalized
        for token in (
            "последние premium-кейсы",
            "последние премиум-кейсы",
            "покажи последние платные кейсы",
            "recent premium cases",
        )
    )


def _is_operator_recent_payment_cases_request(text: str) -> bool:
    normalized = _normalized(text)
    return any(
        token in normalized
        for token in (
            "последние кейсы по оплате",
            "последние оплаты",
            "покажи последние кейсы по оплате",
            "recent payment cases",
        )
    )


def _is_operator_close_last_manual_case_request(text: str) -> bool:
    normalized = _normalized(text)
    return any(
        token in normalized
        for token in (
            "закрой последний ручной кейс",
            "закрой кейс",
            "пометь последний кейс как решенный",
            "пометь кейс как решенный",
            "resolve last manual case",
            "close last manual case",
        )
    )


def _is_operator_last_candidate_full_request(text: str) -> bool:
    normalized = _normalized(text)
    return any(
        token in normalized
        for token in (
            "покажи последний кандидат целиком",
            "последний кандидат целиком",
            "покажи кандидат целиком",
            "show the latest candidate in full",
            "show last candidate fully",
        )
    )


def _is_operator_last_candidate_request(text: str) -> bool:
    normalized = _normalized(text)
    return any(
        token in normalized
        for token in (
            "последний knowledge-кандидат",
            "последний кандидат",
            "какой последний кандидат",
            "last knowledge candidate",
            "last candidate",
        )
    )


def _is_operator_payment_only_request(text: str) -> bool:
    normalized = _normalized(text)
    return any(
        token in normalized
        for token in (
            "только по оплате",
            "только оплаты",
            "по платежам",
            "по оплатам",
            "payment only",
            "payment issues only",
        )
    )


def _is_operator_outreach_search_request(text: str) -> bool:
    normalized = _normalized(text)
    has_search_verb = any(token in normalized for token in ("найди", "поищи", "спарси", "собери", "search", "find"))
    has_target = any(token in normalized for token in ("канал", "каналы", "чат", "чаты", "channel", "channels", "chat", "chats", "групп"))
    return has_search_verb and has_target


def _is_explicit_operator_summary_intent(text: str) -> bool:
    return any(
        checker(text)
        for checker in (
            _is_operator_summary_request,
            _is_operator_premium_request,
            _is_operator_issues_request,
            _is_operator_manual_review_request,
            _is_operator_unresolved_request,
            _is_operator_daily_digest_request,
            _is_operator_candidate_queue_request,
            _is_operator_kb_gap_request,
            _is_operator_last_manual_case_request,
            _is_operator_last_manual_case_details_request,
            _is_operator_last_support_reply_request,
            _is_operator_last_premium_case_request,
            _is_operator_recent_manual_cases_request,
            _is_operator_recent_premium_cases_request,
            _is_operator_recent_payment_cases_request,
            _is_operator_close_last_manual_case_request,
            _is_operator_last_candidate_full_request,
            _is_operator_last_candidate_request,
            _is_operator_payment_only_request,
        )
    )


def _parse_audience_value(raw: str, fragment: str) -> int:
    value = int(raw)
    lowered = fragment.lower()
    if "к" in lowered or "тыс" in lowered or "тысяч" in lowered:
        return value * 1000
    if value <= 50:
        return value * 1000
    return value


def _extract_outreach_params(text: str) -> dict[str, Any]:
    normalized = _normalized(text)

    limit = 5
    match_limit = re.search(r"(?:покажи|найди|собери)\s+(\d{1,2})", normalized)
    if match_limit:
        limit = max(1, min(20, int(match_limit.group(1))))

    member_cap = 10_000
    match_members = re.search(r"до\s+(\d{1,3})(?:\s*к|\s*тыс|\s*тысяч)?", normalized)
    if match_members:
        member_cap = _parse_audience_value(match_members.group(1), normalized[match_members.start(): match_members.end()])

    member_min = 0
    match_member_min = re.search(r"от\s+(\d{1,3})(?:\s*к|\s*тыс|\s*тысяч)?", normalized)
    if not match_member_min:
        match_member_min = re.search(r"не\s+меньше\s+(\d{1,3})(?:\s*к|\s*тыс|\s*тысяч)?", normalized)
    if not match_member_min:
        match_member_min = re.search(r"минимум\s+(\d{1,3})(?:\s*к|\s*тыс|\s*тысяч)?", normalized)
    if match_member_min:
        member_min = _parse_audience_value(
            match_member_min.group(1),
            normalized[match_member_min.start(): match_member_min.end()],
        )

    post_limit = 8
    if "живая аудитория" in normalized or "живой аудитори" in normalized:
        post_limit = 10

    topic = None
    match_topic = re.search(r"(?:по|про)\s+(.+)$", normalized)
    if match_topic:
        topic = match_topic.group(1).strip()
        topic = re.sub(r"\s+от\s+\d{1,3}(?:\s*к|\s*тыс|\s*тысяч)?(?:\s+до\s+\d{1,3}(?:\s*к|\s*тыс|\s*тысяч)?)?.*$", "", topic).strip()
        topic = re.sub(r"\s+не\s+меньше\s+\d{1,3}(?:\s*к|\s*тыс|\s*тысяч)?.*$", "", topic).strip()
        topic = re.sub(r"\s+минимум\s+\d{1,3}(?:\s*к|\s*тыс|\s*тысяч)?.*$", "", topic).strip()
        topic = re.sub(r"\s+до\s+\d.*$", "", topic).strip()
        topic = re.sub(r"\s+покажи\s+\d.*$", "", topic).strip()
        topic = re.sub(r"\s+с живой аудиторией.*$", "", topic).strip()

    if not topic:
        topic_queries = list(DEFAULT_OUTREACH_QUERIES)
    else:
        topic_queries = [topic]

    return {
        "queries": topic_queries,
        "limit": limit,
        "member_cap": member_cap,
        "member_min": member_min,
        "post_limit": post_limit,
        "live_only": ("живая аудитория" in normalized or "живой аудитор" in normalized),
        "entity_type": "chat" if any(token in normalized for token in ("чат", "чаты", "групп")) else "channel",
    }


def _render_outreach_shortlist(*, result: dict[str, Any], params: dict[str, Any], language: str) -> str:
    shortlist = list(result.get("shortlist") or [])
    entity_type = str(params.get("entity_type") or "channel")
    member_cap = int(params.get("member_cap") or 0)
    member_min = int(params.get("member_min") or 0)
    live_only = bool(params.get("live_only"))

    filtered: list[dict[str, Any]] = []
    for item in shortlist:
        member_count = int(item.get("member_count") or 0)
        if member_min and member_count and member_count < member_min:
            continue
        if member_cap and member_count and member_count > member_cap:
            continue
        if live_only and int(item.get("recent_posts_count") or 0) < 3:
            continue
        if entity_type == "channel" and str(item.get("type")) != "channel":
            continue
        if entity_type == "chat" and str(item.get("type")) != "chat":
            continue
        filtered.append(item)

    filtered = filtered[: int(params.get("limit") or 5)]
    if language == "en":
        if not filtered:
            return "I did not find a good shortlist for this query with the current filters."
        lines = [f"I found {len(filtered)} relevant {entity_type} result(s):"]
        for item in filtered:
            title = str(item.get("title") or "Untitled")
            link = str(item.get("link") or item.get("username") or "")
            score = float(item.get("score") or 0.0)
            members = int(item.get("member_count") or 0)
            niche = str(item.get("niche") or "other")
            recommendation = str(item.get("recommendation") or "review")
            summary = str(item.get("summary") or "")
            lines.append(
                f"- {title} | score {score:.1f} | members {members or 'unknown'} | niche {niche} | {recommendation}"
                + (f" | {link}" if link else "")
            )
            if summary:
                lines.append(f"  {summary}")
        return "\n".join(lines)

    if not filtered:
        return "Я не нашёл хорошего shortlist по этому запросу с текущими фильтрами."
    lines = [f"Я нашёл {len(filtered)} подходящих {('канал(ов)' if entity_type == 'channel' else 'чат(ов)')}:"] 
    for item in filtered:
        title = str(item.get("title") or "Без названия")
        link = str(item.get("link") or item.get("username") or "")
        score = float(item.get("score") or 0.0)
        members = int(item.get("member_count") or 0)
        niche = str(item.get("niche") or "other")
        recommendation = str(item.get("recommendation") or "review")
        summary = str(item.get("summary") or "")
        lines.append(
            f"- {title} | score {score:.1f} | аудитория {members or 'неизвестно'} | ниша {niche} | {recommendation}"
            + (f" | {link}" if link else "")
        )
        if summary:
            lines.append(f"  {summary}")
    return "\n".join(lines)


def _render_issue_bucket(bucket: str, language: str) -> str:
    ru = {
        "refund": "возвраты",
        "duplicate_charge": "двойные списания",
        "payment_failed": "ошибки оплаты",
        "activation_issue": "оплата прошла, но подписка не активировалась",
        "premium_entitlement": "Premium активен, но лимиты или функции не обновились",
        "subscribe": "оформление подписки",
        "cancel": "отмена подписки",
        "human_support": "запросы на живого оператора",
        "other": "прочее",
    }
    en = {
        "refund": "refunds",
        "duplicate_charge": "duplicate charges",
        "payment_failed": "payment failures",
        "activation_issue": "payment succeeded but subscription did not activate",
        "premium_entitlement": "Premium active but limits or features did not refresh",
        "subscribe": "subscription signup",
        "cancel": "subscription cancellation",
        "human_support": "human support requests",
        "other": "other",
    }
    mapping = en if language == "en" else ru
    return mapping.get(bucket, bucket)


def _should_mark_manual_review(*, reply_text: str, support_check: dict[str, Any] | None) -> bool:
    normalized_reply = _normalized(reply_text)
    diagnosis = str((support_check or {}).get("diagnosis") or "")
    if diagnosis in {
        "payment_confirmed_but_access_missing",
        "latest_payment_not_confirmed",
        "no_payment_found",
    }:
        return True
    return any(
        token in normalized_reply
        for token in (
            "ручн",
            "manual",
            "проверка с нашей стороны",
            "поддержка проверит",
            "needs manual",
            "manual verification",
        )
    )


def _determine_case_status(*, confident: bool, reply_text: str, support_check: dict[str, Any] | None) -> str:
    if _should_mark_manual_review(reply_text=reply_text, support_check=support_check):
        return "manual_review"
    if confident:
        return "resolved"
    return "open"


def build_operator_reply(
    *,
    operator_text: str,
    language: str,
    summary: dict[str, Any],
) -> str:
    threads_total = int(summary.get("threads_total") or 0)
    open_threads_total = int(summary.get("open_threads_total") or 0)
    manual_review_threads_total = int(summary.get("manual_review_threads_total") or 0)
    resolved_threads_total = int(summary.get("resolved_threads_total") or 0)
    user_messages_total = int(summary.get("user_messages_total") or 0)
    priority_threads_total = int(summary.get("priority_threads_total") or 0)
    pending_candidates_total = int(summary.get("pending_candidates_total") or 0)
    top_issues = list(summary.get("top_issues") or [])
    recent_threads = list(summary.get("recent_threads") or [])
    manual_review_threads = list(summary.get("manual_review_threads") or [])
    pending_candidates = list(summary.get("pending_candidates") or [])
    top_kb_gaps = list(summary.get("top_kb_gaps") or [])

    def _thread_snippet(item: dict[str, Any]) -> str:
        snippet = str(item.get("latest_user_message") or "").strip()
        if len(snippet) > 120:
            snippet = snippet[:117] + "..."
        return snippet or ("No user text captured yet." if language == "en" else "Текст пользователя пока не зафиксирован.")

    def _candidate_snippet(item: dict[str, Any]) -> str:
        title = str(item.get("suggested_title") or "").strip() or ("Untitled candidate" if language == "en" else "Кандидат без названия")
        reason = str(item.get("reason") or "").strip()
        return title + (f" — {reason}" if reason else "")

    def _render_thread_list(title: str, threads: list[dict[str, Any]]) -> str:
        if language == "en":
            if not threads:
                return f"{title}\n- No matching cases right now."
            lines = [title]
            for item in threads[:5]:
                bucket = _render_issue_bucket(str(item.get("issue_bucket") or "other"), language)
                lines.append(f"- [{bucket}] {_thread_snippet(item)}")
            return "\n".join(lines)
        if not threads:
            return f"{title}\n- Сейчас подходящих кейсов нет."
        lines = [title]
        for item in threads[:5]:
            bucket = _render_issue_bucket(str(item.get("issue_bucket") or "other"), language)
            lines.append(f"- [{bucket}] {_thread_snippet(item)}")
        return "\n".join(lines)

    if _is_operator_daily_digest_request(operator_text):
        if language == "en":
            lines = [
                f"Daily support digest: {threads_total} thread(s), {user_messages_total} incoming user message(s), {open_threads_total} open, {manual_review_threads_total} manual-review, {resolved_threads_total} resolved, {priority_threads_total} priority thread(s), {pending_candidates_total} pending knowledge candidate(s)."
            ]
            if top_issues:
                lines.append(
                    "Top issues: "
                    + ", ".join(
                        f"{_render_issue_bucket(str(item['bucket']), language)} ({int(item['count'])})"
                        for item in top_issues[:3]
                    )
                )
            if manual_review_threads:
                lines.append(f"Manual review queue: {len(manual_review_threads)} case(s).")
            return " ".join(lines)
        lines = [
            f"Короткая сводка за день: {threads_total} диалог(ов), {user_messages_total} входящих пользовательских сообщений, {open_threads_total} открытых, {manual_review_threads_total} на ручной проверке, {resolved_threads_total} закрытых, {priority_threads_total} priority кейс(ов), {pending_candidates_total} knowledge-кандидат(ов) на просмотр."
        ]
        if top_issues:
            lines.append(
                "Частые темы: "
                + ", ".join(
                    f"{_render_issue_bucket(str(item['bucket']), language)} ({int(item['count'])})"
                    for item in top_issues[:3]
                )
            )
        if manual_review_threads:
            lines.append(f"На ручной проверке сейчас {len(manual_review_threads)} кейс(ов).")
        return " ".join(lines)

    if _is_operator_last_manual_case_request(operator_text):
        if not manual_review_threads:
            return (
                "Right now I do not see a recent case that clearly requires manual review."
                if language == "en"
                else "Сейчас я не вижу свежего кейса, который явно требует ручной проверки."
            )
        item = manual_review_threads[0]
        bucket = _render_issue_bucket(str(item.get("issue_bucket") or "other"), language)
        return (
            f"The latest manual-review case is [{bucket}] {_thread_snippet(item)}"
            if language == "en"
            else f"Последний кейс на ручную проверку: [{bucket}] {_thread_snippet(item)}"
        )

    if _is_operator_last_manual_case_details_request(operator_text):
        if not manual_review_threads:
            return (
                "Right now I do not see a recent case that clearly requires manual review."
                if language == "en"
                else "Сейчас я не вижу свежего кейса, который явно требует ручной проверки."
            )
        item = manual_review_threads[0]
        bucket = _render_issue_bucket(str(item.get("issue_bucket") or "other"), language)
        user_text = str(item.get("latest_user_message") or "").strip() or (
            "No user text captured yet." if language == "en" else "Текст пользователя пока не зафиксирован."
        )
        assistant_text = str(item.get("latest_assistant_message") or "").strip() or (
            "No support reply captured yet." if language == "en" else "Ответ поддержки пока не зафиксирован."
        )
        if language == "en":
            return (
                f"Latest manual-review case details:\n"
                f"- Issue: {bucket}\n"
                f"- User message: {user_text}\n"
                f"- Support reply: {assistant_text}"
            )
        return (
            f"Детали последнего ручного кейса:\n"
            f"- Тема: {bucket}\n"
            f"- Сообщение пользователя: {user_text}\n"
            f"- Ответ поддержки: {assistant_text}"
        )

    if _is_operator_last_support_reply_request(operator_text):
        if not manual_review_threads:
            return (
                "Right now I do not see a recent manual-review case with a support reply."
                if language == "en"
                else "Сейчас я не вижу свежего ручного кейса с зафиксированным ответом поддержки."
            )
        assistant_text = str(manual_review_threads[0].get("latest_assistant_message") or "").strip()
        if not assistant_text:
            return (
                "The latest manual-review case does not have a captured support reply yet."
                if language == "en"
                else "У последнего ручного кейса пока нет зафиксированного ответа поддержки."
            )
        return (
            f"The latest support reply was:\n{assistant_text}"
            if language == "en"
            else f"Последний ответ поддержки был таким:\n{assistant_text}"
        )

    if _is_operator_last_premium_case_request(operator_text):
        premium_threads = [item for item in recent_threads if item.get("priority_support")]
        if not premium_threads:
            return (
                "Right now I do not see a recent Premium or priority support case."
                if language == "en"
                else "Сейчас я не вижу свежего Premium или priority support кейса."
            )
        item = premium_threads[0]
        return (
            f"The latest Premium case is {_thread_snippet(item)}"
            if language == "en"
            else f"Последний Premium-кейс: {_thread_snippet(item)}"
        )

    if _is_operator_recent_manual_cases_request(operator_text):
        return _render_thread_list(
            "Recent manual-review cases:" if language == "en" else "Последние кейсы на ручную проверку:",
            manual_review_threads,
        )

    if _is_operator_recent_premium_cases_request(operator_text):
        premium_threads = [item for item in recent_threads if item.get("priority_support")]
        return _render_thread_list(
            "Recent Premium cases:" if language == "en" else "Последние Premium-кейсы:",
            premium_threads,
        )

    if _is_operator_recent_payment_cases_request(operator_text):
        payment_buckets = {"payment_failed", "duplicate_charge", "activation_issue", "refund"}
        payment_threads = [item for item in recent_threads if str(item.get("issue_bucket") or "") in payment_buckets]
        return _render_thread_list(
            "Recent payment-related cases:" if language == "en" else "Последние кейсы по оплате:",
            payment_threads,
        )

    if _is_operator_last_candidate_request(operator_text):
        if not pending_candidates:
            return (
                "Right now I do not see a pending knowledge candidate."
                if language == "en"
                else "Сейчас я не вижу knowledge-кандидата в статусе pending."
            )
        return (
            f"The latest pending knowledge candidate is {_candidate_snippet(pending_candidates[0])}"
            if language == "en"
            else f"Последний knowledge-кандидат в pending: {_candidate_snippet(pending_candidates[0])}"
        )

    if _is_operator_last_candidate_full_request(operator_text):
        if not pending_candidates:
            return (
                "Right now I do not see a pending knowledge candidate."
                if language == "en"
                else "Сейчас я не вижу knowledge-кандидата в статусе pending."
            )
        item = pending_candidates[0]
        title = str(item.get("suggested_title") or "").strip() or ("Untitled candidate" if language == "en" else "Кандидат без названия")
        content = str(item.get("suggested_content") or "").strip() or (
            "No candidate content captured yet." if language == "en" else "Содержимое кандидата пока не зафиксировано."
        )
        reason = str(item.get("reason") or "").strip()
        if language == "en":
            return (
                f"Latest pending knowledge candidate:\n"
                f"- Title: {title}\n"
                f"- Reason: {reason or 'No reason recorded.'}\n"
                f"- Content: {content}"
            )
        return (
            f"Последний knowledge-кандидат в pending:\n"
            f"- Заголовок: {title}\n"
            f"- Причина: {reason or 'Причина не зафиксирована.'}\n"
            f"- Содержимое: {content}"
        )

    if _is_operator_payment_only_request(operator_text):
        payment_buckets = {"payment_failed", "duplicate_charge", "activation_issue", "refund"}
        payment_issues = [item for item in top_issues if str(item.get("bucket")) in payment_buckets]
        if language == "en":
            if not payment_issues:
                return "Right now I do not see a strong recent pattern specifically in payment-related support issues."
            lines = ["Recent payment-related support pattern:"]
            for item in payment_issues:
                lines.append(f"- {_render_issue_bucket(str(item['bucket']), language)}: {int(item['count'])}")
            return "\n".join(lines)
        if not payment_issues:
            return "Сейчас я не вижу выраженной недавней картины именно по вопросам оплаты."
        lines = ["По недавним обращениям по оплате картина такая:"]
        for item in payment_issues:
            lines.append(f"- {_render_issue_bucket(str(item['bucket']), language)}: {int(item['count'])}")
        return "\n".join(lines)

    if _is_operator_candidate_queue_request(operator_text):
        if language == "en":
            if not pending_candidates:
                return "Right now I do not see pending knowledge candidates that still need your review."
            lines = [f"Right now I see {len(pending_candidates)} pending knowledge candidate(s):"]
            for item in pending_candidates[:5]:
                title = str(item.get("suggested_title") or "Untitled candidate").strip()
                reason = str(item.get("reason") or "").strip()
                lines.append(f"- {title}" + (f" — {reason}" if reason else ""))
            return "\n".join(lines)
        if not pending_candidates:
            return "Сейчас я не вижу knowledge-кандидатов, которые ещё ждут вашего решения."
        lines = [f"Сейчас я вижу {len(pending_candidates)} knowledge-кандидат(ов), которые ещё ждут вашего решения:"]
        for item in pending_candidates[:5]:
            title = str(item.get("suggested_title") or "Без названия").strip()
            reason = str(item.get("reason") or "").strip()
            lines.append(f"- {title}" + (f" — {reason}" if reason else ""))
        return "\n".join(lines)

    if _is_operator_kb_gap_request(operator_text):
        if language == "en":
            if not top_kb_gaps:
                return "I do not yet see a stable pattern in KB gaps from pending knowledge candidates."
            lines = ["The most repeated KB gaps right now:"]
            for item in top_kb_gaps[:5]:
                lines.append(f"- {str(item['title'])}: {int(item['count'])}")
            return "\n".join(lines)
        if not top_kb_gaps:
            return "Пока я не вижу устойчивой картины по повторяющимся пробелам в KB."
        lines = ["Сейчас чаще всего повторяются такие пробелы в KB:"]
        for item in top_kb_gaps[:5]:
            lines.append(f"- {str(item['title'])}: {int(item['count'])}")
        return "\n".join(lines)

    if _is_operator_premium_request(operator_text):
        if language == "en":
            if priority_threads_total == 0:
                return "Today I do not see any Premium or priority support threads yet."
            latest = recent_threads[:3]
            lines = [
                f"Today I see {priority_threads_total} Premium or priority support thread(s).",
            ]
            for item in latest:
                if not item.get("priority_support"):
                    continue
                snippet = str(item.get("latest_user_message") or "").strip()
                if len(snippet) > 120:
                    snippet = snippet[:117] + "..."
                lines.append(f"- {snippet or 'No user text captured yet.'}")
            return "\n".join(lines)
        if priority_threads_total == 0:
            return "Сегодня я пока не вижу Premium или priority support кейсов."
        lines = [f"Сегодня я вижу {priority_threads_total} Premium или priority support кейс(ов)."]
        added = 0
        for item in recent_threads:
            if not item.get("priority_support"):
                continue
            snippet = str(item.get("latest_user_message") or "").strip()
            if len(snippet) > 120:
                snippet = snippet[:117] + "..."
            lines.append(f"- {snippet or 'Текст пользователя пока не зафиксирован.'}")
            added += 1
            if added >= 3:
                break
        return "\n".join(lines)

    if _is_operator_manual_review_request(operator_text) or _is_operator_unresolved_request(operator_text):
        if language == "en":
            if not manual_review_threads:
                return "Right now I do not see active support cases that clearly require manual review."
            lines = [f"Right now I see {len(manual_review_threads)} case(s) that likely need manual review:"]
            for item in manual_review_threads[:5]:
                bucket = _render_issue_bucket(str(item.get("issue_bucket") or "other"), language)
                lines.append(f"- [{bucket}] {_thread_snippet(item)}")
            return "\n".join(lines)
        if not manual_review_threads:
            return "Сейчас я не вижу активных support-кейсов, которые явно требуют ручной проверки."
        lines = [f"Сейчас я вижу {len(manual_review_threads)} кейс(ов), которые, скорее всего, требуют ручной проверки:"]
        for item in manual_review_threads[:5]:
            bucket = _render_issue_bucket(str(item.get("issue_bucket") or "other"), language)
            lines.append(f"- [{bucket}] {_thread_snippet(item)}")
        return "\n".join(lines)

    if _is_operator_issues_request(operator_text):
        if language == "en":
            if not top_issues:
                return "I do not yet see a stable enough issue pattern in the recent support traffic."
            lines = ["Recent support issue pattern:"]
            for item in top_issues:
                lines.append(f"- {_render_issue_bucket(str(item['bucket']), language)}: {int(item['count'])}")
            return "\n".join(lines)
        if not top_issues:
            return "Пока я не вижу достаточно устойчивой картины по частым проблемам в последних support-обращениях."
        lines = ["По последним support-обращениям картина сейчас такая:"]
        for item in top_issues:
            lines.append(f"- {_render_issue_bucket(str(item['bucket']), language)}: {int(item['count'])}")
        return "\n".join(lines)

    if language == "en":
        lines = [
            f"Today I see {threads_total} support thread(s) and {user_messages_total} incoming user message(s).",
            f"Open threads: {open_threads_total}. Manual-review threads: {manual_review_threads_total}. Resolved threads: {resolved_threads_total}. Priority support threads: {priority_threads_total}. Pending knowledge candidates: {pending_candidates_total}.",
        ]
        if top_issues:
            top = top_issues[0]
            lines.append(f"The top current issue is {_render_issue_bucket(str(top['bucket']), language)} ({int(top['count'])}).")
        return " ".join(lines)

    lines = [
        f"Сегодня я вижу {threads_total} support-диалог(ов) и {user_messages_total} входящих пользовательских сообщений.",
        f"Открытых кейсов: {open_threads_total}. На ручной проверке: {manual_review_threads_total}. Закрытых: {resolved_threads_total}. Priority support кейсов: {priority_threads_total}. Непросмотренных knowledge-кандидатов: {pending_candidates_total}.",
    ]
    if top_issues:
        top = top_issues[0]
        lines.append(f"Самая частая текущая проблема: {_render_issue_bucket(str(top['bucket']), language)} ({int(top['count'])}).")
    return " ".join(lines)


async def maybe_handle_operator_request(
    tg_client: TelegramClient,
    message: Message,
) -> dict[str, Any] | None:
    settings = get_telegram_settings()
    sender_id = getattr(message, "sender_id", None)
    if not settings.is_trusted_operator(sender_id):
        return None

    operator_text = (message.message or "").strip()
    if not operator_text:
        return None

    language = normalize_language(None) or detect_language(operator_text)
    normalized_text = _normalized(operator_text)

    if language == "en" and normalized_text in EN_GREETINGS:
        reply_text = "Hello. What do you want me to check: support, channels, payments, or current cases?"
        sent = await _send_reply_for_message(
            tg_client,
            message,
            reply_text=reply_text,
        )
        return {
            "ok": True,
            "mode": "operator_mode",
            "message_id": message.id,
            "reply_text": reply_text,
            "sent": True,
            "sent_message": sent,
        }

    if language == "ru" and normalized_text in RU_GREETINGS:
        reply_text = "Здравствуйте. Что именно посмотреть: поддержку, каналы, оплаты или текущие кейсы?"
        sent = await _send_reply_for_message(
            tg_client,
            message,
            reply_text=reply_text,
        )
        return {
            "ok": True,
            "mode": "operator_mode",
            "message_id": message.id,
            "reply_text": reply_text,
            "sent": True,
            "sent_message": sent,
        }

    if _is_thanks(normalized_text, language):
        reply_text = "Пожалуйста." if language == "ru" else "You're welcome."
        sent = await _send_reply_for_message(
            tg_client,
            message,
            reply_text=reply_text,
        )
        return {
            "ok": True,
            "mode": "operator_mode",
            "message_id": message.id,
            "reply_text": reply_text,
            "sent": True,
            "sent_message": sent,
        }

    if _is_goodbye(normalized_text, language):
        reply_text = "Всего доброго." if language == "ru" else "Goodbye."
        sent = await _send_reply_for_message(
            tg_client,
            message,
            reply_text=reply_text,
        )
        return {
            "ok": True,
            "mode": "operator_mode",
            "message_id": message.id,
            "reply_text": reply_text,
            "sent": True,
            "sent_message": sent,
        }

    if _is_operator_outreach_search_request(operator_text):
        params = _extract_outreach_params(operator_text)
        result = await search_telegram_outreach(
            tg_client,
            queries=list(params["queries"]),
            limit_per_query=20,
            post_limit=int(params["post_limit"]),
        )
        reply_text = _render_outreach_shortlist(result=result, params=params, language=language)
        sent = await _send_reply_for_message(
            tg_client,
            message,
            reply_text=reply_text,
        )
        return {
            "ok": True,
            "mode": "operator_outreach_search",
            "message_id": message.id,
            "params": params,
            "result_count": len(list((result or {}).get("shortlist") or [])),
            "reply_text": reply_text,
            "sent": True,
            "sent_message": sent,
        }

    if not _is_explicit_operator_summary_intent(operator_text):
        reply_text = (
            "Могу помочь как агент. Можете писать обычным языком. Если нужен отчёт или поиск, скажите прямо: например, `что по поддержке`, `что требует ручной проверки` или `найди каналы по похудению до 10к`."
            if language == "ru"
            else "I can help as an operator agent. You can write normally. If you want a report or a search, ask directly, for example: `what is going on in support`, `what needs manual review`, or `find channels about weight loss under 10k`."
        )
        sent = await _send_reply_for_message(
            tg_client,
            message,
            reply_text=reply_text,
        )
        return {
            "ok": True,
            "mode": "operator_mode",
            "message_id": message.id,
            "reply_text": reply_text,
            "sent": True,
            "sent_message": sent,
        }

    async with httpx.AsyncClient() as kb_client:
        summary = await kb_get(kb_client, "/kb/support-summary", {"days": 1, "include_tests": False})
        if _is_operator_close_last_manual_case_request(operator_text):
            manual_review_threads = list(summary.get("manual_review_threads") or [])
            if not manual_review_threads:
                reply_text = (
                    "Right now I do not see a manual-review case to close."
                    if language == "en"
                    else "Сейчас я не вижу ручного кейса, который можно закрыть."
                )
            else:
                latest = manual_review_threads[0]
                status_update = await kb_post(
                    kb_client,
                    "/kb/support-threads/status",
                    {
                        "thread_id": str(latest["id"]),
                        "case_status": "resolved",
                        "resolution_note": "Closed by owner in operator flow.",
                        "reviewed_by": f"telegram:{sender_id}",
                    },
                )
                snippet = str(latest.get("latest_user_message") or "").strip()
                if len(snippet) > 120:
                    snippet = snippet[:117] + "..."
                reply_text = (
                    f"Closed the latest manual-review case: {snippet or str(status_update['thread_id'])}"
                    if language == "en"
                    else f"Закрыл последний ручной кейс: {snippet or str(status_update['thread_id'])}"
                )
            sent = await _send_reply_for_message(
                tg_client,
                message,
                reply_text=reply_text,
            )
            return {
                "ok": True,
                "mode": "operator_mode",
                "message_id": message.id,
                "summary": summary,
                "reply_text": reply_text,
                "sent": True,
                "sent_message": sent,
            }

    reply_text = build_operator_reply(
        operator_text=operator_text,
        language=language,
        summary=summary,
    )
    sent = await _send_reply_for_message(
        tg_client,
        message,
        reply_text=reply_text,
    )
    return {
        "ok": True,
        "mode": "operator_mode",
        "message_id": message.id,
        "summary": summary,
        "reply_text": reply_text,
        "sent": True,
        "sent_message": sent,
    }


async def maybe_handle_owner_candidate_review(
    tg_client: TelegramClient,
    message: Message,
) -> dict[str, Any] | None:
    settings = get_telegram_settings()
    sender_id = getattr(message, "sender_id", None)
    if not settings.is_trusted_operator(sender_id):
        return None

    action, edited_content = parse_owner_review_action(message.message or "")
    if action is None:
        return None

    if not hasattr(message, "get_reply_message"):
        return None
    replied = await message.get_reply_message()
    if replied is None:
        return None
    candidate_id = extract_candidate_id(replied.message or "")
    if not candidate_id:
        return None

    async with httpx.AsyncClient() as kb_client:
        review = await kb_post(
            kb_client,
            "/kb/proposed-updates/review",
            {
                "id": candidate_id,
                "action": action,
                "reviewed_by": f"telegram:{sender_id}",
                "edited_content": edited_content,
            },
        )

    if action == "approve":
        reply_text = f"Кандидат {candidate_id} подтверждён и добавлен в базу знаний."
    elif action == "reject":
        reply_text = f"Кандидат {candidate_id} отклонён."
    else:
        reply_text = f"Кандидат {candidate_id} обновлён по вашей правке и добавлен в базу знаний."

    sent = await _send_reply_for_message(
        tg_client,
        message,
        reply_text=reply_text,
    )
    return {
        "ok": True,
        "mode": "owner_candidate_review",
        "candidate_id": candidate_id,
        "review": review,
        "sent": True,
        "sent_message": sent,
    }


async def fitmentor_support_subscription_check(
    client: httpx.AsyncClient,
    *,
    telegram_id: int,
) -> dict[str, Any] | None:
    settings = get_telegram_settings()
    base_url = settings.fitmentor_internal_base_url.rstrip("/")
    token = settings.fitmentor_support_internal_token.strip()
    if not base_url or not token or telegram_id <= 0:
        return None

    response = await client.post(
        f"{base_url}/api/internal/support/subscription-check",
        json={"telegram_id": telegram_id},
        headers={"X-Support-Token": token},
        timeout=20.0,
    )
    response.raise_for_status()
    data = response.json()
    return data if isinstance(data, dict) else None


def build_reply(
    user_text: str,
    language: str,
    kb_items: list[dict[str, Any]],
    support_check: dict[str, Any] | None = None,
) -> tuple[str, bool]:
    normalized_text = _normalized(user_text)
    normalized_simple_text = _normalized_simple_phrase(user_text)
    if normalized_text:
        if language == "en" and normalized_simple_text in EN_GREETINGS:
            return (
                "Hello. How can I help you with FitMentor today?",
                True,
            )
        if language == "ru" and normalized_simple_text in RU_GREETINGS:
            return (
                "Здравствуйте. Чем могу помочь вам по FitMentor?",
                True,
            )
        if _is_thanks(normalized_text, language):
            return (
                "You're welcome."
                if language == "en"
                else "Пожалуйста.",
                True,
            )
        if _is_goodbye(normalized_text, language):
            return (
                "Goodbye."
                if language == "en"
                else "Всего доброго.",
                True,
            )

    if _is_subscription_activation_issue(user_text, language):
        diagnosis = str((support_check or {}).get("diagnosis") or "")
        if diagnosis in {"payment_confirmed_and_access_granted", "subscription_active"}:
            return (
                (
                    "I checked the subscription status. Access is already active for this Telegram account. Please reopen the bot and check again. If the problem remains, describe exactly where access is missing."
                )
                if language == "en"
                else (
                    "Я проверил статус подписки. Для этого Telegram-аккаунта доступ уже активен. Пожалуйста, заново откройте бота и проверьте ещё раз. Если проблема останется, напишите, где именно не хватает доступа."
                ),
                True,
            )
        if diagnosis == "payment_pending":
            return (
                (
                    "I checked the payment status. The payment for this Telegram account is still pending and has not been confirmed yet. Please complete the payment flow or wait a little, then check again."
                )
                if language == "en"
                else (
                    "Я проверил статус платежа. Для этого Telegram-аккаунта платёж ещё в обработке и пока не подтверждён. Пожалуйста, завершите оплату или подождите немного, затем проверьте ещё раз."
                ),
                True,
            )
        if diagnosis == "payment_confirmed_but_access_missing":
            return (
                (
                    "I checked the status: the payment is confirmed, but access has not updated yet. We need to check this manually on our side. Please send the payment date and amount so support can finish the activation."
                )
                if language == "en"
                else (
                    "Я проверил статус: платёж подтверждён, но доступ ещё не обновился. Мы проверим это вручную со своей стороны. Пришлите, пожалуйста, дату платежа и сумму, чтобы поддержка завершила активацию."
                ),
                False,
            )
        if diagnosis == "latest_payment_not_confirmed":
            return (
                (
                    "I checked the latest payment status, and it is not confirmed yet. Please send the payment date, amount, and confirmation details if you have them so support can review the case."
                )
                if language == "en"
                else (
                    "Я проверил статус последнего платежа: подтверждения оплаты пока нет. Пришлите, пожалуйста, дату платежа, сумму и подтверждение оплаты, если оно у вас есть, чтобы поддержка проверила кейс."
                ),
                False,
            )
        if diagnosis == "no_payment_found":
            return (
                (
                    "I checked the status for this Telegram account and do not see an active subscription or a recorded payment yet. Please send the payment date, amount, and any payment confirmation or receipt so support can review the case manually."
                )
                if language == "en"
                else (
                    "Я проверил статус для этого Telegram-аккаунта и пока не вижу активной подписки или найденного платежа. Пришлите, пожалуйста, дату платежа, сумму и подтверждение оплаты или чек, чтобы поддержка могла проверить кейс вручную."
                ),
                False,
            )
        if language == "en":
            return (
                "Understood. If payment succeeded but the subscription did not activate, please send your Telegram account, payment date, amount, and any payment confirmation. Support will check the payment and activation manually.",
                False,
            )
        return (
            "Понял. Если оплата прошла, а подписка не активировалась, пришлите, пожалуйста, ваш Telegram-аккаунт, дату платежа, сумму и, если есть, подтверждение оплаты. Поддержка вручную проверит платёж и активацию.",
            False,
        )

    if _is_premium_entitlement_issue(user_text, language):
        diagnosis = str((support_check or {}).get("diagnosis") or "")
        feature_hint = _extract_premium_feature_hint(user_text, language)
        if diagnosis in {"payment_confirmed_and_access_granted", "subscription_active"}:
            if feature_hint == "ai_limit":
                return (
                    (
                        "I checked the status: Premium is already active for this Telegram account. If the AI message limit did not update after payment, please reopen the bot and check the limit once more. If it is still old, send a screenshot and we will verify the limit refresh on our side."
                    )
                    if language == "en"
                    else (
                        "Я проверил статус: для этого Telegram-аккаунта Premium уже активен. Если после оплаты не обновился лимит AI-сообщений, пожалуйста, заново откройте бота и проверьте лимит ещё раз. Если лимит всё ещё старый, пришлите скриншот, и мы проверим обновление со своей стороны."
                    ),
                    False,
                )
            if feature_hint == "weekly_report":
                return (
                    (
                        "I checked the status: Premium is already active for this Telegram account. If the weekly report is still unavailable, please send a screenshot or describe where exactly it is missing, and we will verify it on our side."
                    )
                    if language == "en"
                    else (
                        "Я проверил статус: для этого Telegram-аккаунта Premium уже активен. Если weekly report всё ещё недоступен, пришлите скриншот или напишите, где именно он не отображается, и мы проверим это со своей стороны."
                    ),
                    False,
                )
            if feature_hint == "recipes":
                return (
                    (
                        "I checked the status: Premium is already active for this Telegram account. If recipes are still unavailable, please send a screenshot or describe where exactly they are missing, and we will verify it on our side."
                    )
                    if language == "en"
                    else (
                        "Я проверил статус: для этого Telegram-аккаунта Premium уже активен. Если рецепты всё ещё недоступны, пришлите скриншот или напишите, где именно они не открываются, и мы проверим это со своей стороны."
                    ),
                    False,
                )
            return (
                (
                    "I checked the status: Premium is already active for this Telegram account. Please tell me which exact limit or feature did not update after payment, and we will check it on our side."
                )
                if language == "en"
                else (
                    "Я проверил статус: для этого Telegram-аккаунта Premium уже активен. Напишите, пожалуйста, какой именно лимит или функция не обновились после оплаты, и мы проверим это со своей стороны."
                ),
                False,
            )
        if diagnosis == "payment_pending":
            return (
                (
                    "I checked the payment status. The latest payment is still pending, so Premium limits or features may not have updated yet. Please wait a little or complete the payment flow, then check again."
                )
                if language == "en"
                else (
                    "Я проверил статус платежа. Последний платёж ещё в обработке, поэтому Premium-лимиты или функции могли ещё не обновиться. Пожалуйста, подождите немного или завершите оплату, затем проверьте ещё раз."
                ),
                True,
            )
        if diagnosis == "no_payment_found":
            return (
                (
                    "I checked the status for this Telegram account and do not see an active paid Premium subscription or a recorded payment yet. Please send the payment date, amount, and payment confirmation so support can review the case."
                )
                if language == "en"
                else (
                    "Я проверил статус для этого Telegram-аккаунта и пока не вижу активной платной Premium-подписки или найденного платежа. Пришлите, пожалуйста, дату платежа, сумму и подтверждение оплаты, чтобы поддержка проверила кейс."
                ),
                False,
            )
        return (
            (
                "Understood. If Premium was paid but the limits or Premium features did not update, please send your Telegram account, payment date, amount, and tell us which limit or feature is still unavailable. Support will check the payment and the access update."
            )
            if language == "en"
            else (
                "Понял. Если Premium оплачен, но лимиты или Premium-функции не обновились, пришлите, пожалуйста, ваш Telegram-аккаунт, дату платежа, сумму и уточните, какой именно лимит или функция всё ещё недоступны. Поддержка проверит оплату и обновление доступа."
            ),
            False,
        )

    if _is_payment_failed(normalized_text, language):
        return (
            (
                "If payment does not go through, please send the payment date, amount, payment method, and the exact error if you saw one. Support will check what happened and tell you the next step."
            )
            if language == "en"
            else (
                "Если оплата не проходит, пришлите, пожалуйста, дату попытки оплаты, сумму, способ оплаты и точный текст ошибки, если он был. Поддержка проверит ситуацию и подскажет, что делать дальше."
            ),
            False,
        )

    if _is_duplicate_charge(normalized_text, language):
        return (
            (
                "If you were charged twice, please send your Telegram account, payment date, amount, and both payment confirmations if available. Support will verify the charges manually."
            )
            if language == "en"
            else (
                "Если у вас было двойное списание, пришлите, пожалуйста, ваш Telegram-аккаунт, дату платежа, сумму и оба подтверждения оплаты, если они есть. Поддержка вручную проверит списания."
            ),
            False,
        )

    if _is_refund_request(normalized_text, language):
        return (
            (
                "Refunds are not the default outcome. Please send your Telegram account, payment date, amount, and the reason for the request. Support will review the request under FitMentor's refund policy."
            )
            if language == "en"
            else (
                "Возврат не является стандартным исходом по умолчанию. Пришлите, пожалуйста, ваш Telegram-аккаунт, дату платежа, сумму и причину запроса. Поддержка рассмотрит обращение по правилам Refund Policy FitMentor."
            ),
            False,
        )

    if _is_how_to_subscribe(normalized_text, language):
        return (
            (
                "You can choose a FitMentor plan and complete payment through the service flow in Telegram. If you need help choosing a plan, describe what you want from FitMentor and support will guide you."
            )
            if language == "en"
            else (
                "Оформить подписку можно через сценарий оплаты внутри FitMentor в Telegram. Если нужна помощь с выбором тарифа, напишите, что именно вы хотите от FitMentor, и поддержка подскажет подходящий вариант."
            ),
            True,
        )

    if _is_how_to_cancel(normalized_text, language):
        return (
            (
                "Please send your Telegram account and clarify which subscription you want to cancel. Support will tell you the next step and check the current status."
            )
            if language == "en"
            else (
                "Пришлите, пожалуйста, ваш Telegram-аккаунт и уточните, какую именно подписку вы хотите отменить. Поддержка подскажет следующий шаг и проверит текущий статус."
            ),
            False,
        )

    if _is_subscription_status_check(normalized_text, language):
        diagnosis = str((support_check or {}).get("diagnosis") or "")
        subscription = (support_check or {}).get("subscription") or {}
        tier_name = str(subscription.get("effective_tier_name") or subscription.get("current_tier_name") or "")
        until = str(subscription.get("subscription_until") or "")
        if diagnosis in {"subscription_active", "payment_confirmed_and_access_granted"}:
            return (
                (
                    f"I checked the subscription status. Your current access is active"
                    + (f" ({tier_name})" if tier_name else "")
                    + (f" until {until}." if until else ".")
                )
                if language == "en"
                else (
                    f"Я проверил статус подписки. Сейчас доступ активен"
                    + (f" ({tier_name})" if tier_name else "")
                    + (f" до {until}." if until else ".")
                ),
                True,
            )
        if diagnosis == "payment_pending":
            return (
                (
                    "I checked the subscription status. The latest payment is still pending, so access has not been activated yet."
                )
                if language == "en"
                else (
                    "Я проверил статус подписки. Последний платёж ещё в обработке, поэтому доступ пока не активирован."
                ),
                True,
            )
        if diagnosis == "no_payment_found":
            return (
                (
                    "I checked the subscription status. I do not see an active paid subscription or a recent payment for this Telegram account."
                )
                if language == "en"
                else (
                    "Я проверил статус подписки. Для этого Telegram-аккаунта я не вижу активной платной подписки или недавнего платежа."
                ),
                True,
            )
        return (
            (
                "Please send your Telegram account and, if relevant, the payment date. Support will check the current subscription status manually."
            )
            if language == "en"
            else (
                "Пришлите, пожалуйста, ваш Telegram-аккаунт и, если это связано с оплатой, дату платежа. Поддержка вручную проверит текущий статус подписки."
            ),
            False,
        )

    if _is_human_support_request(normalized_text, language):
        return (
            (
                "Understood. Please describe the issue briefly and include your Telegram account if the question is about payment or access. A support specialist will review it."
            )
            if language == "en"
            else (
                "Понял. Кратко опишите проблему и укажите ваш Telegram-аккаунт, если вопрос связан с оплатой или доступом. Обращение проверит специалист поддержки."
            ),
            False,
        )

    if kb_items:
        top = kb_items[0]
        return str(top["content"]).strip(), True

    if _is_payment_or_access_context(user_text, language):
        if language == "en":
            return (
                "I could not find a clear approved answer yet. Please send your Telegram account, payment date, amount, and any payment confirmation details so support can review this manually.",
                False,
            )
        return (
            "Я пока не нашёл точного утверждённого ответа. Пришлите, пожалуйста, ваш Telegram-аккаунт, дату платежа, сумму и, если есть, подтверждение оплаты, чтобы поддержка могла проверить это вручную.",
            False,
        )

    if language == "en":
        return (
            "What is your question? I will try to help. If this is about payment or access, include your Telegram account and any relevant payment details.",
            False,
        )

    return (
        "Какой у вас вопрос? Постараюсь помочь. Если это про оплату или доступ, сразу укажите Telegram-аккаунт и данные платежа, если они есть.",
        False,
    )


async def maybe_create_proposed_update(
    kb_client: httpx.AsyncClient,
    *,
    user_text: str,
    reply_text: str,
    language: str,
    source: str,
    support_check: dict[str, Any] | None,
) -> dict[str, Any] | None:
    draft = build_candidate_knowledge_draft(
        user_text=user_text,
        reply_text=reply_text,
        language=language,
        support_check=support_check,
    )
    if draft is None:
        return None

    result = await kb_post(
        kb_client,
        "/kb/proposed-updates",
        {
            "source": source,
            "suggested_category": draft["category"],
            "suggested_title": draft["title"],
            "suggested_content": draft["content"],
            "reason": draft["reason"],
            "evidence": {
                "language": language,
                "user_text": user_text,
                "draft_reply": reply_text,
                "support_check_diagnosis": (support_check or {}).get("diagnosis"),
                "priority_support": _is_priority_support(support_check),
            },
        },
    )
    if not isinstance(result, dict):
        return None
    return {
        **result,
        "suggested_category": draft["category"],
        "suggested_title": draft["title"],
        "suggested_content": draft["content"],
        "reason": draft["reason"],
        "evidence": {
            "language": language,
            "user_text": user_text,
            "draft_reply": reply_text,
            "support_check_diagnosis": (support_check or {}).get("diagnosis"),
            "priority_support": _is_priority_support(support_check),
        },
    }


def build_owner_candidate_notification(
    *,
    candidate_id: str,
    user_text: str,
    suggested_title: str,
    suggested_content: str,
    language: str,
    reason: str,
    priority_support: bool,
) -> str:
    priority_line = (
        ("Priority: Premium\n" if priority_support else "Priority: standard\n")
        if language == "en"
        else ("Приоритет: Premium\n" if priority_support else "Приоритет: standard\n")
    )
    if language == "en":
        return (
            "New candidate knowledge draft\n\n"
            f"ID: {candidate_id}\n"
            f"Reason: {reason}\n\n"
            f"{priority_line}\n"
            f"User case:\n{user_text}\n\n"
            f"Suggested title:\n{suggested_title}\n\n"
            f"Suggested KB card:\n{suggested_content}\n\n"
            "Reply to this message in natural language, for example:\n"
            "- approve\n"
            "- do not add it\n"
            "- edit like this: ..."
        )

    return (
        "Новый candidate knowledge draft\n\n"
        f"ID: {candidate_id}\n"
        f"Причина: {reason}\n\n"
        f"{priority_line}\n"
        f"Кейс пользователя:\n{user_text}\n\n"
        f"Предлагаемый заголовок:\n{suggested_title}\n\n"
        f"Предлагаемая KB-карточка:\n{suggested_content}\n\n"
        "Ответьте на это сообщение обычным языком, например:\n"
        "- подтверждаю\n"
        "- не добавляй\n"
        "- исправь так: ..."
    )


async def notify_owner_about_candidate(
    tg_client: TelegramClient,
    *,
    candidate: dict[str, Any],
    user_text: str,
    language: str,
    priority_support: bool,
) -> dict[str, Any] | None:
    settings = get_telegram_settings()
    owner_id = settings.telegram_owner_user_id
    candidate_id = str(candidate.get("id") or "").strip()
    if not owner_id or not candidate_id:
        return None

    reason = str(candidate.get("status") or "pending")
    evidence = candidate.get("evidence") or {}
    if isinstance(evidence, str):
        try:
            evidence = json.loads(evidence)
        except Exception:
            evidence = {}
    suggested_title = str(candidate.get("suggested_title") or "").strip()
    suggested_content = str(candidate.get("suggested_content") or "").strip()
    sent = await tg_client.send_message(
        int(owner_id),
        build_owner_candidate_notification(
            candidate_id=candidate_id,
            user_text=user_text,
            suggested_title=suggested_title,
            suggested_content=suggested_content,
            language=language,
            reason=reason,
            priority_support=bool(evidence.get("priority_support", priority_support)),
        ),
    )
    return {
        "candidate_id": candidate_id,
        "owner_chat_id": getattr(sent, "chat_id", None),
        "owner_message_id": sent.id,
    }


def extract_owner_support_test(text: str) -> tuple[bool, str]:
    stripped = text.strip()
    prefixes = ("/support_test", "/as_user")
    for prefix in prefixes:
        if stripped.startswith(prefix):
            remaining = stripped[len(prefix) :].strip()
            return True, remaining
    return False, text


def _message_peer(message: Message) -> str | int:
    username = getattr(message.chat, "username", None) if getattr(message, "chat", None) else None
    if username:
        return str(username)
    sender_id = getattr(message, "sender_id", None)
    if sender_id is not None:
        return int(sender_id)
    chat_id = getattr(message, "chat_id", None)
    if chat_id is not None:
        return int(chat_id)
    return "me"


async def _send_reply_for_message(
    tg_client: TelegramClient,
    message: Message,
    *,
    reply_text: str,
) -> dict[str, Any]:
    # For live Telethon events, prefer replying through the message/chat context.
    # This avoids brittle entity resolution for private dialogs that may not be cached yet.
    try:
        input_chat = None
        if hasattr(message, "get_input_chat"):
            input_chat = await message.get_input_chat()
        if input_chat is not None:
            raw_sent = await tg_client.send_message(
                input_chat,
                reply_text,
                reply_to=int(message.id),
            )
            return {
                "id": raw_sent.id,
                "chat_id": raw_sent.chat_id,
                "sender_id": getattr(raw_sent, "sender_id", None),
                "text": raw_sent.message or "",
                "date": raw_sent.date.isoformat() if raw_sent.date else None,
                "reply_to_msg_id": getattr(raw_sent, "reply_to_msg_id", None),
                "out": bool(raw_sent.out),
            }
    except Exception:
        pass

    if hasattr(message, "reply"):
        try:
            raw_sent = await message.reply(reply_text)
            return {
                "id": raw_sent.id,
                "chat_id": raw_sent.chat_id,
                "sender_id": getattr(raw_sent, "sender_id", None),
                "text": raw_sent.message or "",
                "date": raw_sent.date.isoformat() if raw_sent.date else None,
                "reply_to_msg_id": getattr(raw_sent, "reply_to_msg_id", None),
                "out": bool(raw_sent.out),
            }
        except Exception:
            pass

    return await telegram_reply(
        tg_client,
        {
            "peer": _message_peer(message),
            "reply_to_msg_id": int(message.id),
            "text": reply_text,
        },
    )


async def process_support_message(
    tg_client: TelegramClient,
    message: Message,
    *,
    send: bool,
    source: str,
) -> dict[str, Any]:
    settings = get_telegram_settings()
    message_text = message.message or ""
    if not message_text.strip():
        return {"ok": True, "status": "empty_message_ignored", "message_id": message.id}

    sender_id = getattr(message, "sender_id", None)
    chat_id = getattr(message, "chat_id", None)
    is_owner = settings.is_trusted_operator(sender_id)
    support_test_mode, effective_text = extract_owner_support_test(message_text)
    owner_language = normalize_language(None) or detect_language(effective_text or message_text)
    owner_support_like = bool(
        is_owner
        and not support_test_mode
        and _is_owner_support_like_request(effective_text, owner_language)
    )
    is_test_traffic = bool(support_test_mode or settings.is_test_user(sender_id))

    owner_review_result = await maybe_handle_owner_candidate_review(tg_client, message)
    if owner_review_result is not None:
        return owner_review_result

    if is_owner and not support_test_mode and not owner_support_like:
        operator_result = await maybe_handle_operator_request(tg_client, message)
        if operator_result is not None:
            return operator_result
        return {
            "ok": True,
            "status": "operator_mode",
            "sender_id": sender_id,
            "message_id": message.id,
            "message_text": message_text,
        }

    user_text = effective_text.strip()
    if not user_text:
        return {
            "ok": False,
            "status": "empty_support_test_payload" if support_test_mode else "empty_message_ignored",
            "message_id": message.id,
        }

    language = normalize_language(None) or detect_language(user_text)
    thread_chat_id = str(chat_id or _message_peer(message))
    thread_user_id = str(sender_id or thread_chat_id)
    peer = _message_peer(message)

    async with httpx.AsyncClient() as kb_client:
        support_check: dict[str, Any] | None = None
        support_check_error: str | None = None
        candidate_update: dict[str, Any] | None = None
        owner_candidate_notification: dict[str, Any] | None = None
        normalized_text = _normalized(user_text)
        if sender_id and (
            _is_subscription_activation_issue(user_text, language)
            or _is_subscription_status_check(normalized_text, language)
            or _is_premium_entitlement_issue(user_text, language)
        ):
            try:
                support_check = await fitmentor_support_subscription_check(
                    kb_client,
                    telegram_id=int(sender_id),
                )
            except Exception as exc:
                support_check = None
                support_check_error = str(exc)

        thread = await kb_post(
            kb_client,
            "/kb/support-threads",
            {
                "telegram_user_id": thread_user_id,
                "telegram_chat_id": thread_chat_id,
                "preferred_language": language,
                "priority_support": _is_priority_support(support_check),
                "is_test": is_test_traffic,
            },
        )
        thread_id = thread["thread_id"]
        thread_language = normalize_language(thread.get("preferred_language")) or language
        priority_support = bool(thread.get("priority_support") or _is_priority_support(support_check))
        is_test_thread = bool(thread.get("is_test") or is_test_traffic)
        case_status = str(thread.get("case_status") or "open")

        await kb_post(
            kb_client,
            "/kb/support-messages",
            {
                "thread_id": thread_id,
                "role": "user",
                "message_text": user_text,
                "retrieval_context": [],
                "preferred_language": thread_language,
            },
        )

        search = await kb_get(
            kb_client,
            "/kb/search",
            {"query": user_text, "limit": 5, "language": thread_language},
        )
        kb_items = list(search.get("items", []))
        reply_text, confident = build_reply(
            user_text=user_text,
            language=thread_language,
            kb_items=kb_items,
            support_check=support_check,
        )
        sent_message: dict[str, Any] | None = None
        if send:
            sent_message = await _send_reply_for_message(
                tg_client,
                message,
                reply_text=reply_text,
            )

        await kb_post(
            kb_client,
            "/kb/support-messages",
            {
                "thread_id": thread_id,
                "role": "assistant",
                "message_text": reply_text,
                "retrieval_context": kb_items,
                "preferred_language": thread_language,
            },
        )

        case_status = str(
            (
                await kb_post(
                    kb_client,
                    "/kb/support-threads/status",
                    {
                        "thread_id": thread_id,
                        "case_status": _determine_case_status(
                            confident=confident,
                            reply_text=reply_text,
                            support_check=support_check,
                        ),
                        "resolution_note": (
                            "Automatically resolved by support flow."
                            if confident and not _should_mark_manual_review(reply_text=reply_text, support_check=support_check)
                            else None
                        ),
                        "reviewed_by": "support_flow",
                    },
                )
            ).get("case_status")
            or case_status
        )

        if not confident and should_create_candidate_knowledge(
            user_text=user_text,
            reply_text=reply_text,
            language=thread_language,
            kb_items=kb_items,
            support_check=support_check,
        ):
            candidate_update = await maybe_create_proposed_update(
                kb_client,
                user_text=user_text,
                reply_text=reply_text,
                language=thread_language,
                source=source,
                support_check=support_check,
            )
            if candidate_update and bool(candidate_update.get("created", True)):
                try:
                    owner_candidate_notification = await notify_owner_about_candidate(
                        tg_client,
                        candidate=candidate_update,
                        user_text=user_text,
                        language=thread_language,
                        priority_support=priority_support,
                    )
                except Exception:
                    owner_candidate_notification = None

    return {
        "ok": True,
        "peer": peer,
        "thread_id": thread_id,
        "preferred_language": thread_language,
        "message_id": message.id,
        "mode": "support_test" if support_test_mode else "support",
        "is_test": is_test_thread,
        "confident": confident,
        "kb_hits": len(kb_items),
        "priority_support": priority_support,
        "case_status": case_status,
        "support_check": support_check,
        "support_check_error": support_check_error,
        "candidate_update": candidate_update,
        "owner_candidate_notification": owner_candidate_notification,
        "reply_text": reply_text,
        "sent": bool(sent_message),
        "sent_message": sent_message,
    }
