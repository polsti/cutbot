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
        "/weight — log your weight\n"
        "/progress — weight chart\n"
        "/goal — change your goal\n"
        "/assist — AI nutrition assistant\n"
        "/reminders — weigh-in reminders\n"
        "/settings — language and style\n"
        "/help — this help\n\n"
        "More (/fridge etc.) is coming."
    ),
    "fallback": "Didn't get that 🤔 Send a food photo to log a meal, or type /help.",
    "button_expired": "This button has expired — the bot restarted. Start again: /add",
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
    # weight
    "weigh_q": "What do you weigh today? In kg, e.g. 68.4",
    "weigh_saved": "⚖️ Saved: {weight} kg",
    "weigh_first": "That's your first entry — from now on I'll show your progress.",
    "weigh_since_last": "Since last time ({date}): {diff:+.1f} kg",
    "weigh_since_start": "Since the start: {diff:+.1f} kg",
    "weigh_good": "Great progress 💪",
    "weigh_left": "{left} kg left to your {target} kg goal 🔥",
    "weigh_reached": "🎉 Goal of {target} kg reached! Switch to maintain or gain — /goal",
    "chart_weight": "Weight",
    "chart_target": "Goal",
    "progress_summary": "📈 Start: {start} kg ({start_date})\nNow: {current} kg\nChange: {change:+.1f} kg in {days} days",
    "progress_first": "📈 Only one entry so far: {current} kg. Log your weight with /weight and the chart will show up here.",
    "goal_intro": "Pick your new goal:",
    "goal_updated": "Goal updated ✅ New daily norm (at {weight} kg):",
    # weigh-in reminders
    "rem_q": "Want to track your weight? I'll remind you in the morning when it's weigh day ⚖️",
    "rem_yes_no": {"yes": "✅ Yes", "no": "No, thanks"},
    "rem_freq_q": "How often do you want to weigh in?",
    "rem_freq_buttons": {"daily": "Every day", "every3": "Every 3 days", "weekly": "Once a week"},
    "rem_weekday_q": "Which day of the week?",
    "weekday_names": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
    "rem_time_q": "What time is it for you right now? E.g. 18:40 — that's how I'll know your timezone and message you in the morning.",
    "rem_time_error": "Send the time as HH:MM, e.g. 18:40",
    "rem_when": {"daily": "every day", "every3": "every 3 days", "weekly": "every week on {day}"},
    "rem_on": "Done ✅ I'll remind you at 08:00 your time, {when}. You can log your weight any other day too — /weight",
    "rem_off": "OK, no reminders. You can turn them on any time — /reminders",
    "reminder_msg": "⚖️ Today is weigh day! Best in the morning, before breakfast.",
    "reminder_btn": "⚖️ Log weight",
    # assistant
    "assist_intro": "🤖 AI assistant here. I can see your profile, daily norm, today's and this week's food, and your weight history.\n\nAsk anything: how to get more protein, why the weight isn't moving, what to eat for dinner.\n\n/stop — end the chat.",
    "assist_bye": "Chat ended. Come back any time — /assist",
    "assist_error": "Couldn't answer — the AI service is overloaded. Try again in a minute.",
    "assist_text_only": "In assistant mode, send text. To log a meal from a photo, /stop first.",
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
