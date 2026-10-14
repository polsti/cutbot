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
from bot.style import CONFIRM, GENDER_LABELS, GOAL_LINES, WOLF_QUOTES

router = Router()


class Onboarding(StatesGroup):
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


GENDER_KB = InlineKeyboardMarkup(
    inline_keyboard=[[
        InlineKeyboardButton(text=GENDER_LABELS["m"], callback_data="gender:m"),
        InlineKeyboardButton(text=GENDER_LABELS["f"], callback_data="gender:f"),
    ]]
)

JOB_TYPE_KB = InlineKeyboardMarkup(
    inline_keyboard=[[
        InlineKeyboardButton(text="Сидячая работа/учёба", callback_data="job:office"),
        InlineKeyboardButton(text="Физическая работа / на ногах", callback_data="job:physical"),
    ]]
)

FREQUENCY_LABELS = [
    ("0", "Не занимаюсь"),
    ("1-2", "1–2 раза в неделю"),
    ("3-4", "3–4 раза в неделю"),
    ("5+", "5+ раз в неделю"),
]


def _frequency_kb(prefix: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text=label, callback_data=f"{prefix}:{key}")] for key, label in FREQUENCY_LABELS]
    )


STRENGTH_KB = _frequency_kb("strength")
CARDIO_KB = _frequency_kb("cardio")

STEPS_LABELS = [
    ("<5000", "Меньше 5 000"),
    ("5000-10000", "5 000 – 10 000"),
    ("10000-15000", "10 000 – 15 000"),
    ("15000+", "Больше 15 000"),
]
STEPS_KB = InlineKeyboardMarkup(
    inline_keyboard=[[InlineKeyboardButton(text=label, callback_data=f"steps:{key}")] for key, label in STEPS_LABELS]
)

GOAL_KB = InlineKeyboardMarkup(
    inline_keyboard=[[
        InlineKeyboardButton(text="Поддержание веса", callback_data="goal:maintain"),
        InlineKeyboardButton(text="Похудение", callback_data="goal:lose"),
        InlineKeyboardButton(text="Набор массы", callback_data="goal:gain"),
    ]]
)

PACE_KB = InlineKeyboardMarkup(
    inline_keyboard=[[
        InlineKeyboardButton(text="Медленный", callback_data="pace:slow"),
        InlineKeyboardButton(text="Средний", callback_data="pace:medium"),
        InlineKeyboardButton(text="Быстрый", callback_data="pace:fast"),
    ]]
)


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext) -> None:
    async with async_session() as session:
        user = await get_or_create_user(session, message.from_user.id, message.from_user.language_code or "ru")

    if user.status != "onboarding":
        await message.answer(f"Профиль есть. <b>{random.choice(WOLF_QUOTES)}</b> Думай.")
        return

    await state.set_state(Onboarding.gender)
    await message.answer(
        f"Погнали считать. {CONFIRM}\n\n"
        f"<b>{random.choice(WOLF_QUOTES)}</b>\n\n"
        "Ты вообще кто?",
        reply_markup=GENDER_KB,
    )


@router.callback_query(StateFilter(Onboarding.gender), F.data.startswith("gender:"))
async def on_gender(callback: CallbackQuery, state: FSMContext) -> None:
    gender = callback.data.split(":")[1]
    await state.update_data(gender=gender)
    await state.set_state(Onboarding.age)
    await callback.message.edit_text(f"{GENDER_LABELS[gender]}. {CONFIRM}")
    await callback.message.answer("Возраст?")
    await callback.answer()


@router.message(StateFilter(Onboarding.age))
async def on_age(message: Message, state: FSMContext) -> None:
    if not message.text.isdigit() or not (10 <= int(message.text) <= 100):
        await message.answer("По факту, Андрюх, это не число. Думай. Ещё раз — цифрами.")
        return
    await state.update_data(age=int(message.text))
    await state.set_state(Onboarding.height)
    await message.answer("Рост, в см?")


@router.message(StateFilter(Onboarding.height))
async def on_height(message: Message, state: FSMContext) -> None:
    try:
        height = float(message.text.replace(",", "."))
        assert 100 <= height <= 250
    except (ValueError, AssertionError):
        await message.answer("Рост в см, цифрами. Думай.")
        return
    await state.update_data(height_cm=height)
    await state.set_state(Onboarding.weight)
    await message.answer("Текущий вес, в кг?")


@router.message(StateFilter(Onboarding.weight))
async def on_weight(message: Message, state: FSMContext) -> None:
    try:
        weight = float(message.text.replace(",", "."))
        assert 30 <= weight <= 300
    except (ValueError, AssertionError):
        await message.answer("Вес в кг, цифрами. Не для фантазий.")
        return
    await state.update_data(weight_kg=weight)
    await state.set_state(Onboarding.job_type)
    await message.answer(
        "Теперь активность. Честно, без сгущёнки в голове:\n\n"
        "Работа/учёба — сидячая или на ногах?",
        reply_markup=JOB_TYPE_KB,
    )


