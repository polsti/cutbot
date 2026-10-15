from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.models.meal_entry import MealEntry


async def save_meal_entry(session: AsyncSession, user_id: int, **fields) -> MealEntry:
    entry = MealEntry(user_id=user_id, **fields)
    session.add(entry)
    await session.commit()
    await session.refresh(entry)
    return entry


async def get_today_totals(session: AsyncSession, user_id: int) -> dict:
    start_of_day = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    result = await session.execute(
        select(MealEntry).where(MealEntry.user_id == user_id, MealEntry.logged_at >= start_of_day)
    )
    entries = result.scalars().all()
    return {
        "count": len(entries),
        "calories": sum(e.calories for e in entries),
        "protein_g": sum(e.protein_g for e in entries),
        "fat_g": sum(e.fat_g for e in entries),
        "carbs_g": sum(e.carbs_g for e in entries),
    }
