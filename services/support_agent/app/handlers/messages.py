from aiogram import Router
from aiogram.types import Message

from services.support_agent.app.services.support import build_support_reply

router = Router()


@router.message()
async def handle_message(message: Message) -> None:
    reply = await build_support_reply(
        user_text=message.text or "",
        telegram_user_id=str(message.from_user.id) if message.from_user else str(message.chat.id),
        telegram_chat_id=str(message.chat.id),
    )
    await message.answer(reply)
