import asyncio
import html
import logging

from aiogram import F, Router
from aiogram.enums import ChatAction
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message

from bot.models.base import async_session
from bot.services.assistant import MAX_HISTORY_MESSAGES, ask_assistant, build_user_context
from bot.services.meals import get_today_entries, get_week_totals
from bot.services.profiles import get_profile
from bot.services.users import get_or_create_user
from bot.services.weights import get_weight_entries
from bot.texts import texts_for
from bot.voices import DEFAULT_VOICE, get_voice

router = Router()
log = logging.getLogger(__name__)


class Assist(StatesGroup):
    chatting = State()


@router.message(Command("assist"))
async def cmd_assist(message: Message, state: FSMContext) -> None:
    async with async_session() as session:
        user = await get_or_create_user(session, message.from_user.id)
    await state.set_state(Assist.chatting)
    await state.update_data(voice=user.voice, history=[])
    await message.answer(texts_for(get_voice(user.voice))["assist_intro"])


@router.message(StateFilter(Assist.chatting), Command("stop"))
async def cmd_stop(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    await state.clear()
    await message.answer(texts_for(get_voice(data.get("voice", DEFAULT_VOICE)))["assist_bye"])


@router.message(StateFilter(Assist.chatting), ~F.text.startswith("/"))
async def on_question(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    voice = get_voice(data.get("voice", DEFAULT_VOICE))
    t = texts_for(voice)

    if not message.text:
        await message.answer(t["assist_text_only"])
        return

    await message.bot.send_chat_action(message.chat.id, ChatAction.TYPING)

    # Fresh data on every question, so "what about now?" after logging a meal works.
    async with async_session() as session:
        user = await get_or_create_user(session, message.from_user.id)
        context = build_user_context(
            await get_profile(session, user.id),
            await get_today_entries(session, user.id),
            await get_week_totals(session, user.id),
            await get_weight_entries(session, user.id),
        )

    history = data.get("history", [])
    try:
        answer = await asyncio.to_thread(
            ask_assistant, history, message.text, context, t["gemini_language"], voice["assistant_style"],
        )
    except Exception:
        log.exception("assistant failed")
        await message.answer(t["assist_error"])
        return

    history = (history + [{"role": "user", "text": message.text}, {"role": "model", "text": answer}])[-MAX_HISTORY_MESSAGES:]
    await state.update_data(history=history)
    # Bot uses HTML parse mode — escape so a "<" or "&" from the model can't break the message.
    await message.answer(html.escape(answer) or t["assist_error"])
