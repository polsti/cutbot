from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message

from bot.models.base import async_session
from bot.services.users import get_or_create_user

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    async with async_session() as session:
        user = await get_or_create_user(session, message.from_user.id, message.from_user.language_code or "ru")

    if user.status == "onboarding":
        await message.answer(
            "Привет! Я помогу считать калории, БЖУ и активность.\n\n"
            "Онбординг (расчёт твоей нормы) будет в следующем шаге — пока что я просто запомнил тебя в базе 🙂"
        )
    else:
        await message.answer("С возвращением! Используй /today, чтобы увидеть сводку за сегодня.")


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    await message.answer(
        "Доступные команды:\n"
        "/start — начать / профиль\n"
        "/help — эта справка\n\n"
        "Остальные команды (/add, /today, /fridge и т.д.) появятся на следующих этапах."
    )
