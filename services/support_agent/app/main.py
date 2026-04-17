from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties

from packages.common.settings.config import Settings, get_settings
from services.support_agent.app.handlers.messages import router


def build_dispatcher() -> Dispatcher:
    dp = Dispatcher()
    dp.include_router(router)
    return dp


async def run() -> None:
    settings = get_settings()
    bot = Bot(
        token=settings.telegram_support_bot_token,
        default=DefaultBotProperties(parse_mode="HTML"),
    )
    dp = build_dispatcher()
    await dp.start_polling(bot)


if __name__ == "__main__":
    import asyncio

    asyncio.run(run())
