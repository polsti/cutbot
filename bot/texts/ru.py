"""Russian UI text — prompts, buttons and number formats shared by all
Russian voices. Personality lines live in bot/voices/, not here."""

TEXTS = {
    "gemini_language": "русский",
    "choose_theme": "Выбери стиль общения бота:",
    "theme_changed": "Стиль изменён: {label}",
    "help": (
        "Команды:\n"
        "/start — профиль\n"
        "/add — записать приём пищи по фото\n"
        "/today — сводка за сегодня\n"
        "/stats — за последние 7 дней\n"
        "/settings — язык и стиль общения\n"
        "/help — справка\n\n"
        "Остальное (/fridge и т.д.) — дальше по плану."
    ),
    # onboarding
    "age_q": "Возраст?",
    "height_q": "Рост, в см?",
    "weight_q": "Текущий вес, в кг?",
    "job_buttons": {
        "office": "Сидячая работа/учёба",
        "physical": "Физическая работа / на ногах",
    },
    "strength_q": "Силовые — сколько раз в неделю? Ноль — тоже ответ, но ты знаешь, что это значит.",
    "cardio_q": "Кардио — сколько раз в неделю? Без самообмана.",
    "frequency_labels": {
        "0": "Не занимаюсь",
        "1-2": "1–2 раза в неделю",
        "3-4": "3–4 раза в неделю",
        "5+": "5+ раз в неделю",
    },
    "steps_q": "Шаги в день — в среднем? Честно, не для красоты цифры.",
    "steps_labels": {
        "<5000": "Меньше 5 000",
        "5000-10000": "5 000 – 10 000",
        "10000-15000": "10 000 – 15 000",
        "15000+": "Больше 15 000",
    },
    "goal_q": "Цель. Без розовых очков.",
    "goal_buttons": {
        "maintain": "Поддержание веса",
        "lose": "Похудение",
        "gain": "Набор массы",
    },
    "target_weight_q": "Целевой вес, в кг?",
    "pace_q": "Темп? Выбирай трезво — быстрый не значит лучший.",
    "pace_buttons": {
        "slow": "Медленный",
        "medium": "Средний",
        "fast": "Быстрый",
    },
    "share_meal_btn": "📸 Поделиться едой",
    "macros_block": (
        "🔥 Калории: {calories} ккал\n"
        "🥩 Белки: {protein_g} г\n"
        "🧈 Жиры: {fat_g} г\n"
        "🍞 Углеводы: {carbs_g} г"
    ),
    "water_line": "💧 Вода: {water_ml} мл",
    # meals
    "skip_description_btn": "Без описания",
    "add_to_diary_btn": "✅ Добавить в дневник",
    "cancel_btn": "❌ Отмена",
    "week_btn": "📅 Неделя",
    "day_names": ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"],
    "saved_to_diary": "Записано в дневник.",
    "total_today": "Итого сегодня: {calories}{target} ккал ({count} приём(ов))",
    "today_meal_line": "{time} — {dish}: {calories} ккал",
    "today_totals": (
        "🔥 {calories} / {target_calories} ккал (осталось {cal_left})\n"
        "🥩 {protein_g} / {target_protein_g} г белка (осталось {protein_left})\n"
        "🧈 {fat_g} / {target_fat_g} г жиров (осталось {fat_left})\n"
        "🍞 {carbs_g} / {target_carbs_g} г углеводов (осталось {carbs_left})"
    ),
    "week_day_line": "{label}: {calories} ккал ({count} приём(ов)) — Б:{protein_g} Ж:{fat_g} У:{carbs_g}",
    "week_avg": "Среднее за дни с записями: {avg} ккал",
}
