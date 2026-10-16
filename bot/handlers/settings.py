from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

from bot.models.base import async_session
from bot.services.users import get_or_create_user, set_voice
from bot.voices import VOICES, get_voice

router = Router()

VOICE_KB = InlineKeyboardMarkup(
    inline_keyboard=[[InlineKeyboardButton(text=v["label"], callback_data=f"voice:{key}")] for key, v in VOICES.items()]
)


@router.message(Command("settings"))
async def cmd_settings(message: Message) -> None:
    await message.answer("Выбери стиль общения бота:", reply_markup=VOICE_KB)


@router.callback_query(F.data.startswith("voice:"))
async def on_voice_chosen(callback: CallbackQuery) -> None:
    voice_name = callback.data.split(":")[1]

    async with async_session() as session:
        user = await get_or_create_user(session, callback.from_user.id)
        await set_voice(session, user.id, voice_name)

    voice = get_voice(voice_name)
    await callback.message.edit_text(f"Стиль изменён: {voice['label']}\n\n{voice['confirm']}")
    await callback.answer()
