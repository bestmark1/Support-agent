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
        self.assertIn("Коротко напишите, что произошло", reply_text)
        self.assertNotIn("дату платежа", reply_text)
        self.assertFalse(confident)

    def test_payment_context_keeps_payment_oriented_reply(self) -> None:
        reply_text, confident = self.support_flow.build_reply("Оплата не прошла.", "ru", [])
        self.assertIn("дату попытки оплаты", reply_text)
        self.assertFalse(confident)
