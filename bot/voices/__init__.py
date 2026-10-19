"""Switchable bot personas. Each voice is a dict of the same keys — the
"personality" slots used across onboarding, meal logging, and summaries.
Short functional prompts (e.g. "Рост, в см?") live in bot/texts/ per
language; only the flavor/personality text lives here.

Each voice belongs to one language ("lang" key), and the voice decides
which language the whole bot speaks.

To add a new voice: copy one of the voice files, fill in every key, and
register it in VOICES below. Nothing else needs to change — if its
language now has 2+ voices, the theme picker appears automatically.
"""

from bot.voices import coach, kozak, meme, smaev

VOICES = {
    "smaev": smaev.VOICE,
    "coach": coach.VOICE,
    "meme": meme.VOICE,
    "kozak": kozak.VOICE,
}
DEFAULT_VOICE = "smaev"


def get_voice(name: str) -> dict:
    return VOICES.get(name, VOICES[DEFAULT_VOICE])


def voices_for(lang: str) -> list[str]:
    return [key for key, voice in VOICES.items() if voice["lang"] == lang]
