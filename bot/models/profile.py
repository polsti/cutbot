from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from bot.models.base import Base


class Profile(Base):
    __tablename__ = "profiles"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True)

    gender: Mapped[str] = mapped_column(String(1))  # 'm' or 'f'
    age: Mapped[int] = mapped_column(Integer)
    height_cm: Mapped[float] = mapped_column(Float)
    weight_kg: Mapped[float] = mapped_column(Float)
    job_type: Mapped[str] = mapped_column(String(10))  # office / physical
    strength_freq: Mapped[str] = mapped_column(String(5))  # 0 / 1-2 / 3-4 / 5+
    cardio_freq: Mapped[str] = mapped_column(String(5))  # 0 / 1-2 / 3-4 / 5+
    steps_bucket: Mapped[str] = mapped_column(String(15))  # <5000 / 5000-10000 / 10000-15000 / 15000+
    activity_coefficient: Mapped[float] = mapped_column(Float)
    goal: Mapped[str] = mapped_column(String(10))  # maintain / lose / gain
    pace: Mapped[str | None] = mapped_column(String(10), nullable=True)

    target_calories: Mapped[int] = mapped_column(Integer)
    protein_g: Mapped[int] = mapped_column(Integer)
    fat_g: Mapped[int] = mapped_column(Integer)
    carbs_g: Mapped[int] = mapped_column(Integer)
    water_ml: Mapped[int] = mapped_column(Integer)

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
