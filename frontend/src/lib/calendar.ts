import { parseMonth } from './format.ts'

/** Turkish weekday initials, Monday first (as Turkish calendars are). */
export const WEEKDAYS = ['Pzt', 'Sal', 'Çar', 'Per', 'Cum', 'Cmt', 'Paz']

function isoDate(year: number, monthIndex: number, day: number): string {
  return `${year}-${String(monthIndex + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`
}

/**
 * The weeks of a month ("2026-10") as rows of 7 cells, Monday first. Cells before the 1st
 * and after the last day are null.
 */
export function monthGrid(month: string): (string | null)[][] {
  const first = parseMonth(month)
  const year = first.getFullYear()
  const monthIndex = first.getMonth()
  const daysInMonth = new Date(year, monthIndex + 1, 0).getDate()
  // getDay(): Sunday = 0. Shift so Monday = 0.
  const leading = (first.getDay() + 6) % 7

  const cells: (string | null)[] = Array(leading).fill(null)
  for (let day = 1; day <= daysInMonth; day++) cells.push(isoDate(year, monthIndex, day))
  while (cells.length % 7 !== 0) cells.push(null)

  const weeks = []
  for (let i = 0; i < cells.length; i += 7) weeks.push(cells.slice(i, i + 7))
  return weeks
}

/** 0 (nothing) to 4 (the most), relative to the largest value it is compared with. */
export function heatLevel(value: number, max: number): 0 | 1 | 2 | 3 | 4 {
  if (value <= 0 || max <= 0) return 0
  const share = value / max
  if (share > 0.75) return 4
  if (share > 0.5) return 3
  if (share > 0.25) return 2
  return 1
}

// One hue, light to dark: the spending color mixed in at growing strength.
const HEAT_MIX = [0, 14, 30, 50, 75]

export function heatColor(level: number): string | undefined {
  if (level === 0) return undefined
  return `color-mix(in oklab, var(--chart-expense) ${HEAT_MIX[level]}%, transparent)`
}

export function todayIso(): string {
  const now = new Date()
  return isoDate(now.getFullYear(), now.getMonth(), now.getDate())
}
