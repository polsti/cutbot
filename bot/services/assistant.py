"""/assist: Gemini chat grounded in the user's own data.

build_user_context() turns profile + meals + weights into a plain-text
summary (pure function, testable). ask_assistant() sends it to Gemini as
the system instruction together with the recent chat history.
"""

import time

from google import genai
from google.genai import types
from google.genai.errors import ServerError

from bot.config import settings
from bot.services.vision import MODEL

MAX_HISTORY_MESSAGES = 12  # last 6 question/answer pairs
MAX_REPLY_CHARS = 3500  # Telegram limit is 4096

SYSTEM_TEMPLATE = """You are the nutrition assistant inside a calorie-tracking Telegram bot.
Answer in this language: {language}.
Personality: {style}

Rules:
- Base advice on the user's real data below; cite their actual numbers when relevant
  (e.g. "today you're at 62/120 g protein").
- Be practical: concrete foods, portions in grams, simple swaps. Keep answers short —
  this is a chat, aim for under 150 words unless asked for more.
- Plain text only. No markdown, no **bold**, no tables. Simple dashes for lists are fine.
- You are not a doctor. For medical conditions, medication, pregnancy, or signs of an
  eating disorder (very low intake, fear of eating, purging), be kind and suggest seeing
  a professional. Never recommend going below the user's minimum calorie target.
- Stay on topic: nutrition, training, weight, habits. Politely steer back otherwise.

USER DATA:
{context}"""


def build_user_context(profile, today_entries, week_days, weight_entries) -> str:
    if profile is None:
        return "No profile yet — the user hasn't finished onboarding (/start)."

    lines = [
        f"Profile: {'male' if profile.gender == 'm' else 'female'}, {profile.age} y, "
        f"{profile.height_cm:g} cm, {profile.weight_kg:g} kg.",
        f"Goal: {profile.goal}"
        + (f", target weight {profile.target_weight_kg:g} kg" if profile.target_weight_kg else "")
        + (f", pace {profile.pace}" if profile.pace else "") + ".",
        f"Daily norm: {profile.target_calories} kcal, protein {profile.protein_g} g, "
        f"fat {profile.fat_g} g, carbs {profile.carbs_g} g, water {profile.water_ml} ml.",
    ]

    if today_entries:
        totals = {k: sum(getattr(e, k) for e in today_entries) for k in ("calories", "protein_g", "fat_g", "carbs_g")}
        lines.append(
            f"Today so far: {totals['calories']} kcal, P {totals['protein_g']} g, "
            f"F {totals['fat_g']} g, C {totals['carbs_g']} g. Meals: "
            + "; ".join(f"{e.dish_name} ({e.calories} kcal)" for e in today_entries)
        )
    else:
        lines.append("Today: nothing logged yet.")

    week = [
        f"{d['date']:%a %d.%m}: {d['calories']} kcal P{d['protein_g']} F{d['fat_g']} C{d['carbs_g']}"
        if d["count"] else f"{d['date']:%a %d.%m}: not logged"
        for d in week_days
    ]
    lines.append("Last 7 days: " + " | ".join(week))

    if weight_entries:
        recent = weight_entries[-10:]
        lines.append("Weight history: " + ", ".join(f"{e.recorded_at:%d.%m} {e.weight_kg:g} kg" for e in recent))
    return "\n".join(lines)


def ask_assistant(history: list[dict], question: str, context: str, language: str, style: str) -> str:
    """history: [{"role": "user"|"model", "text": ...}], oldest first. Blocking — call via asyncio.to_thread."""
    client = genai.Client(api_key=settings.gemini_api_key, http_options=types.HttpOptions(timeout=30_000))
    contents = [
        types.Content(role=m["role"], parts=[types.Part.from_text(text=m["text"])])
        for m in history[-MAX_HISTORY_MESSAGES:]
    ]
    contents.append(types.Content(role="user", parts=[types.Part.from_text(text=question)]))
    config = types.GenerateContentConfig(
        system_instruction=SYSTEM_TEMPLATE.format(language=language, style=style, context=context),
    )

    last_error = None
    for attempt in range(3):
        try:
            response = client.models.generate_content(model=MODEL, contents=contents, config=config)
            return (response.text or "").strip()[:MAX_REPLY_CHARS]
        except (ServerError, TimeoutError) as e:
            last_error = e
            time.sleep(3 * (attempt + 1))
    raise last_error
