from aiogram import F, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

from bot.handlers.onboarding import row_kb
from bot.models.base import async_session
from bot.services.calculations import calculate_norms, weight_progress
from bot.services.profiles import get_profile, save_profile
from bot.services.users import get_or_create_user
from bot.services.weights import add_weight_entry, ensure_start_entry, get_weight_entries
from bot.texts import texts_for
from bot.voices import DEFAULT_VOICE, get_voice

router = Router()


class WeightLog(StatesGroup):
    waiting_weight = State()


class GoalChange(StatesGroup):
    goal = State()
    target_weight = State()
    pace = State()


def fmt_kg(value: float) -> str:
    return f"{value:g}"


def parse_kg(text: str | None) -> float | None:
    try:
        value = float((text or "").replace(",", "."))
    except ValueError:
        return None
    return value if 30 <= value <= 300 else None


async def _voice_and_texts(state: FSMContext) -> tuple[dict, dict]:
    data = await state.get_data()
    voice = get_voice(data.get("voice", DEFAULT_VOICE))
    return voice, texts_for(voice)


# --- /weight: log a weigh-in any day ---------------------------------------

@router.message(Command("weight"))
async def cmd_weight(message: Message, state: FSMContext) -> None:
    await ask_weight(message.from_user.id, message, state)


@router.callback_query(F.data == "weigh")  # button on the morning reminder (phase 10)
async def on_weigh_button(callback: CallbackQuery, state: FSMContext) -> None:
    await ask_weight(callback.from_user.id, callback.message, state)
    await callback.answer()


async def ask_weight(telegram_id: int, message: Message, state: FSMContext) -> None:
    async with async_session() as session:
        user = await get_or_create_user(session, telegram_id)
    voice = get_voice(user.voice)
    await state.set_state(WeightLog.waiting_weight)
    await state.update_data(voice=user.voice)
    await message.answer(texts_for(voice)["weigh_q"])


@router.message(StateFilter(WeightLog.waiting_weight), ~F.text.startswith("/"))
async def on_weight_value(message: Message, state: FSMContext) -> None:
    voice, t = await _voice_and_texts(state)
    weight = parse_kg(message.text)
    if weight is None:
        await message.answer(voice["weight_error"])
        return

    async with async_session() as session:
        user = await get_or_create_user(session, message.from_user.id)
        await ensure_start_entry(session, user.id)
        await add_weight_entry(session, user.id, weight)
        entries = await get_weight_entries(session, user.id)
        profile = await get_profile(session, user.id)
    await state.clear()

    goal = profile.goal if profile else "maintain"
    target = profile.target_weight_kg if profile else None
    p = weight_progress([e.weight_kg for e in entries], goal, target)

    lines = [t["weigh_saved"].format(weight=fmt_kg(weight))]
    if p["since_last"] is None:
        lines.append(t["weigh_first"])
    else:
        lines.append(t["weigh_since_last"].format(date=entries[-2].recorded_at.strftime("%d.%m"), diff=p["since_last"]))
        if len(entries) > 2:
            lines.append(t["weigh_since_start"].format(diff=p["since_start"]))
    if p["toward_goal"]:
        lines.append(t["weigh_good"])
    if p["reached"]:
        lines.append(t["weigh_reached"].format(target=fmt_kg(target)))
    elif p["left"] is not None:
        lines.append(t["weigh_left"].format(target=fmt_kg(target), left=fmt_kg(p["left"])))

    await message.answer("\n".join(lines))


# --- /goal: change goal + target, recalculate the norm ---------------------

@router.message(Command("goal"))
async def cmd_goal(message: Message, state: FSMContext) -> None:
    async with async_session() as session:
        user = await get_or_create_user(session, message.from_user.id)
        profile = await get_profile(session, user.id)
    voice = get_voice(user.voice)
    t = texts_for(voice)

    if profile is None:
        await message.answer(voice["today_no_profile"])
        return

    await state.set_state(GoalChange.goal)
    await state.update_data(voice=user.voice)
    await message.answer(t["goal_intro"], reply_markup=row_kb("newgoal", t["goal_buttons"]))


@router.callback_query(StateFilter(GoalChange.goal), F.data.startswith("newgoal:"))
async def on_new_goal(callback: CallbackQuery, state: FSMContext) -> None:
    voice, t = await _voice_and_texts(state)
    goal = callback.data.split(":")[1]
    await state.update_data(goal=goal)
    await callback.message.edit_text(voice["confirm"])
    await callback.message.answer(voice["goal_lines"][goal])

    if goal == "maintain":
        await finish_goal_change(callback.message, callback.from_user.id, state)
    else:
        await state.set_state(GoalChange.target_weight)
        await callback.message.answer(t["target_weight_q"])
    await callback.answer()


@router.message(StateFilter(GoalChange.target_weight), ~F.text.startswith("/"))
async def on_new_target_weight(message: Message, state: FSMContext) -> None:
    voice, t = await _voice_and_texts(state)
    target = parse_kg(message.text)
    if target is None:
        await message.answer(voice["target_weight_error"])
        return
    await state.update_data(target_weight_kg=target)
    await state.set_state(GoalChange.pace)
    await message.answer(t["pace_q"], reply_markup=row_kb("newpace", t["pace_buttons"]))


@router.callback_query(StateFilter(GoalChange.pace), F.data.startswith("newpace:"))
async def on_new_pace(callback: CallbackQuery, state: FSMContext) -> None:
    voice, _ = await _voice_and_texts(state)
    await state.update_data(pace=callback.data.split(":")[1])
    await callback.message.edit_text(voice["confirm"])
    await finish_goal_change(callback.message, callback.from_user.id, state)
    await callback.answer()


async def finish_goal_change(message: Message, telegram_id: int, state: FSMContext) -> None:
    data = await state.get_data()
    voice, t = await _voice_and_texts(state)
    goal = data["goal"]
    pace = data.get("pace") if goal != "maintain" else None
    target = data.get("target_weight_kg") if goal != "maintain" else None

    async with async_session() as session:
        user = await get_or_create_user(session, telegram_id)
        profile = await get_profile(session, user.id)
        norms = calculate_norms(
            profile.gender, profile.age, profile.height_cm, profile.weight_kg,
            profile.activity_coefficient, goal, pace,
        )
        await save_profile(session, user.id, goal=goal, pace=pace, target_weight_kg=target, **norms)
        weight = profile.weight_kg

    await state.clear()
    macros = {k: norms[k] for k in ("protein_g", "fat_g", "carbs_g")}
    await message.answer(
        f"{t['goal_updated'].format(weight=fmt_kg(weight))}\n\n"
        f"{t['macros_block'].format(calories=norms['target_calories'], **macros)}\n"
        f"{t['water_line'].format(water_ml=norms['water_ml'])}\n\n"
        f"{voice['confirm']}"
    )
