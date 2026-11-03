// Mirrors backend app/services/periods.py. A month ends on the user's statement closing day
// (or on its last day if it is shorter) and is named after the month it ends in: with a
// closing day of 6, "2026-10" runs from 7 September to 6 October. No closing day means
// calendar months.

const CALENDAR_MONTH_END = 31

function closingDate(year: number, monthIndex: number, endDay: number): Date {
  const lastDay = new Date(year, monthIndex + 1, 0).getDate()
  return new Date(year, monthIndex, Math.min(endDay, lastDay))
}

function monthKey(date: Date): string {
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`
}

/** The month ("2026-10") whose period `date` falls in. */
export function periodMonthOf(date: Date, endDay: number | null): string {
  const closing = closingDate(date.getFullYear(), date.getMonth(), endDay ?? CALENDAR_MONTH_END)
  // Compared by day, not by time: `new Date()` on the closing day is later than its midnight.
  return date.getDate() <= closing.getDate()
    ? monthKey(date)
    : monthKey(new Date(date.getFullYear(), date.getMonth() + 1, 1))
}

/** First and last day of `month`'s period. */
export function periodRange(month: string, endDay: number | null): { start: Date; end: Date } {
  const [year, monthNumber] = month.split('-').map(Number)
  const day = endDay ?? CALENDAR_MONTH_END
  const previousClosing = closingDate(year, monthNumber - 2, day)
  const start = new Date(previousClosing)
  start.setDate(start.getDate() + 1)
  return { start, end: closingDate(year, monthNumber - 1, day) }
}