@router.callback_query(StateFilter(Onboarding.job_type), F.data.startswith("job:"))
async def on_job_type(callback: CallbackQuery, state: FSMContext) -> None:
    job_type = callback.data.split(":")[1]
    await state.update_data(job_type=job_type)
    await state.set_state(Onboarding.strength_freq)
    await callback.message.edit_text(CONFIRM)
    await callback.message.answer(
        "Силовые — сколько раз в неделю? Ноль — тоже ответ, но ты знаешь, что это значит.",
        reply_markup=STRENGTH_KB,
    )
    await callback.answer()


@router.callback_query(StateFilter(Onboarding.strength_freq), F.data.startswith("strength:"))
async def on_strength_freq(callback: CallbackQuery, state: FSMContext) -> None:
    strength_freq = callback.data.split(":")[1]
    await state.update_data(strength_freq=strength_freq)
    await state.set_state(Onboarding.cardio_freq)
    await callback.message.edit_text(CONFIRM)
    await callback.message.answer(
        "Кардио — сколько раз в неделю? Без самообмана.",
        reply_markup=CARDIO_KB,
    )
    await callback.answer()


@router.callback_query(StateFilter(Onboarding.cardio_freq), F.data.startswith("cardio:"))
async def on_cardio_freq(callback: CallbackQuery, state: FSMContext) -> None:
    cardio_freq = callback.data.split(":")[1]
    await state.update_data(cardio_freq=cardio_freq)
    await state.set_state(Onboarding.steps)
    await callback.message.edit_text(CONFIRM)
    await callback.message.answer(
        "Шаги в день — в среднем? Честно, не для красоты цифры.",
        reply_markup=STEPS_KB,
    )
    await callback.answer()


@router.callback_query(StateFilter(Onboarding.steps), F.data.startswith("steps:"))
async def on_steps(callback: CallbackQuery, state: FSMContext) -> None:
    steps_bucket = callback.data.split(":")[1]
    await state.update_data(steps_bucket=steps_bucket)
    await state.set_state(Onboarding.goal)
    await callback.message.edit_text(CONFIRM)
    await callback.message.answer("Цель. Без розовых очков.", reply_markup=GOAL_KB)
    await callback.answer()


@router.callback_query(StateFilter(Onboarding.goal), F.data.startswith("goal:"))
async def on_goal(callback: CallbackQuery, state: FSMContext) -> None:
    goal = callback.data.split(":")[1]
    await state.update_data(goal=goal)
    await callback.message.edit_text(CONFIRM)
    await callback.message.answer(GOAL_LINES[goal])

    if goal == "maintain":
        await finish_onboarding(callback.message, state)
    else:
        await state.set_state(Onboarding.target_weight)
        await callback.message.answer("Целевой вес, в кг?")
    await callback.answer()


@router.message(StateFilter(Onboarding.target_weight))
async def on_target_weight(message: Message, state: FSMContext) -> None:
    try:
        target = float(message.text.replace(",", "."))
        assert 30 <= target <= 300
    except (ValueError, AssertionError):
        await message.answer("Целевой вес в кг, цифрами. Мечты не считаются.")
        return
    await state.update_data(target_weight_kg=target)
    await state.set_state(Onboarding.pace)
    await message.answer("Темп? Выбирай трезво — быстрый не значит лучший.", reply_markup=PACE_KB)


@router.callback_query(StateFilter(Onboarding.pace), F.data.startswith("pace:"))
async def on_pace(callback: CallbackQuery, state: FSMContext) -> None:
    pace = callback.data.split(":")[1]
    await state.update_data(pace=pace)
    await callback.message.edit_text(CONFIRM)
    await finish_onboarding(callback.message, state)
    await callback.answer()


async def finish_onboarding(message: Message, state: FSMContext) -> None:
    data = await state.get_data()

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
            target_calories=target_calories,
            **macros,
            water_ml=water_ml,
        )
        await mark_active(session, user.id)

    await state.clear()
    await message.answer(
        "Норма готова. Это не предложение — это план.\n\n"
        f"🔥 Калории: {target_calories} ккал\n"
        f"🥩 Белки: {macros['protein_g']} г\n"
        f"🧈 Жиры: {macros['fat_g']} г\n"
        f"🍞 Углеводы: {macros['carbs_g']} г\n"
        f"💧 Вода: {water_ml} мл\n\n"
        f"<b>{random.choice(WOLF_QUOTES)}</b>\n\n"
        "Дневник и трекинг — дальше. Думай."
    )
