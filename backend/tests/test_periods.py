from datetime import date

import pytest

from app.services.periods import Period, PeriodCalendar


@pytest.mark.parametrize("end_day", [None, 31])
def test_without_a_closing_day_periods_are_calendar_months(end_day: int | None) -> None:
    periods = PeriodCalendar(end_day)

    assert periods.period(date(2026, 2, 1)) == Period(
        date(2026, 2, 1), date(2026, 2, 1), date(2026, 2, 28)
    )
    assert periods.period(date(2026, 10, 1)) == Period(
        date(2026, 10, 1), date(2026, 10, 1), date(2026, 10, 31)
    )


def test_period_is_named_after_the_month_it_ends_in() -> None:
    assert PeriodCalendar(6).period(date(2026, 10, 1)) == Period(
        date(2026, 10, 1), date(2026, 9, 7), date(2026, 10, 6)
    )


def test_january_period_starts_in_the_previous_year() -> None:
    assert PeriodCalendar(6).period(date(2026, 1, 1)) == Period(
        date(2026, 1, 1), date(2025, 12, 7), date(2026, 1, 6)
    )


@pytest.mark.parametrize(
    ("month", "start", "end"),
    [
        # February has no 30th: its period ends on its last day...
        (date(2026, 2, 1), date(2026, 1, 31), date(2026, 2, 28)),
        # ...and March's starts the day after.
        (date(2026, 3, 1), date(2026, 3, 1), date(2026, 3, 30)),
        (date(2028, 2, 1), date(2028, 1, 31), date(2028, 2, 29)),
    ],
)
def test_closing_day_past_the_end_of_a_short_month(month: date, start: date, end: date) -> None:
    assert PeriodCalendar(30).period(month) == Period(month, start, end)


@pytest.mark.parametrize(
    ("day", "month"),
    [
        (date(2026, 10, 6), date(2026, 10, 1)),
        (date(2026, 10, 7), date(2026, 11, 1)),
        (date(2026, 9, 7), date(2026, 10, 1)),
        (date(2026, 12, 31), date(2027, 1, 1)),
    ],
)
def test_month_of_a_day(day: date, month: date) -> None:
    assert PeriodCalendar(6).month_of(day) == month


def test_periods_cover_every_day_exactly_once() -> None:
    periods = PeriodCalendar(30).periods(date(2025, 11, 1), date(2027, 3, 1))

    days = [day for period in periods for day in period.days()]
    assert days[0] == date(2025, 10, 31)
    assert days[-1] == date(2027, 3, 30)
    assert len(days) == len(set(days)) == (days[-1] - days[0]).days + 1
    assert all(PeriodCalendar(30).month_of(day) == p.month for p in periods for day in p.days())
