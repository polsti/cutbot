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
        "/help — справка\n\n"
        "Остальное (/add, /today, /fridge) — дальше по плану.\n\n"
        f"<b>{random.choice(WOLF_QUOTES)}</b>"
    )
