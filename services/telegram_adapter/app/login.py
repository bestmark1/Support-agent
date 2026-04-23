from __future__ import annotations

import asyncio
import getpass

from telethon.errors import SessionPasswordNeededError

from services.telegram_adapter.app.client import create_client
from services.telegram_adapter.app.config import get_telegram_settings


async def main() -> None:
    settings = get_telegram_settings()
    phone = settings.telegram_phone or input("Telegram phone (international format): ").strip()

    client = create_client()
    await client.connect()
    if await client.is_user_authorized():
        print(f"Session already authorized at {settings.session_path}")
        await client.disconnect()
        return

    sent = await client.send_code_request(phone)
    code = input("Telegram login code: ").strip()
    try:
        await client.sign_in(phone=phone, code=code, phone_code_hash=sent.phone_code_hash)
    except SessionPasswordNeededError:
        password = getpass.getpass("Telegram 2FA password: ")
        await client.sign_in(password=password)

    me = await client.get_me()
    print(f"Authorized Telegram session for user id={me.id} username={me.username!r}")
    print(f"Session stored at {settings.session_path}")
    await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
