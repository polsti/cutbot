from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.models.profile import Profile
from bot.models.weight_entry import WeightEntry


async def add_weight_entry(session: AsyncSession, user_id: int, weight_kg: float) -> WeightEntry:
    """Save a weigh-in and keep profile.weight_kg = latest weight."""
    entry = WeightEntry(user_id=user_id, weight_kg=weight_kg)
    session.add(entry)
    profile = (await session.execute(select(Profile).where(Profile.user_id == user_id))).scalar_one_or_none()
    if profile is not None:
        profile.weight_kg = weight_kg
    await session.commit()
    await session.refresh(entry)
    return entry


async def get_weight_entries(session: AsyncSession, user_id: int) -> list[WeightEntry]:
    """All weigh-ins, oldest first."""
    result = await session.execute(
        select(WeightEntry).where(WeightEntry.user_id == user_id).order_by(WeightEntry.recorded_at)
    )
    return list(result.scalars())


async def ensure_start_entry(session: AsyncSession, user_id: int) -> None:
    """Users who onboarded before weight logging existed have no entries yet —
    use their onboarding weight as the starting point so progress shows right away."""
    has_entry = (await session.execute(select(WeightEntry.id).where(WeightEntry.user_id == user_id).limit(1))).first()
    if has_entry:
        return
    profile = (await session.execute(select(Profile).where(Profile.user_id == user_id))).scalar_one_or_none()
    if profile is not None:
        session.add(WeightEntry(user_id=user_id, weight_kg=profile.weight_kg, recorded_at=profile.updated_at))
        await session.commit()
