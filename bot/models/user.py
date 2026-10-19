from datetime import date, datetime, timezone

from sqlalchemy import BigInteger, Date, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from bot.models.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    language: Mapped[str] = mapped_column(String(5), default="ru")
    timezone: Mapped[str] = mapped_column(String(50), default="UTC")
    status: Mapped[str] = mapped_column(String(20), default="onboarding")
    voice: Mapped[str] = mapped_column(String(20), default="smaev")

    # Morning weigh-in reminders (phase 10)
    weigh_reminder: Mapped[str] = mapped_column(String(10), default="none")  # none / daily / every3 / weekly
    weigh_weekday: Mapped[int | None] = mapped_column(Integer, nullable=True)  # 0=Mon, only for weekly
    weigh_since: Mapped[date | None] = mapped_column(Date, nullable=True)  # anchor for "every 3 days"
    last_weigh_reminder: Mapped[date | None] = mapped_column(Date, nullable=True)  # local date of last send
    utc_offset_min: Mapped[int | None] = mapped_column(Integer, nullable=True)  # local time = UTC + offset
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
