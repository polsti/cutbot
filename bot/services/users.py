from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.models.user import User


async def get_or_create_user(session: AsyncSession, telegram_id: int, language: str = "ru") -> User:
    result = await session.execute(select(User).where(User.telegram_id == telegram_id))
    user = result.scalar_one_or_none()
    if user is None:
        user = User(telegram_id=telegram_id, language=language)
        session.add(user)
        await session.commit()
        await session.refresh(user)
    return user


async def mark_active(session: AsyncSession, user_id: int) -> None:
    user = await session.get(User, user_id)
    user.status = "active"
    await session.commit()
