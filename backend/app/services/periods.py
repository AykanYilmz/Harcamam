"""Reporting periods: calendar months, or months that end on the user's statement closing day.

A period is named after the month it ends in, the way banks name statements: with a closing
day of 6, "October" runs from 7 September to 6 October. A closing day of 31 (or none) is the
calendar month. In months shorter than the closing day the period ends on the month's last day.

Periods are identified by the first day of the month they are named after, `date(2026, 10, 1)`.
"""

import calendar
import datetime as dt
from dataclasses import dataclass

CALENDAR_MONTH_END = 31


def add_months(month: dt.date, count: int) -> dt.date:
    index = month.year * 12 + month.month - 1 + count
    return dt.date(index // 12, index % 12 + 1, 1)


def _closing_date(month: dt.date, end_day: int) -> dt.date:
    """The day `month`'s period ends on: `end_day`, or the month's last day if it is shorter."""
    last_day = calendar.monthrange(month.year, month.month)[1]
    return month.replace(day=min(end_day, last_day))


@dataclass(frozen=True)
class Period:
    month: dt.date
    start: dt.date
    # Inclusive, as people say it: "7 Eylül - 6 Ekim".
    end: dt.date

    @property
    def end_exclusive(self) -> dt.date:
        return self.end + dt.timedelta(days=1)

    def days(self) -> list[dt.date]:
        count = (self.end - self.start).days + 1
        return [self.start + dt.timedelta(days=offset) for offset in range(count)]


class PeriodCalendar:
    """Maps dates to periods for one closing day."""

    def __init__(self, end_day: int | None) -> None:
        self.end_day = end_day or CALENDAR_MONTH_END

    def period(self, month: dt.date) -> Period:
        month = month.replace(day=1)
        start = _closing_date(add_months(month, -1), self.end_day) + dt.timedelta(days=1)
        return Period(month=month, start=start, end=_closing_date(month, self.end_day))

    def month_of(self, day: dt.date) -> dt.date:
        """The period `day` falls in, as its month."""
        month = day.replace(day=1)
        return month if day <= _closing_date(month, self.end_day) else add_months(month, 1)

    def periods(self, first: dt.date, last: dt.date) -> list[Period]:
        """Every period from month `first` to month `last`, inclusive."""
        result = []
        month = first.replace(day=1)
        while month <= last:
            result.append(self.period(month))
            month = add_months(month, 1)
        return result
