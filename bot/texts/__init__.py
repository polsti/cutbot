"""UI text per language. Every language file must have the same keys as
ru.py — tests/test_texts.py checks this.

To add a language: copy ru.py, translate every value, register it in
TEXTS and LANGUAGE_LABELS below, and add at least one voice for it in
bot/voices/.
"""

from bot.texts import en, ru, uk

TEXTS = {"ru": ru.TEXTS, "en": en.TEXTS, "uk": uk.TEXTS}

# Order here = order of the buttons in the language picker.
LANGUAGE_LABELS = {
    "en": "🇬🇧 English",
    "uk": "🇺🇦 Українська",
    "ru": "🇷🇺 Русский",
}

# Shown before we know the user's language, so it's in all three.
LANGUAGE_PROMPT = "🌍 Choose your language / Обери мову / Выбери язык:"


def texts_for(voice: dict) -> dict:
    return TEXTS[voice["lang"]]
