import random

from aiogram import F, Router
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

from bot.models.base import async_session
from bot.services.calculations import (
    calculate_activity_coefficient,
    calculate_bmr,
    calculate_macros,
    calculate_target_calories,
    calculate_tdee,
    calculate_water_ml,
)
from bot.services.profiles import save_profile
from bot.services.users import get_or_create_user, mark_active
from bot.services.weights import add_weight_entry
from bot.texts import LANGUAGE_LABELS, LANGUAGE_PROMPT, texts_for
from bot.voices import DEFAULT_VOICE, get_voice

router = Router()


class Onboarding(StatesGroup):
    language = State()
    gender = State()
    age = State()
    height = State()
    weight = State()
    job_type = State()
    strength_freq = State()
    cardio_freq = State()
    steps = State()
    goal = State()
    target_weight = State()
    pace = State()


def language_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text=label, callback_data=f"lang:{lang}")] for lang, label in LANGUAGE_LABELS.items()]
    )


def build_gender_kb(voice: dict) -> InlineKeyboardMarkup:
    labels = voice["gender_labels"]
    return InlineKeyboardMarkup(
        inline_keyboard=[[
            InlineKeyboardButton(text=labels["m"], callback_data="gender:m"),
            InlineKeyboardButton(text=labels["f"], callback_data="gender:f"),
        ]]
    )


def row_kb(prefix: str, labels: dict) -> InlineKeyboardMarkup:
    """All buttons in one row."""
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text=label, callback_data=f"{prefix}:{key}") for key, label in labels.items()]]
    )


def column_kb(prefix: str, labels: dict) -> InlineKeyboardMarkup:
    """One button per row."""
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text=label, callback_data=f"{prefix}:{key}")] for key, label in labels.items()]
    )


def share_meal_kb(t: dict) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text=t["share_meal_btn"], callback_data="share_meal")]]
    )


async def _voice_and_texts(state: FSMContext) -> tuple[dict, dict]:
    data = await state.get_data()
    voice = get_voice(data.get("voice", DEFAULT_VOICE))
    return voice, texts_for(voice)


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext) -> None:
    async with async_session() as session:
        user = await get_or_create_user(session, message.from_user.id, message.from_user.language_code or "ru")

    if user.status != "onboarding":
        voice = get_voice(user.voice)
        await message.answer(voice["welcome_back"].format(quote=f"<b>{random.choice(voice['quotes'])}</b>"))
        return

    # Language (and, for Russian, the theme) comes first — the picker
    # lives in settings.py and calls begin_onboarding() once it's chosen.
    await state.set_state(Onboarding.language)
    await message.answer(LANGUAGE_PROMPT, reply_markup=language_kb())


async def begin_onboarding(message: Message, state: FSMContext, voice_name: str) -> None:
    voice = get_voice(voice_name)
    await state.set_state(Onboarding.gender)
    await state.update_data(voice=voice_name)
    await message.answer(
        voice["start_intro"].format(quote=f"<b>{random.choice(voice['quotes'])}</b>"),
        reply_markup=build_gender_kb(voice),
    )


@router.callback_query(StateFilter(Onboarding.gender), F.data.startswith("gender:"))
async def on_gender(callback: CallbackQuery, state: FSMContext) -> None:
    voice, t = await _voice_and_texts(state)

    gender = callback.data.split(":")[1]
    await state.update_data(gender=gender)
    await state.set_state(Onboarding.age)
    await callback.message.edit_text(f"{voice['gender_labels'][gender]}. {voice['confirm']}")
    await callback.message.answer(t["age_q"])
    await callback.answer()


@router.message(StateFilter(Onboarding.age))
async def on_age(message: Message, state: FSMContext) -> None:
    voice, t = await _voice_and_texts(state)

    if not message.text or not message.text.isdigit() or not (10 <= int(message.text) <= 100):
        await message.answer(voice["age_error"])
        return
    await state.update_data(age=int(message.text))
    await state.set_state(Onboarding.height)
    await message.answer(t["height_q"])


@router.message(StateFilter(Onboarding.height))
async def on_height(message: Message, state: FSMContext) -> None:
    voice, t = await _voice_and_texts(state)

    try:
        height = float(message.text.replace(",", "."))
        assert 100 <= height <= 250
    except (ValueError, AssertionError, AttributeError):
        await message.answer(voice["height_error"])
        return
    await state.update_data(height_cm=height)
    await state.set_state(Onboarding.weight)
    await message.answer(t["weight_q"])


@router.message(StateFilter(Onboarding.weight))
async def on_weight(message: Message, state: FSMContext) -> None:
    voice, t = await _voice_and_texts(state)

    try:
        weight = float(message.text.replace(",", "."))
        assert 30 <= weight <= 300
    except (ValueError, AssertionError, AttributeError):
        await message.answer(voice["weight_error"])
        return
    await state.update_data(weight_kg=weight)
    await state.set_state(Onboarding.job_type)
    await message.answer(voice["activity_intro"], reply_markup=row_kb("job", t["job_buttons"]))


@router.callback_query(StateFilter(Onboarding.job_type), F.data.startswith("job:"))
async def on_job_type(callback: CallbackQuery, state: FSMContext) -> None:
    voice, t = await _voice_and_texts(state)

    job_type = callback.data.split(":")[1]
    await state.update_data(job_type=job_type)
    await state.set_state(Onboarding.strength_freq)
    await callback.message.edit_text(voice["confirm"])
    await callback.message.answer(t["strength_q"], reply_markup=column_kb("strength", t["frequency_labels"]))
    await callback.answer()


