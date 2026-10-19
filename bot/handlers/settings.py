from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

from bot.handlers.onboarding import Onboarding, begin_onboarding, language_kb
from bot.models.base import async_session
from bot.services.users import get_or_create_user, set_language, set_voice
from bot.texts import LANGUAGE_PROMPT, TEXTS, texts_for
from bot.voices import VOICES, get_voice, voices_for

router = Router()


def theme_kb(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text=VOICES[key]["label"], callback_data=f"voice:{key}")] for key in voices_for(lang)]
    )


@router.message(Command("settings"))
async def cmd_settings(message: Message) -> None:
    await message.answer(LANGUAGE_PROMPT, reply_markup=language_kb())


@router.callback_query(F.data.startswith("lang:"))
async def on_language_chosen(callback: CallbackQuery, state: FSMContext) -> None:
    lang = callback.data.split(":")[1]

    async with async_session() as session:
        user = await get_or_create_user(session, callback.from_user.id)
        await set_language(session, user.id, lang)

    voice_keys = voices_for(lang)
    if len(voice_keys) == 1:
        await apply_voice(callback, state, voice_keys[0])
    else:
        await callback.message.edit_text(TEXTS[lang]["choose_theme"], reply_markup=theme_kb(lang))
    await callback.answer()


@router.callback_query(F.data.startswith("voice:"))
async def on_voice_chosen(callback: CallbackQuery, state: FSMContext) -> None:
    await apply_voice(callback, state, callback.data.split(":")[1])
    await callback.answer()


async def apply_voice(callback: CallbackQuery, state: FSMContext, voice_name: str) -> None:
    async with async_session() as session:
        user = await get_or_create_user(session, callback.from_user.id)
        await set_voice(session, user.id, voice_name)

    voice = get_voice(voice_name)
    t = texts_for(voice)
    await callback.message.edit_text(f"{t['theme_changed'].format(label=voice['label'])}\n\n{voice['confirm']}")

    # Picked during /start → go straight on to the onboarding questions.
    if await state.get_state() == Onboarding.language.state:
        await begin_onboarding(callback.message, state, voice_name)
