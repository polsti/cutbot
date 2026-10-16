from aiogram import F, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

from bot.models.base import async_session
from bot.services.meals import get_today_entries, get_today_totals, get_week_totals, save_meal_entry
from bot.services.profiles import get_profile
from bot.services.users import get_or_create_user
from bot.services.vision import analyze_meal_photo
from bot.voices import DEFAULT_VOICE, get_voice

router = Router()


class MealLog(StatesGroup):
    waiting_photo = State()
    waiting_description = State()
    confirming = State()


SKIP_DESCRIPTION_KB = InlineKeyboardMarkup(
    inline_keyboard=[[InlineKeyboardButton(text="Без описания", callback_data="skip_description")]]
)

CONFIRM_MEAL_KB = InlineKeyboardMarkup(
    inline_keyboard=[[
        InlineKeyboardButton(text="✅ Добавить в дневник", callback_data="confirm_meal"),
        InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_meal"),
    ]]
)

WEEK_KB = InlineKeyboardMarkup(
    inline_keyboard=[[InlineKeyboardButton(text="📅 Неделя", callback_data="show_week")]]
)

DAY_NAMES = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]


@router.callback_query(F.data == "share_meal")
async def on_share_meal(callback: CallbackQuery, state: FSMContext) -> None:
    await start_meal_log(callback.from_user.id, callback.message, state)
    await callback.answer()


@router.message(Command("add"))
async def cmd_add(message: Message, state: FSMContext) -> None:
    await start_meal_log(message.from_user.id, message, state)


async def start_meal_log(telegram_id: int, message: Message, state: FSMContext) -> None:
    async with async_session() as session:
        user = await get_or_create_user(session, telegram_id)
    voice = get_voice(user.voice)

    await state.set_state(MealLog.waiting_photo)
    await state.update_data(voice=user.voice)
    await message.answer(voice["share_meal_prompt"])


