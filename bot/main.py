import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from bot.config import settings
from bot.handlers.fallback import router as fallback_router
from bot.handlers.meals import router as meals_router
from bot.handlers.onboarding import router as onboarding_router
from bot.handlers.settings import router as settings_router
from bot.handlers.start import router as start_router
from bot.handlers.weight import router as weight_router
from bot.health import start_health_server


async def main() -> None:
    logging.basicConfig(level=logging.INFO)

    bot = Bot(token=settings.bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()
    dp.include_router(onboarding_router)
    dp.include_router(meals_router)
    dp.include_router(settings_router)
    dp.include_router(weight_router)
    dp.include_router(start_router)
    dp.include_router(fallback_router)  # must stay last

    health_runner = await start_health_server(settings.port)
    try:
        await dp.start_polling(bot)
    finally:
        await health_runner.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
