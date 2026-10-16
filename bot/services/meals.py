from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.models.meal_entry import MealEntry


async def save_meal_entry(session: AsyncSession, user_id: int, **fields) -> MealEntry:
    entry = MealEntry(user_id=user_id, **fields)
    session.add(entry)
    await session.commit()
    await session.refresh(entry)
    return entry


async def get_today_entries(session: AsyncSession, user_id: int) -> list[MealEntry]:
    start_of_day = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    result = await session.execute(
        select(MealEntry)
        .where(MealEntry.user_id == user_id, MealEntry.logged_at >= start_of_day)
        .order_by(MealEntry.logged_at)
    )
    return list(result.scalars().all())


async def get_today_totals(session: AsyncSession, user_id: int) -> dict:
    entries = await get_today_entries(session, user_id)
    return {
        "count": len(entries),
        "calories": sum(e.calories for e in entries),
        "protein_g": sum(e.protein_g for e in entries),
        "fat_g": sum(e.fat_g for e in entries),
        "carbs_g": sum(e.carbs_g for e in entries),
    }


async def get_week_totals(session: AsyncSession, user_id: int) -> list[dict]:
    """Per-day totals for the last 7 days (today + 6 previous), oldest first.
    Days with no entries are included with zero totals, so gaps are visible."""
    today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = today - timedelta(days=6)

    result = await session.execute(
        select(MealEntry).where(MealEntry.user_id == user_id, MealEntry.logged_at >= week_start)
    )
    entries = result.scalars().all()

    days = []
    for i in range(7):
        day = week_start + timedelta(days=i)
        day_entries = [e for e in entries if day <= e.logged_at < day + timedelta(days=1)]
        days.append({
            "date": day.date(),
            "count": len(day_entries),
            "calories": sum(e.calories for e in day_entries),
            "protein_g": sum(e.protein_g for e in day_entries),
            "fat_g": sum(e.fat_g for e in day_entries),
            "carbs_g": sum(e.carbs_g for e in day_entries),
        })
    return days
