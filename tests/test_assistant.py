import os
from datetime import date, datetime
from types import SimpleNamespace as NS

os.environ.setdefault("BOT_TOKEN", "dummy")
os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://user:pass@localhost:5432/dbname")
os.environ.setdefault("GEMINI_API_KEY", "dummy")

from bot.services.assistant import build_user_context  # noqa: E402

PROFILE = NS(gender="f", age=24, height_cm=165.0, weight_kg=67.2, goal="lose", target_weight_kg=60.0, pace="medium",
             target_calories=1650, protein_g=130, fat_g=60, carbs_g=150, water_ml=2000)


def test_context_includes_real_numbers():
    today = [NS(dish_name="Omelette", calories=350, protein_g=22, fat_g=25, carbs_g=5)]
    week = [{"date": date(2026, 10, 19), "count": 1, "calories": 350, "protein_g": 22, "fat_g": 25, "carbs_g": 5},
            {"date": date(2026, 10, 18), "count": 0, "calories": 0, "protein_g": 0, "fat_g": 0, "carbs_g": 0}]
    weights = [NS(recorded_at=datetime(2026, 10, 1), weight_kg=70.0), NS(recorded_at=datetime(2026, 10, 19), weight_kg=67.2)]
    ctx = build_user_context(PROFILE, today, week, weights)
    assert "target weight 60 kg" in ctx
    assert "1650 kcal" in ctx and "protein 130 g" in ctx
    assert "Omelette (350 kcal)" in ctx and "P 22 g" in ctx
    assert "not logged" in ctx
    assert "19.10 67.2 kg" in ctx


def test_context_without_profile():
    assert "onboarding" in build_user_context(None, [], [], [])


def test_context_nothing_logged_today():
    assert "nothing logged yet" in build_user_context(PROFILE, [], [], [])
