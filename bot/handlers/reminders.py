from datetime import datetime, timezone

from aiogram import F, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

from bot.handlers.onboarding import column_kb, row_kb
from bot.models.base import async_session
from bot.services.reminders import REMINDER_HOUR, local_now, utc_offset_from_local_time
from bot.services.users import get_or_create_user, update_user
from bot.texts import texts_for
from bot.voices import DEFAULT_VOICE, get_voice

router = Router()


class ReminderSetup(StatesGroup):
    ask = State()
    frequency = State()
    weekday = State()
    local_time = State()


async def _voice_and_texts(state: FSMContext) -> tuple[dict, dict]:
    data = await state.get_data()
    voice = get_voice(data.get("voice", DEFAULT_VOICE))
    return voice, texts_for(voice)


async def start_reminder_setup(message: Message, state: FSMContext, voice_name: str) -> None:
    """Entry point — called from /reminders and at the end of onboarding."""
    t = texts_for(get_voice(voice_name))
    await state.set_state(ReminderSetup.ask)
    await state.update_data(voice=voice_name)
    await message.answer(t["rem_q"], reply_markup=row_kb("rem", t["rem_yes_no"]))


@router.message(Command("reminders"))
async def cmd_reminders(message: Message, state: FSMContext) -> None:
    async with async_session() as session:
        user = await get_or_create_user(session, message.from_user.id)
    await start_reminder_setup(message, state, user.voice)


@router.callback_query(StateFilter(ReminderSetup.ask), F.data == "rem:no")
async def on_no_reminders(callback: CallbackQuery, state: FSMContext) -> None:
    _, t = await _voice_and_texts(state)
    async with async_session() as session:
        user = await get_or_create_user(session, callback.from_user.id)
        await update_user(session, user.id, weigh_reminder="none")
    await state.clear()
    await callback.message.edit_text(t["rem_off"])
    await callback.answer()


@router.callback_query(StateFilter(ReminderSetup.ask), F.data == "rem:yes")
async def on_yes_reminders(callback: CallbackQuery, state: FSMContext) -> None:
    voice, t = await _voice_and_texts(state)
    await state.set_state(ReminderSetup.frequency)
    await callback.message.edit_text(voice["confirm"])
    await callback.message.answer(t["rem_freq_q"], reply_markup=column_kb("remfreq", t["rem_freq_buttons"]))
    await callback.answer()


@router.callback_query(StateFilter(ReminderSetup.frequency), F.data.startswith("remfreq:"))
async def on_frequency(callback: CallbackQuery, state: FSMContext) -> None:
    voice, t = await _voice_and_texts(state)
    frequency = callback.data.split(":")[1]
    await state.update_data(frequency=frequency)
    await callback.message.edit_text(voice["confirm"])

    if frequency == "weekly":
        await state.set_state(ReminderSetup.weekday)
        days = dict(enumerate(t["weekday_names"]))
        await callback.message.answer(t["rem_weekday_q"], reply_markup=column_kb("remday", days))
    else:
        await ask_time_or_finish(callback.message, callback.from_user.id, state)
    await callback.answer()


@router.callback_query(StateFilter(ReminderSetup.weekday), F.data.startswith("remday:"))
async def on_weekday(callback: CallbackQuery, state: FSMContext) -> None:
    voice, _ = await _voice_and_texts(state)
    await state.update_data(weekday=int(callback.data.split(":")[1]))
    await callback.message.edit_text(voice["confirm"])
    await ask_time_or_finish(callback.message, callback.from_user.id, state)
    await callback.answer()


async def ask_time_or_finish(message: Message, telegram_id: int, state: FSMContext) -> None:
    async with async_session() as session:
        user = await get_or_create_user(session, telegram_id)
    if user.utc_offset_min is not None:  # timezone already known from an earlier setup
        await finish_setup(message, telegram_id, state, user.utc_offset_min)
        return
    _, t = await _voice_and_texts(state)
    await state.set_state(ReminderSetup.local_time)
    await message.answer(t["rem_time_q"])


@router.message(StateFilter(ReminderSetup.local_time), ~F.text.startswith("/"))
async def on_local_time(message: Message, state: FSMContext) -> None:
    _, t = await _voice_and_texts(state)
    offset = utc_offset_from_local_time(message.text or "", datetime.now(timezone.utc))
    if offset is None:
        await message.answer(t["rem_time_error"])
        return
    await finish_setup(message, message.from_user.id, state, offset)


async def finish_setup(message: Message, telegram_id: int, state: FSMContext, offset: int) -> None:
    data = await state.get_data()
    voice, t = await _voice_and_texts(state)
    frequency = data["frequency"]
    weekday = data.get("weekday") if frequency == "weekly" else None

    now = local_now(datetime.now(timezone.utc), offset)
    async with async_session() as session:
        user = await get_or_create_user(session, telegram_id)
        await update_user(
            session, user.id,
            weigh_reminder=frequency,
            weigh_weekday=weekday,
            weigh_since=now.date(),
            utc_offset_min=offset,
            # Set up after 08:00 → don't fire straight away, start from the next due morning.
            last_weigh_reminder=now.date() if now.hour >= REMINDER_HOUR else None,
        )
    await state.clear()

    when = t["rem_when"][frequency].format(day=t["weekday_names"][weekday] if weekday is not None else "")
    await message.answer(f"{t['rem_on'].format(when=when)}\n\n{voice['confirm']}")