@router.callback_query(StateFilter(Onboarding.strength_freq), F.data.startswith("strength:"))
async def on_strength_freq(callback: CallbackQuery, state: FSMContext) -> None:
    voice, t = await _voice_and_texts(state)

    strength_freq = callback.data.split(":")[1]
    await state.update_data(strength_freq=strength_freq)
    await state.set_state(Onboarding.cardio_freq)
    await callback.message.edit_text(voice["confirm"])
    await callback.message.answer(t["cardio_q"], reply_markup=column_kb("cardio", t["frequency_labels"]))
    await callback.answer()


@router.callback_query(StateFilter(Onboarding.cardio_freq), F.data.startswith("cardio:"))
async def on_cardio_freq(callback: CallbackQuery, state: FSMContext) -> None:
    voice, t = await _voice_and_texts(state)

    cardio_freq = callback.data.split(":")[1]
    await state.update_data(cardio_freq=cardio_freq)
    await state.set_state(Onboarding.steps)
    await callback.message.edit_text(voice["confirm"])
    await callback.message.answer(t["steps_q"], reply_markup=column_kb("steps", t["steps_labels"]))
    await callback.answer()


@router.callback_query(StateFilter(Onboarding.steps), F.data.startswith("steps:"))
async def on_steps(callback: CallbackQuery, state: FSMContext) -> None:
    voice, t = await _voice_and_texts(state)

    steps_bucket = callback.data.split(":")[1]
    await state.update_data(steps_bucket=steps_bucket)
    await state.set_state(Onboarding.goal)
    await callback.message.edit_text(voice["confirm"])
    await callback.message.answer(t["goal_q"], reply_markup=row_kb("goal", t["goal_buttons"]))
    await callback.answer()


@router.callback_query(StateFilter(Onboarding.goal), F.data.startswith("goal:"))
async def on_goal(callback: CallbackQuery, state: FSMContext) -> None:
    voice, t = await _voice_and_texts(state)

    goal = callback.data.split(":")[1]
    await state.update_data(goal=goal)
    await callback.message.edit_text(voice["confirm"])
    await callback.message.answer(voice["goal_lines"][goal])

    if goal == "maintain":
        await finish_onboarding(callback.message, state)
    else:
        await state.set_state(Onboarding.target_weight)
        await callback.message.answer(t["target_weight_q"])
    await callback.answer()


@router.message(StateFilter(Onboarding.target_weight))
async def on_target_weight(message: Message, state: FSMContext) -> None:
    voice, t = await _voice_and_texts(state)

    try:
        target = float(message.text.replace(",", "."))
        assert 30 <= target <= 300
    except (ValueError, AssertionError, AttributeError):
        await message.answer(voice["target_weight_error"])
        return
    await state.update_data(target_weight_kg=target)
    await state.set_state(Onboarding.pace)
    await message.answer(t["pace_q"], reply_markup=row_kb("pace", t["pace_buttons"]))


@router.callback_query(StateFilter(Onboarding.pace), F.data.startswith("pace:"))
async def on_pace(callback: CallbackQuery, state: FSMContext) -> None:
    voice, _ = await _voice_and_texts(state)

    pace = callback.data.split(":")[1]
    await state.update_data(pace=pace)
    await callback.message.edit_text(voice["confirm"])
    await finish_onboarding(callback.message, state)
    await callback.answer()


async def finish_onboarding(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    voice, t = await _voice_and_texts(state)

    bmr = calculate_bmr(data["gender"], data["weight_kg"], data["height_cm"], data["age"])
    activity_coefficient = calculate_activity_coefficient(
        data["job_type"], data["strength_freq"], data["cardio_freq"], data["steps_bucket"]
    )
    tdee = calculate_tdee(bmr, activity_coefficient)
    target_calories = calculate_target_calories(tdee, data["gender"], data["goal"], data.get("pace"))
    macros = calculate_macros(data["gender"], data["goal"], data["weight_kg"], target_calories)
    water_ml = calculate_water_ml(data["weight_kg"])

    async with async_session() as session:
        user = await get_or_create_user(session, message.chat.id)
        await save_profile(
            session,
            user_id=user.id,
            gender=data["gender"],
            age=data["age"],
            height_cm=data["height_cm"],
            weight_kg=data["weight_kg"],
            job_type=data["job_type"],
            strength_freq=data["strength_freq"],
            cardio_freq=data["cardio_freq"],
            steps_bucket=data["steps_bucket"],
            activity_coefficient=activity_coefficient,
            goal=data["goal"],
            pace=data.get("pace"),
            target_weight_kg=data.get("target_weight_kg") if data["goal"] != "maintain" else None,
            target_calories=target_calories,
            **macros,
            water_ml=water_ml,
        )
        await add_weight_entry(session, user.id, data["weight_kg"])  # starting point for /weight progress
        await mark_active(session, user.id)

    await state.clear()
    await message.answer(
        f"{voice['final_summary_lead']}\n\n"
        f"{t['macros_block'].format(calories=target_calories, **macros)}\n"
        f"{t['water_line'].format(water_ml=water_ml)}\n\n"
        f"<b>{random.choice(voice['quotes'])}</b>\n\n"
        f"{voice['final_summary_tail']}",
        reply_markup=share_meal_kb(t),
    )

    # Imported here, not at the top: reminders.py imports keyboards from this module.
    from bot.handlers.reminders import start_reminder_setup
    await start_reminder_setup(message, state, data.get("voice", DEFAULT_VOICE))
