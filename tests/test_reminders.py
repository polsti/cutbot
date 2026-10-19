from datetime import date, datetime

from bot.services.reminders import is_weigh_day, should_send, utc_offset_from_local_time

NOW = datetime(2026, 10, 19, 16, 40)  # UTC


def test_offset_spain_summer_time():
    assert utc_offset_from_local_time("18:40", NOW) == 120


def test_offset_rounds_to_15_and_accepts_dot():
    assert utc_offset_from_local_time("19.43", NOW) == 180  # Kyiv, user typed a bit late


def test_offset_across_midnight():
    # 16:40 UTC is 01:40 next day in Tokyo-ish (+9)
    assert utc_offset_from_local_time("01:40", NOW) == 540
    # and 05:40 same day in Hawaii (-11 range check)
    assert utc_offset_from_local_time("05:40", NOW) == -660


def test_offset_rejects_garbage():
    assert utc_offset_from_local_time("hello", NOW) is None
    assert utc_offset_from_local_time("25:00", NOW) is None


def test_weigh_days():
    start = date(2026, 10, 19)
    assert is_weigh_day("daily", None, None, start)
    assert is_weigh_day("every3", None, start, date(2026, 10, 22))
    assert not is_weigh_day("every3", None, start, date(2026, 10, 21))
    assert is_weigh_day("weekly", 0, None, date(2026, 10, 19))  # Monday
    assert not is_weigh_day("weekly", 0, None, date(2026, 10, 20))


def test_should_send_only_in_the_morning_once():
    morning = datetime(2026, 10, 20, 6, 5)  # 08:05 in UTC+2
    assert should_send("daily", None, None, None, 120, morning)
    assert not should_send("daily", None, None, date(2026, 10, 20), 120, morning)  # already sent
    assert not should_send("daily", None, None, None, 120, datetime(2026, 10, 20, 5, 0))  # 07:00 local
    assert not should_send("daily", None, None, None, 120, datetime(2026, 10, 20, 11, 0))  # 13:00 local
    assert not should_send("none", None, None, None, 120, morning)
    assert not should_send("daily", None, None, None, None, morning)  # no timezone yet
