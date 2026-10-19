"""Ukrainian UI text — prompts, buttons and number formats shared by all
Ukrainian voices. Personality lines live in bot/voices/, not here."""

TEXTS = {
    "gemini_language": "українська",
    "choose_theme": "Обери стиль спілкування бота:",
    "theme_changed": "Стиль змінено: {label}",
    "help": (
        "Команди:\n"
        "/start — профіль\n"
        "/add — записати прийом їжі за фото\n"
        "/today — підсумок за сьогодні\n"
        "/stats — за останні 7 днів\n"
        "/weight — записати вагу\n"
        "/progress — графік ваги\n"
        "/goal — змінити мету\n"
        "/reminders — нагадування про зважування\n"
        "/settings — мова і стиль спілкування\n"
        "/help — довідка\n\n"
        "Решта (/fridge тощо) — далі за планом."
    ),
    "fallback": "Не зрозумів 🤔 Надішли фото їжі, щоб записати прийом, або набери /help.",
    "button_expired": "Ця кнопка застаріла — бот перезапускався. Почни заново: /add",
    # onboarding
    "age_q": "Вік?",
    "height_q": "Зріст, у см?",
    "weight_q": "Поточна вага, у кг?",
    "job_buttons": {
        "office": "Сидяча робота / навчання",
        "physical": "Фізична робота / на ногах",
    },
    "strength_q": "Силові — скільки разів на тиждень? Нуль — теж відповідь, але ти знаєш, що це означає.",
    "cardio_q": "Кардіо — скільки разів на тиждень? Без самообману.",
    "frequency_labels": {
        "0": "Не займаюсь",
        "1-2": "1–2 рази на тиждень",
        "3-4": "3–4 рази на тиждень",
        "5+": "5+ разів на тиждень",
    },
    "steps_q": "Кроків на день — у середньому? Чесно, не для краси.",
    "steps_labels": {
        "<5000": "Менше 5 000",
        "5000-10000": "5 000 – 10 000",
        "10000-15000": "10 000 – 15 000",
        "15000+": "Більше 15 000",
    },
    "goal_q": "Мета. Без рожевих окулярів.",
    "goal_buttons": {
        "maintain": "Підтримка ваги",
        "lose": "Схуднення",
        "gain": "Набір маси",
    },
    "target_weight_q": "Цільова вага, у кг?",
    "pace_q": "Темп? Обирай тверезо — швидкий не означає кращий.",
    "pace_buttons": {
        "slow": "Повільний",
        "medium": "Середній",
        "fast": "Швидкий",
    },
    "share_meal_btn": "📸 Поділитися їжею",
    "macros_block": (
        "🔥 Калорії: {calories} ккал\n"
        "🥩 Білки: {protein_g} г\n"
        "🧈 Жири: {fat_g} г\n"
        "🍞 Вуглеводи: {carbs_g} г"
    ),
    "water_line": "💧 Вода: {water_ml} мл",
    # weight
    "weigh_q": "Скільки важиш сьогодні? У кг, наприклад 68.4",
    "weigh_saved": "⚖️ Записав: {weight} кг",
    "weigh_first": "Це перший запис — далі показуватиму прогрес.",
    "weigh_since_last": "З минулого разу ({date}): {diff:+.1f} кг",
    "weigh_since_start": "З самого початку: {diff:+.1f} кг",
    "weigh_good": "Чудовий прогрес 💪",
    "weigh_left": "До мети {target} кг залишилось {left} кг 🔥",
    "weigh_reached": "🎉 Мету {target} кг досягнуто! Можна змінити мету на підтримку або набір — /goal",
    "chart_weight": "Вага",
    "chart_target": "Мета",
    "progress_summary": "📈 Старт: {start} кг ({start_date})\nЗараз: {current} кг\nЗміна: {change:+.1f} кг за {days} дн.",
    "progress_first": "📈 Поки один запис: {current} кг. Записуй вагу через /weight — і тут зʼявиться графік.",
    "goal_intro": "Обери нову мету:",
    "goal_updated": "Мету оновлено ✅ Нова норма (за вагою {weight} кг):",
    # weigh-in reminders
    "rem_q": "Хочеш відстежувати вагу? Вранці нагадуватиму, що сьогодні день зважування ⚖️",
    "rem_yes_no": {"yes": "✅ Так", "no": "Ні, дякую"},
    "rem_freq_q": "Як часто зважуватися?",
    "rem_freq_buttons": {"daily": "Щодня", "every3": "Раз на 3 дні", "weekly": "Раз на тиждень"},
    "rem_weekday_q": "В який день тижня?",
    "weekday_names": ["Понеділок", "Вівторок", "Середа", "Четвер", "Пʼятниця", "Субота", "Неділя"],
    "rem_time_q": "Котра в тебе зараз година? Наприклад 18:40 — так я зрозумію твій часовий пояс і напишу саме вранці.",
    "rem_time_error": "Напиши час у форматі ГГ:ХХ, наприклад 18:40",
    "rem_when": {"daily": "щодня", "every3": "раз на 3 дні", "weekly": "щотижня — {day}"},
    "rem_on": "Готово ✅ Нагадаю о 08:00 за твоїм часом, {when}. Вагу можна записати й у будь-який інший день — /weight",
    "rem_off": "Ок, без нагадувань. Увімкнути можна будь-коли — /reminders",
    "reminder_msg": "⚖️ Сьогодні день зважування! Краще вранці, натщесерце.",
    "reminder_btn": "⚖️ Записати вагу",
    # meals
    "skip_description_btn": "Без опису",
    "add_to_diary_btn": "✅ Додати в щоденник",
    "cancel_btn": "❌ Скасувати",
    "week_btn": "📅 Тиждень",
    "day_names": ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Нд"],
    "saved_to_diary": "Записано в щоденник.",
    "total_today": "Разом сьогодні: {calories}{target} ккал ({count} прийом(ів))",
    "today_meal_line": "{time} — {dish}: {calories} ккал",
    "today_totals": (
        "🔥 {calories} / {target_calories} ккал (залишилось {cal_left})\n"
        "🥩 {protein_g} / {target_protein_g} г білка (залишилось {protein_left})\n"
        "🧈 {fat_g} / {target_fat_g} г жирів (залишилось {fat_left})\n"
        "🍞 {carbs_g} / {target_carbs_g} г вуглеводів (залишилось {carbs_left})"
    ),
    "week_day_line": "{label}: {calories} ккал ({count} прийом(ів)) — Б:{protein_g} Ж:{fat_g} В:{carbs_g}",
    "week_avg": "Середнє за дні із записами: {avg} ккал",
}
