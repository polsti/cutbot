from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.models.profile import Profile


async def save_profile(session: AsyncSession, user_id: int, **fields) -> Profile:
    result = await session.execute(select(Profile).where(Profile.user_id == user_id))
    profile = result.scalar_one_or_none()

    if profile is None:
        profile = Profile(user_id=user_id, **fields)
        session.add(profile)
    else:
        for key, value in fields.items():
            setattr(profile, key, value)

    await session.commit()
    await session.refresh(profile)
    return profile
