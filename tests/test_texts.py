"""Every language and every voice must have the same keys and the same
{placeholders} — otherwise the bot crashes only when a user of that
language hits that exact message."""

import os
from string import Formatter

os.environ.setdefault("BOT_TOKEN", "dummy")
os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://user:pass@localhost:5432/dbname")
os.environ.setdefault("GEMINI_API_KEY", "dummy")

import pytest  # noqa: E402

from bot.texts import LANGUAGE_LABELS, TEXTS  # noqa: E402
from bot.voices import VOICES, voices_for  # noqa: E402


def _placeholders(value) -> set:
    if isinstance(value, str):
        return {name for _, name, _, _ in Formatter().parse(value) if name}
    if isinstance(value, dict):
        return {(k, p) for k, v in value.items() for p in _placeholders(v)} | {("key", k) for k in value}
    return set()


@pytest.mark.parametrize("lang", list(TEXTS))
def test_language_matches_russian(lang):
    ru, other = TEXTS["ru"], TEXTS[lang]
    assert other.keys() == ru.keys()
    for key in ru:
        assert _placeholders(other[key]) == _placeholders(ru[key]), key
    assert len(other["day_names"]) == 7
    assert len(other["weekday_names"]) == 7


@pytest.mark.parametrize("name", list(VOICES))
def test_voice_matches_smaev(name):
    smaev, voice = VOICES["smaev"], VOICES[name]
    assert voice.keys() == smaev.keys()
    for key in smaev:
        # A voice may skip a placeholder (e.g. no {quote}), but must not invent one.
        assert _placeholders(voice[key]) <= _placeholders(smaev[key]), key
    assert voice["lang"] in TEXTS
    assert voice["quotes"] and voice["help_quote_pool"]


@pytest.mark.parametrize("lang", list(LANGUAGE_LABELS))
def test_every_language_has_a_voice(lang):
    assert lang in TEXTS
    assert voices_for(lang)


def test_handlers_import():
    # Catches typos / circular imports between onboarding and settings.
    import bot.main  # noqa: F401
