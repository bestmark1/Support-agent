from __future__ import annotations

import importlib
import sys
import types
import unittest


def _install_telethon_stubs() -> None:
    telethon = types.ModuleType("telethon")
    telethon.TelegramClient = type("TelegramClient", (), {})
    telethon.functions = types.SimpleNamespace(
        contacts=types.SimpleNamespace(
            SearchRequest=type("SearchRequest", (), {}),
        )
    )
    sys.modules["telethon"] = telethon

    tl_module = types.ModuleType("telethon.tl")
    custom_module = types.ModuleType("telethon.tl.custom")
    message_module = types.ModuleType("telethon.tl.custom.message")
    message_module.Message = type("Message", (), {})

    sys.modules["telethon.tl"] = tl_module
    sys.modules["telethon.tl.custom"] = custom_module
    sys.modules["telethon.tl.custom.message"] = message_module


class SupportFlowSmokeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        _install_telethon_stubs()
        sys.modules.pop("services.partnership_research.app.services.telegram_outreach", None)
        sys.modules.pop("services.telegram_adapter.app.commands", None)
        sys.modules.pop("services.telegram_adapter.app.support_flow", None)
        cls.support_flow = importlib.import_module("services.telegram_adapter.app.support_flow")

    def test_russian_greeting_with_punctuation(self) -> None:
        reply_text, confident = self.support_flow.build_reply("Привет.", "ru", [])
        self.assertEqual(reply_text, "Здравствуйте. Чем могу помочь вам по FitMentor?")
        self.assertTrue(confident)

    def test_russian_thanks_with_punctuation(self) -> None:
        reply_text, confident = self.support_flow.build_reply("Спасибо!", "ru", [])
        self.assertEqual(reply_text, "Пожалуйста.")
        self.assertTrue(confident)

    def test_english_goodbye_with_punctuation(self) -> None:
        reply_text, confident = self.support_flow.build_reply("Bye.", "en", [])
        self.assertEqual(reply_text, "Goodbye.")
        self.assertTrue(confident)

    def test_generic_unknown_case_uses_neutral_fallback(self) -> None:
        reply_text, confident = self.support_flow.build_reply("У меня другой вопрос.", "ru", [])
        self.assertIn("Какой у вас вопрос?", reply_text)
        self.assertNotIn("дату платежа", reply_text)
        self.assertFalse(confident)

    def test_payment_context_keeps_payment_oriented_reply(self) -> None:
        reply_text, confident = self.support_flow.build_reply("Оплата не прошла.", "ru", [])
        self.assertIn("дату попытки оплаты", reply_text)
        self.assertIn("что делать дальше", reply_text)
        self.assertFalse(confident)

    def test_payment_phrase_oplata_ne_prohodit_hits_payment_branch(self) -> None:
        reply_text, confident = self.support_flow.build_reply("Оплата не проходит. Что делать?", "ru", [])
        self.assertIn("дату попытки оплаты", reply_text)
        self.assertIn("что делать дальше", reply_text)
        self.assertFalse(confident)

    def test_premium_entitlement_reply_uses_human_wording(self) -> None:
        reply_text, confident = self.support_flow.build_reply(
            "После оплаты Premium у меня остался старый лимит AI-сообщений. Что делать?",
            "ru",
            [],
            {"diagnosis": "subscription_active"},
        )
        self.assertIn("Premium уже активен", reply_text)
        self.assertIn("какой именно лимит или функция не обновились", reply_text)
        self.assertNotIn("Premium-прав", reply_text)
        self.assertFalse(confident)

    def test_subscription_activation_missing_access_reply_is_clearer(self) -> None:
        reply_text, confident = self.support_flow.build_reply(
            "Оплатил, но подписка не активировалась",
            "ru",
            [],
            {"diagnosis": "payment_confirmed_but_access_missing"},
        )
        self.assertIn("платёж подтверждён", reply_text)
        self.assertIn("доступ ещё не обновился", reply_text)
        self.assertIn("проверим это вручную", reply_text)
        self.assertFalse(confident)

    def test_known_premium_case_does_not_create_candidate(self) -> None:
        should_create = self.support_flow.should_create_candidate_knowledge(
            user_text="После оплаты Premium у меня остался старый лимит AI-сообщений. Что делать?",
            reply_text="Я проверил статус: для этого Telegram-аккаунта Premium уже активен, но лимиты или Premium-функции могли ещё не обновиться. Мы проверим это вручную со своей стороны.",
            language="ru",
            kb_items=[],
            support_check={"diagnosis": "subscription_active"},
        )
        self.assertFalse(should_create)

    def test_premium_issue_is_not_operator_summary_intent(self) -> None:
        is_operator = self.support_flow._is_operator_premium_request(
            "После оплаты Premium у меня остался старый лимит AI-сообщений. Что делать?"
        )
        self.assertFalse(is_operator)

    def test_owner_support_like_request_detects_subscription_issue(self) -> None:
        is_support_like = self.support_flow._is_owner_support_like_request(
            "У меня Premium, но лимит AI-сообщений не обновился после оплаты",
            "ru",
        )
        self.assertTrue(is_support_like)
