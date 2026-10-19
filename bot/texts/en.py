"""English UI text — prompts, buttons and number formats shared by all
English voices. Personality lines live in bot/voices/, not here."""

TEXTS = {
    "gemini_language": "English",
    "choose_theme": "Pick the bot's vibe:",
    "theme_changed": "Style changed: {label}",
    "help": (
        "Commands:\n"
        "/start — profile\n"
        "/add — log a meal from a photo\n"
        "/today — today's summary\n"
        "/stats — last 7 days\n"
        "/settings — language and style\n"
        "/help — this help\n\n"
        "More (/fridge etc.) is coming."
    ),
    # onboarding
    "age_q": "Age?",
    "height_q": "Height, in cm?",
    "weight_q": "Current weight, in kg?",
    "job_buttons": {
        "office": "Desk job / studying",
        "physical": "Physical job / on my feet",
    },
    "strength_q": "Strength training — how many times a week? Zero is an answer too, but you know what it means.",
    "cardio_q": "Cardio — how many times a week? No lying to yourself.",
    "frequency_labels": {
        "0": "I don't",
        "1-2": "1–2 times a week",
        "3-4": "3–4 times a week",
        "5+": "5+ times a week",
    },
    "steps_q": "Steps per day, on average? Real numbers, not dream numbers.",
    "steps_labels": {
        "<5000": "Under 5,000",
        "5000-10000": "5,000 – 10,000",
        "10000-15000": "10,000 – 15,000",
        "15000+": "Over 15,000",
    },
    "goal_q": "Your goal. No rose-tinted glasses.",
    "goal_buttons": {
        "maintain": "Maintain weight",
        "lose": "Lose weight",
        "gain": "Gain muscle",
    },
    "target_weight_q": "Target weight, in kg?",
    "pace_q": "Pace? Choose wisely — faster isn't better.",
    "pace_buttons": {
        "slow": "Slow",
        "medium": "Medium",
        "fast": "Fast",
    },
    "share_meal_btn": "📸 Share a meal",
    "macros_block": (
        "🔥 Calories: {calories} kcal\n"
        "🥩 Protein: {protein_g} g\n"
        "🧈 Fat: {fat_g} g\n"
        "🍞 Carbs: {carbs_g} g"
    ),
    "water_line": "💧 Water: {water_ml} ml",
    # meals
    "skip_description_btn": "No description",
    "add_to_diary_btn": "✅ Add to diary",
    "cancel_btn": "❌ Cancel",
    "week_btn": "📅 Week",
    "day_names": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
    "saved_to_diary": "Saved to your diary.",
    "total_today": "Today so far: {calories}{target} kcal ({count} meal(s))",
    "today_meal_line": "{time} — {dish}: {calories} kcal",
    "today_totals": (
        "🔥 {calories} / {target_calories} kcal ({cal_left} left)\n"
        "🥩 {protein_g} / {target_protein_g} g protein ({protein_left} left)\n"
        "🧈 {fat_g} / {target_fat_g} g fat ({fat_left} left)\n"
        "🍞 {carbs_g} / {target_carbs_g} g carbs ({carbs_left} left)"
    ),
    "week_day_line": "{label}: {calories} kcal ({count} meal(s)) — P:{protein_g} F:{fat_g} C:{carbs_g}",
    "week_avg": "Average on logged days: {avg} kcal",
}
