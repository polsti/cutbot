import random

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from bot.models.base import async_session
from bot.services.users import get_or_create_user
from bot.voices import get_voice

router = Router()


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    async with async_session() as session:
        user = await get_or_create_user(session, message.from_user.id)
    voice = get_voice(user.voice)

    await message.answer(
        "Команды:\n"
        "/start — профиль\n"
        "/add — записать приём пищи по фото\n"
        "/today — сводка за сегодня\n"
        "/stats — за последние 7 дней\n"
        "/settings — стиль общения\n"
        "/help — справка\n\n"
        "Остальное (/fridge и т.д.) — дальше по плану.\n\n"
        f"<b>{random.choice(voice['help_quote_pool'])}</b>"
    )
