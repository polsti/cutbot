import random

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from bot.style import WOLF_QUOTES

router = Router()


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    await message.answer(
        "Команды:\n"
        "/start — профиль\n"
        "/add — записать приём пищи по фото\n"
        "/today — сводка за сегодня\n"
        "/stats — за последние 7 дней\n"
        "/help — справка\n\n"
        "Остальное (/fridge и т.д.) — дальше по плану.\n\n"
        f"<b>{random.choice(WOLF_QUOTES)}</b>"
    )
