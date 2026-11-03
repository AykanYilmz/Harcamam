// Turkish formatting with the browser's Intl API. Amounts arrive from the API as decimal
// strings ("1129.00"); they are converted to numbers only here, for display.

const currency = new Intl.NumberFormat('tr-TR', { style: 'currency', currency: 'TRY' })
const compactCurrency = new Intl.NumberFormat('tr-TR', {
  style: 'currency',
  currency: 'TRY',
  notation: 'compact',
  maximumFractionDigits: 1,
})
const percent = new Intl.NumberFormat('tr-TR', { style: 'percent', maximumFractionDigits: 1 })
const longMonth = new Intl.DateTimeFormat('tr-TR', { month: 'long', year: 'numeric' })
const shortMonth = new Intl.DateTimeFormat('tr-TR', { month: 'short' })
const shortDate = new Intl.DateTimeFormat('tr-TR', {
  day: 'numeric',
  month: 'short',
  year: 'numeric',
})
const dayMonth = new Intl.DateTimeFormat('tr-TR', { day: 'numeric', month: 'short' })

/** "1129.00" -> "₺1.129,00" */
export function formatCurrency(amount: string | number): string {
  return currency.format(Number(amount))
}

/** 45092.1 -> "₺45,1 B" (for chart axes) */
export function formatCurrencyCompact(amount: string | number): string {
  return compactCurrency.format(Number(amount))
}

/** 26.1 (already a percentage) -> "%26,1" */
export function formatPercent(value: number): string {
  return percent.format(value / 100)
}

/** "2026-10" -> date at the first of that month, in local time. */
export function parseMonth(month: string): Date {
  const [year, monthIndex] = month.split('-').map(Number)
  return new Date(year, monthIndex - 1, 1)
}

/** "2026-10" -> "2026-11" (or a negative step for earlier months) */
export function shiftMonth(month: string, steps: number): string {
  const date = parseMonth(month)
  date.setMonth(date.getMonth() + steps)
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`
}

/** "2026-10" -> "Ekim 2026" */
export function formatMonth(month: string): string {
  return longMonth.format(parseMonth(month))
}

/** "2026-10" -> "Eki" */
export function formatMonthShort(month: string): string {
  return shortMonth.format(parseMonth(month))
}

function localDate(isoDate: string): Date {
  const [year, month, day] = isoDate.slice(0, 10).split('-').map(Number)
  return new Date(year, month - 1, day)
}

/** "2026-10-05" -> "5 Eki 2026". Parsed as a local date, so no timezone shifts a day. */
export function formatDate(isoDate: string): string {
  return shortDate.format(localDate(isoDate))
}

/** "2026-09-07", "2026-10-06" -> "7 Eyl – 6 Eki"; years are shown only when they differ. */
export function formatDateRange(start: string | Date, end: string | Date): string {
  const [from, to] = [start, end].map((value) =>
    typeof value === 'string' ? localDate(value) : value,
  )
  const format = from.getFullYear() === to.getFullYear() ? dayMonth : shortDate
  return `${format.format(from)} – ${format.format(to)}`
}