@router.message(StateFilter(MealLog.waiting_photo), F.photo)
async def on_photo(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    voice = get_voice(data.get("voice", DEFAULT_VOICE))

    photo = message.photo[-1]  # largest resolution
    file = await message.bot.get_file(photo.file_id)
    buffer = await message.bot.download_file(file.file_path)

    await state.update_data(photo_bytes=buffer.read(), photo_file_id=photo.file_id)
    await state.set_state(MealLog.waiting_description)
    await message.answer(voice["description_prompt"], reply_markup=SKIP_DESCRIPTION_KB)


@router.message(StateFilter(MealLog.waiting_photo))
async def on_not_a_photo(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    voice = get_voice(data.get("voice", DEFAULT_VOICE))
    await message.answer(voice["not_a_photo"])


@router.callback_query(StateFilter(MealLog.waiting_description), F.data == "skip_description")
async def on_skip_description(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    voice = get_voice(data.get("voice", DEFAULT_VOICE))
    await callback.message.edit_text(voice["confirm"])
    await run_analysis(callback.message, state, description=None)
    await callback.answer()


@router.message(StateFilter(MealLog.waiting_description))
async def on_description(message: Message, state: FSMContext) -> None:
    await run_analysis(message, state, description=message.text)


async def run_analysis(message: Message, state: FSMContext, description: str | None) -> None:
    data = await state.get_data()
    voice = get_voice(data.get("voice", DEFAULT_VOICE))
    thinking = await message.answer(voice["thinking"])

    try:
        result = analyze_meal_photo(data["photo_bytes"], "image/jpeg", description)
    except Exception:
        await thinking.edit_text(voice["vision_error"])
        await state.set_state(MealLog.waiting_photo)
        return

    await state.update_data(description=description, **result)
    await state.set_state(MealLog.confirming)

    note_line = f"\n\n⚠️ {result['note']}" if result.get("note") else ""
    await thinking.edit_text(
        f"<b>{result['dish_name']}</b>\n\n"
        f"🔥 Калории: {result['calories']} ккал\n"
        f"🥩 Белки: {result['protein_g']} г\n"
        f"🧈 Жиры: {result['fat_g']} г\n"
        f"🍞 Углеводы: {result['carbs_g']} г"
        f"{note_line}\n\n"
        f"{voice['meal_result_lead']}",
        reply_markup=CONFIRM_MEAL_KB,
    )


@router.callback_query(StateFilter(MealLog.confirming), F.data == "confirm_meal")
async def on_confirm_meal(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    voice = get_voice(data.get("voice", DEFAULT_VOICE))

    async with async_session() as session:
        user = await get_or_create_user(session, callback.message.chat.id)
        await save_meal_entry(
            session,
            user_id=user.id,
            dish_name=data["dish_name"],
            description=data.get("description"),
            note=data.get("note", ""),
            photo_file_id=data.get("photo_file_id"),
            calories=data["calories"],
            protein_g=data["protein_g"],
            fat_g=data["fat_g"],
            carbs_g=data["carbs_g"],
        )
        profile = await get_profile(session, user.id)
        totals = await get_today_totals(session, user.id)

    await state.clear()

    target_line = f" / {profile.target_calories}" if profile else ""
    await callback.message.edit_text(
        f"{voice['confirm']} Записано в дневник.\n\n"
        f"Итого сегодня: {totals['calories']}{target_line} ккал ({totals['count']} приём(ов))"
    )
    await callback.answer()


@router.callback_query(StateFilter(MealLog.confirming), F.data == "cancel_meal")
async def on_cancel_meal(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    voice = get_voice(data.get("voice", DEFAULT_VOICE))
    await state.clear()
    await callback.message.edit_text(voice["meal_cancel"])
    await callback.answer()


@router.message(Command("today"))
async def cmd_today(message: Message) -> None:
    text = await build_today_text(message.from_user.id)
    await message.answer(text, reply_markup=WEEK_KB)


async def build_today_text(telegram_id: int) -> str:
    async with async_session() as session:
        user = await get_or_create_user(session, telegram_id)
        profile = await get_profile(session, user.id)
        entries = await get_today_entries(session, user.id)

    voice = get_voice(user.voice)

    if profile is None:
        return voice["today_no_profile"]

    if not entries:
        return voice["today_empty"]

    totals = {
        "calories": sum(e.calories for e in entries),
        "protein_g": sum(e.protein_g for e in entries),
        "fat_g": sum(e.fat_g for e in entries),
        "carbs_g": sum(e.carbs_g for e in entries),
    }
    cal_left = profile.target_calories - totals["calories"]
    protein_left = profile.protein_g - totals["protein_g"]
    fat_left = profile.fat_g - totals["fat_g"]
    carbs_left = profile.carbs_g - totals["carbs_g"]

    meal_lines = [
        f"{e.logged_at.strftime('%H:%M')} — {e.dish_name}: {e.calories} ккал" for e in entries
    ]

    return (
        f"{voice['today_lead']}\n\n"
        + "\n".join(meal_lines)
        + "\n\n"
        f"🔥 {totals['calories']} / {profile.target_calories} ккал (осталось {cal_left})\n"
        f"🥩 {totals['protein_g']} / {profile.protein_g} г белка (осталось {protein_left})\n"
        f"🧈 {totals['fat_g']} / {profile.fat_g} г жиров (осталось {fat_left})\n"
        f"🍞 {totals['carbs_g']} / {profile.carbs_g} г углеводов (осталось {carbs_left})\n\n"
        f"{voice['confirm']}"
    )


@router.message(Command("stats"))
async def cmd_stats(message: Message) -> None:
    text = await build_week_text(message.from_user.id)
    await message.answer(text)


@router.callback_query(F.data == "show_week")
async def on_show_week(callback: CallbackQuery) -> None:
    text = await build_week_text(callback.from_user.id)
    await callback.message.answer(text)
    await callback.answer()


async def build_week_text(telegram_id: int) -> str:
    async with async_session() as session:
        user = await get_or_create_user(session, telegram_id)
        days = await get_week_totals(session, user.id)

    voice = get_voice(user.voice)

    lines = []
    for day in days:
        label = f"{DAY_NAMES[day['date'].weekday()]} {day['date'].strftime('%d.%m')}"
        if day["count"] == 0:
            lines.append(f"{label}: {voice['week_no_data']}")
        else:
            lines.append(
                f"{label}: {day['calories']} ккал ({day['count']} приём(ов)) "
                f"— Б:{day['protein_g']} Ж:{day['fat_g']} У:{day['carbs_g']}"
            )

    logged_days = [d for d in days if d["count"] > 0]
    avg_line = ""
    if logged_days:
        avg_calories = round(sum(d["calories"] for d in logged_days) / len(logged_days))
        avg_line = f"\n\nСреднее за дни с записями: {avg_calories} ккал"

    return f"{voice['week_lead']}\n\n" + "\n".join(lines) + avg_line + f"\n\n{voice['confirm']}"
