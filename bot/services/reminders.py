"""Pure time logic for weigh-in reminders — no Telegram, no DB, easy to test."""

from datetime import date, datetime, timedelta

REMINDER_HOUR = 8  # 08:00 local
# Send any time from 08:00 until noon if not sent yet today, so a restart or
# deploy right at 08:00 delays the reminder instead of skipping the day.
SEND_UNTIL_HOUR = 12


def utc_offset_from_local_time(local_hhmm: str, now_utc: datetime) -> int | None:
    """User says what time it is for them ("18:40") -> offset from UTC in minutes,
    rounded to 15 min. None if the input isn't a valid time."""
    try:
        hours, minutes = local_hhmm.strip().replace(".", ":").split(":")
        local_minutes = int(hours) * 60 + int(minutes)
    except ValueError:
        return None
    if not (0 <= int(hours) <= 23 and 0 <= int(minutes) <= 59):
        return None

    utc_minutes = now_utc.hour * 60 + now_utc.minute
    offset = local_minutes - utc_minutes
    # Pick the equivalent offset inside the real-world range (UTC-12 .. UTC+14).
    if offset < -12 * 60:
        offset += 24 * 60
    elif offset > 14 * 60:
        offset -= 24 * 60
    return round(offset / 15) * 15


def local_now(now_utc: datetime, offset_min: int) -> datetime:
    return now_utc + timedelta(minutes=offset_min)


def is_weigh_day(frequency: str, weekday: int | None, since: date | None, today: date) -> bool:
    if frequency == "daily":
        return True
    if frequency == "every3":
        return since is not None and (today - since).days % 3 == 0
    if frequency == "weekly":
        return weekday is not None and today.weekday() == weekday
    return False


def should_send(
    frequency: str, weekday: int | None, since: date | None,
    last_sent: date | None, offset_min: int | None, now_utc: datetime,
) -> bool:
    if frequency == "none" or offset_min is None:
        return False
    now = local_now(now_utc, offset_min)
    if not (REMINDER_HOUR <= now.hour < SEND_UNTIL_HOUR):
        return False
    if last_sent == now.date():
        return False
    return is_weigh_day(frequency, weekday, since, now.date())
