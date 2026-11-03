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

/** "2026-10-05" -> "5 Eki 2026". Parsed as a local date, so no timezone shifts a day. */
export function formatDate(isoDate: string): string {
  const [year, month, day] = isoDate.slice(0, 10).split('-').map(Number)
  return shortDate.format(new Date(year, month - 1, day))
}
