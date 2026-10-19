"""Catch-all for anything no other router handled. Must be included last
in main.py. Without it the bot silently ignores the update — a button
just spins forever, which looks like the bot is down.

Most common cause: the bot restarted (every deploy) and lost the in-memory
FSM state, so buttons from before the restart no longer match any handler.
"""

from aiogram import Router
from aiogram.types import CallbackQuery, Message

from bot.models.base import async_session
from bot.services.users import get_or_create_user
from bot.texts import texts_for
from bot.voices import get_voice

router = Router()


async def _texts(telegram_id: int) -> dict:
    async with async_session() as session:
        user = await get_or_create_user(session, telegram_id)
    return texts_for(get_voice(user.voice))


@router.callback_query()
async def on_expired_button(callback: CallbackQuery) -> None:
    t = await _texts(callback.from_user.id)
    await callback.answer(t["button_expired"], show_alert=True)


@router.message()
async def on_unknown_message(message: Message) -> None:
    t = await _texts(message.from_user.id)
    await message.answer(t["fallback"])
