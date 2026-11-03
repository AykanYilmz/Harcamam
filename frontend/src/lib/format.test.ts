import { describe, expect, it } from 'vitest'
import {
  formatCurrency,
  formatCurrencyCompact,
  formatDate,
  formatMonth,
  formatMonthShort,
  formatPercent,
  shiftMonth,
} from './format.ts'

describe('format', () => {
  it.each([
    ['1129.00', '₺1.129,00'],
    ['0.00', '₺0,00'],
    ['-1500.00', '-₺1.500,00'],
    [45092.1, '₺45.092,10'],
  ])('formats %s as currency', (amount, expected) => {
    expect(formatCurrency(amount)).toBe(expected)
  })

  it('formats compact currency for axes', () => {
    // Intl separates the number and "B" (bin) with a no-break space.
    expect(formatCurrencyCompact('45092.10')).toBe('₺45,1 B')
  })

  it('formats percentages the Turkish way', () => {
    expect(formatPercent(26.1)).toBe('%26,1')
    expect(formatPercent(-100)).toBe('-%100')
  })

  it('formats months', () => {
    expect(formatMonth('2026-10')).toBe('Ekim 2026')
    expect(formatMonthShort('2026-01')).toBe('Oca')
  })

  it.each([
    ['2026-10', 1, '2026-11'],
    ['2026-12', 1, '2027-01'],
    ['2026-01', -1, '2025-12'],
  ])('shifts %s by %i month', (month, steps, expected) => {
    expect(shiftMonth(month, steps)).toBe(expected)
  })

  it('formats dates without timezone shifts', () => {
    expect(formatDate('2026-10-01')).toBe('1 Eki 2026')
    expect(formatDate('2026-10-31T23:30:00Z')).toBe('31 Eki 2026')
  })
})
