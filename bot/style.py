"""Shared bot voice — Andrey Smaev (Андрей Смаев) meme style: deadpan,
absurdist "alpha wolf" pseudo-wisdom, streetlifting/сгущёнка references.

Centralized here so every handler (onboarding, and later the food diary,
activity log, fridge, etc.) pulls from the same voice instead of each
file inventing its own flavor text.
"""

GENDER_LABELS = {"m": "Рыба-меч", "f": "Малышка"}

CONFIRM = "По факту, Андрюх ✅"

GOAL_LINES = {
    "lose": "Вот и думайте.",
    "gain": "Че, пацаны, по сгущёнке?",
    "maintain": "Сколько волка ни корми — он всё равно на сгущёнку смотрит.",
}

# Reserved for the fridge/photo-recognition feature (not built yet, later phase).
# Use when the recognized fridge contents are basically empty.
FRIDGE_EMPTY_LINE = "У тебя нет даже Бобров и Грибов."

WOLF_QUOTES = [
    "Если тебе тяжело идти, значит, ты забыл снять гири. Думай.",
    "Неважно, сколько у тебя денег. Важно, сколько у тебя денег на самом деле.",
    "Работа — не волк. Работа — это ворк. А волк — это ходить.",
    "Я не ленивый. Я просто нахожусь в режиме энергосбережения ради будущих миллионов.",
    "Пока они спали, я спал. Мы разные.",
]
