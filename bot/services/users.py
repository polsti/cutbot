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


async def set_voice(session: AsyncSession, user_id: int, voice: str) -> None:
    user = await session.get(User, user_id)
    user.voice = voice
    await session.commit()


async def set_language(session: AsyncSession, user_id: int, language: str) -> None:
    user = await session.get(User, user_id)
    user.language = language
    await session.commit()


async def update_user(session: AsyncSession, user_id: int, **fields) -> None:
    user = await session.get(User, user_id)
    for key, value in fields.items():
        setattr(user, key, value)
    await session.commit()


async def get_reminder_users(session: AsyncSession) -> list[User]:
    result = await session.execute(select(User).where(User.weigh_reminder != "none"))
    return list(result.scalars())
