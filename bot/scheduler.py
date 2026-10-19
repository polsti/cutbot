"""Background job: every few minutes, send the morning weigh-in reminder to
everyone for whom it's 08:00–12:00 local time on a weigh day and who hasn't
had it yet today."""

import logging
from datetime import datetime, timezone

from aiogram import Bot
from aiogram.exceptions import TelegramForbiddenError
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from bot.models.base import async_session
from bot.services.reminders import local_now, should_send
from bot.services.users import get_reminder_users
from bot.texts import texts_for
from bot.voices import get_voice

CHECK_EVERY_MINUTES = 5

log = logging.getLogger(__name__)


async def send_due_reminders(bot: Bot) -> None:
    now_utc = datetime.now(timezone.utc)
    async with async_session() as session:
        for user in await get_reminder_users(session):
            if not should_send(
                user.weigh_reminder, user.weigh_weekday, user.weigh_since,
                user.last_weigh_reminder, user.utc_offset_min, now_utc,
            ):
                continue

            t = texts_for(get_voice(user.voice))
            kb = InlineKeyboardMarkup(
                inline_keyboard=[[InlineKeyboardButton(text=t["reminder_btn"], callback_data="weigh")]]
            )
            try:
                await bot.send_message(user.telegram_id, t["reminder_msg"], reply_markup=kb)
            except TelegramForbiddenError:
                user.weigh_reminder = "none"  # user blocked the bot — stop trying
                continue
            except Exception:
                log.exception("weigh reminder failed for user %s", user.id)
                continue
            user.last_weigh_reminder = local_now(now_utc, user.utc_offset_min).date()
        await session.commit()


def start_scheduler(bot: Bot) -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler(timezone="UTC")
    scheduler.add_job(
        send_due_reminders, "interval", minutes=CHECK_EVERY_MINUTES, args=[bot],
        next_run_time=datetime.now(timezone.utc),
    )
    scheduler.start()
    return scheduler
