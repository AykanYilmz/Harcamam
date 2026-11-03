import { describe, expect, it } from 'vitest'
import { periodMonthOf, periodRange } from './periods.ts'

const ymd = (date: Date) =>
  `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`

describe('periodMonthOf', () => {
  it('uses calendar months without a closing day', () => {
    expect(periodMonthOf(new Date(2026, 9, 31), null)).toBe('2026-10')
  })

  it('moves days after the closing day to the next month', () => {
    expect(periodMonthOf(new Date(2026, 9, 6), 6)).toBe('2026-10')
    expect(periodMonthOf(new Date(2026, 9, 7), 6)).toBe('2026-11')
    expect(periodMonthOf(new Date(2026, 11, 31), 6)).toBe('2027-01')
  })
})

describe('periodRange', () => {
  it('runs from the day after the previous closing day to this one', () => {
    const { start, end } = periodRange('2026-10', 6)
    expect([ymd(start), ymd(end)]).toEqual(['2026-09-07', '2026-10-06'])
  })

  it('crosses the year for January', () => {
    const { start, end } = periodRange('2026-01', 6)
    expect([ymd(start), ymd(end)]).toEqual(['2025-12-07', '2026-01-06'])
  })

  it('ends a short month on its last day', () => {
    const { start, end } = periodRange('2026-02', 30)
    expect([ymd(start), ymd(end)]).toEqual(['2026-01-31', '2026-02-28'])
    expect(ymd(periodRange('2026-03', 30).start)).toBe('2026-03-01')
  })

  it('is the calendar month without a closing day', () => {
    const { start, end } = periodRange('2026-02', null)
    expect([ymd(start), ymd(end)]).toEqual(['2026-02-01', '2026-02-28'])
  })
})

describe('periodMonthOf on the closing day itself', () => {
  it('keeps the whole day, whatever the time', () => {
    expect(periodMonthOf(new Date(2026, 9, 6, 23, 59), 6)).toBe('2026-10')
  })
})
