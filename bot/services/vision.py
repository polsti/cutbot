import json
import time

from google import genai
from google.genai.errors import ServerError
from google.genai import types

from bot.config import settings

MODEL = "gemini-3.5-flash"

PROMPT_TEMPLATE = """Ты — эксперт по оценке калорийности блюд по фото.

Проанализируй фото еды и оцени:
- название блюда
- общую калорийность всей порции на фото (ккал)
- белки (г)
- жиры (г)
- углеводы (г)
- заметку о том, какие детали неизвестны и могли повлиять на точность оценки

{description_block}

Ответь СТРОГО в формате JSON с полями: dish_name (строка), calories (число),
protein_g (число), fat_g (число), carbs_g (число), note (строка,
коротко — что именно не хватало для точного расчёта, например способ готовки,
точный вес, вид мяса).

dish_name и note пиши на языке: {language}."""

WITH_DESCRIPTION = 'Пользователь написал про блюдо: "{description}". Используй эту информацию для точности.'
WITHOUT_DESCRIPTION = (
    "Пользователь не указал деталей (способ готовки, точный вес, состав) — "
    "оценивай по виду, но обязательно отметь в note, что это снижает точность."
)


def analyze_meal_photo(image_bytes: bytes, mime_type: str, description: str | None, language: str = "русский") -> dict:
    description_block = WITH_DESCRIPTION.format(description=description) if description else WITHOUT_DESCRIPTION
    prompt = PROMPT_TEMPLATE.format(description_block=description_block, language=language)

    client = genai.Client(
        api_key=settings.gemini_api_key,
        http_options=types.HttpOptions(timeout=30_000),  # ms; free tier can otherwise hang indefinitely under load
    )

    last_error = None
    for attempt in range(5):
        try:
            response = client.models.generate_content(
                model=MODEL,
                contents=[
                    types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
                    prompt,
                ],
                config=types.GenerateContentConfig(response_mime_type="application/json"),
            )
            break
        except (ServerError, TimeoutError) as e:
            last_error = e
            time.sleep(5 * (attempt + 1))  # free tier gets transient 503s / slow responses under load
    else:
        raise last_error

    result = json.loads(response.text)
    return {
        "dish_name": result["dish_name"],
        "calories": round(float(result["calories"])),
        "protein_g": round(float(result["protein_g"])),
        "fat_g": round(float(result["fat_g"])),
        "carbs_g": round(float(result["carbs_g"])),
        "note": result.get("note", ""),
    }
