from aiogram import F, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

from bot.models.base import async_session
from bot.services.meals import get_today_totals, save_meal_entry
from bot.services.profiles import get_profile
from bot.services.users import get_or_create_user
from bot.services.vision import analyze_meal_photo
from bot.style import CONFIRM

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


@router.callback_query(F.data == "share_meal")
async def on_share_meal(callback: CallbackQuery, state: FSMContext) -> None:
    await start_meal_log(callback.message, state)
    await callback.answer()


@router.message(Command("add"))
async def cmd_add(message: Message, state: FSMContext) -> None:
    await start_meal_log(message, state)


async def start_meal_log(message: Message, state: FSMContext) -> None:
    await state.set_state(MealLog.waiting_photo)
    await message.answer("Пришли фото еды 📸")


@router.message(StateFilter(MealLog.waiting_photo), F.photo)
async def on_photo(message: Message, state: FSMContext) -> None:
    photo = message.photo[-1]  # largest resolution
    file = await message.bot.get_file(photo.file_id)
    buffer = await message.bot.download_file(file.file_path)

    await state.update_data(photo_bytes=buffer.read(), photo_file_id=photo.file_id)
    await state.set_state(MealLog.waiting_description)
    await message.answer(
        "Хочешь написать описание? (например: без масла, 100 г риса, свинина)\n\n"
        "Это повышает точность расчёта.",
        reply_markup=SKIP_DESCRIPTION_KB,
    )


@router.message(StateFilter(MealLog.waiting_photo))
async def on_not_a_photo(message: Message) -> None:
    await message.answer("Это не фото. Пришли фото еды — по факту, Андрюх.")


@router.callback_query(StateFilter(MealLog.waiting_description), F.data == "skip_description")
async def on_skip_description(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.message.edit_text(CONFIRM)
    await run_analysis(callback.message, state, description=None)
    await callback.answer()


@router.message(StateFilter(MealLog.waiting_description))
async def on_description(message: Message, state: FSMContext) -> None:
    await run_analysis(message, state, description=message.text)


async def run_analysis(message: Message, state: FSMContext, description: str | None) -> None:
    data = await state.get_data()
    thinking = await message.answer("Думаю над фото... 🤔")

    try:
        result = analyze_meal_photo(data["photo_bytes"], "image/jpeg", description)
    except Exception:
        await thinking.edit_text("Не вышло разобрать фото. Пришли ещё раз, по-другому ракурсом.")
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
        "Это оценка, не аптекарская точность. Добавляем?",
        reply_markup=CONFIRM_MEAL_KB,
    )


@router.callback_query(StateFilter(MealLog.confirming), F.data == "confirm_meal")
async def on_confirm_meal(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()

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

    await state.clear()
    await callback.message.edit_text(f"{CONFIRM} Записано в дневник.")
    await callback.answer()


@router.callback_query(StateFilter(MealLog.confirming), F.data == "cancel_meal")
async def on_cancel_meal(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.message.edit_text("Отменено. Не страшно — пришли /start и жми 'Поделиться едой' заново, когда будешь готов.")
    await callback.answer()


@router.message(Command("today"))
async def cmd_today(message: Message) -> None:
    async with async_session() as session:
        user = await get_or_create_user(session, message.from_user.id)
        profile = await get_profile(session, user.id)
        totals = await get_today_totals(session, user.id)

    if profile is None:
        await message.answer("Сначала профиль. /start — и погнали.")
        return

    if totals["count"] == 0:
        await message.answer("Сегодня пока пусто. Жми /start → 'Поделиться едой' и добавляй.")
        return

    cal_left = profile.target_calories - totals["calories"]
    protein_left = profile.protein_g - totals["protein_g"]
    fat_left = profile.fat_g - totals["fat_g"]
    carbs_left = profile.carbs_g - totals["carbs_g"]

    await message.answer(
        f"Сегодня съедено ({totals['count']} приём(ов)):\n\n"
        f"🔥 {totals['calories']} / {profile.target_calories} ккал (осталось {cal_left})\n"
        f"🥩 {totals['protein_g']} / {profile.protein_g} г белка (осталось {protein_left})\n"
        f"🧈 {totals['fat_g']} / {profile.fat_g} г жиров (осталось {fat_left})\n"
        f"🍞 {totals['carbs_g']} / {profile.carbs_g} г углеводов (осталось {carbs_left})\n\n"
        f"{CONFIRM}"
    )
