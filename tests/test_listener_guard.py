from __future__ import annotations

import importlib
import sys
import types
import unittest


def _install_listener_stubs() -> None:
    telethon = types.ModuleType("telethon")
    telethon.events = types.SimpleNamespace(NewMessage=object)
    sys.modules["telethon"] = telethon

    client_module = types.ModuleType("services.telegram_adapter.app.client")
    client_module.create_client = lambda: None
    sys.modules["services.telegram_adapter.app.client"] = client_module

    support_flow_module = types.ModuleType("services.telegram_adapter.app.support_flow")
    support_flow_module.process_support_message = lambda *args, **kwargs: None
    sys.modules["services.telegram_adapter.app.support_flow"] = support_flow_module


class ListenerGuardTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        _install_listener_stubs()
        sys.modules.pop("scripts.support_listener", None)
        cls.listener_module = importlib.import_module("scripts.support_listener")

    def test_ignores_outgoing_messages(self) -> None:
        result = self.listener_module.should_ignore_message(
            message_sender_id=111,
            message_out=True,
            self_user_id=7448513035,
        )
        self.assertTrue(result)

    def test_ignores_messages_from_self_account(self) -> None:
        result = self.listener_module.should_ignore_message(
            message_sender_id=7448513035,
            message_out=False,
            self_user_id=7448513035,
        )
        self.assertTrue(result)

    def test_keeps_real_inbound_messages(self) -> None:
        result = self.listener_module.should_ignore_message(
            message_sender_id=111,
            message_out=False,
            self_user_id=7448513035,
        )
        self.assertFalse(result)
