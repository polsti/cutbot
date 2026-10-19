"""Козак — з гумором, по-нашому (Ukrainian)."""

VOICE = {
    "lang": "uk",
    "label": "🇺🇦 Козак",
    "gender_labels": {"m": "Козак", "f": "Козачка"},
    "confirm": "Записав, козаче ✅",
    "welcome_back": "О, хто повернувся! {quote}",
    "start_intro": "Привіт! Рахуємо калорії по-козацьки.\n\n{quote}\n\nКілька питань. Відповідай чесно — трекер усе бачить.\n\nСтать?",
    "age_error": "Шо ти, козаче, це ж не число. Ще раз — цифрами.",
    "height_error": "Зріст у см, цифрами.",
    "weight_error": "Вага в кг, цифрами. Без фантазій.",
    "activity_intro": "Тепер активність. Чесно:\n\nРобота/навчання — сидяча чи на ногах?",
    "goal_lines": {
        "lose": "Худнемо. Сало — по святах.",
        "gain": "Набираємо. Вареники в поміч, але з розумом.",
        "maintain": "Тримаємо форму. Козак має бути в тонусі.",
    },
    "target_weight_error": "Цільова вага в кг, цифрами. Мрії не рахуються.",
    "final_summary_lead": "Норма готова. Це не порада — це план.",
    "final_summary_tail": "Щоденник і трекінг — далі. Тримайся, козаче.",
    # TODO(Polina): replace with your own quotes
    "quotes": [
        "Козацькому роду нема переводу.",
        "Терпи, козаче, отаманом будеш.",
        "Де сила — там і воля.",
    ],
    "fridge_empty_line": "Холодильник порожній — навіть сала нема.",  # reserved for the fridge feature, not built yet
    "share_meal_prompt": "Надсилай фото їжі 📸",
    "not_a_photo": "Це не фото, козаче. Надішли фото їжі.",
    "description_prompt": "Хочеш додати опис? (наприклад: без олії, 100 г рису, курка)\n\nТак розрахунок буде точнішим.",
    "thinking": "Дивлюсь на фото... 🤔",
    "vision_error": "Не вийшло розібрати фото. Надішли ще раз, з іншого ракурсу.",
    "meal_result_lead": "Це оцінка, не аптечна точність. Додаємо?",
    "meal_cancel": "Скасовано. Не страшно — тисни /add, коли будеш готовий.",
    "today_no_profile": "Спершу профіль. /start — і поїхали.",
    "today_empty": "Сьогодні поки порожньо. /add — і додавай.",
    "today_lead": "Сьогодні:",
    "week_lead": "Останні 7 днів:",
    "week_no_data": "— (нічого не записано)",
    # TODO(Polina): replace with your own quotes
    # How the /assist AI should talk (instruction for the model, in English)
    "assistant_style": "Friendly Ukrainian humour, cossack jokes ('козаче', 'шо ти, козаче'), playful but caring.",
    "help_quote_pool": [
        "Дисципліна — це свобода.",
        "Без зусиль нема результату.",
        "Крок за кроком — і до мети.",
    ],
}
