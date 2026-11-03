import { describe, expect, it } from 'vitest'
import { heatLevel, monthGrid } from './calendar.ts'

describe('monthGrid', () => {
  it('starts weeks on Monday', () => {
    // 1 October 2026 is a Thursday.
    const weeks = monthGrid('2026-10')

    expect(weeks[0]).toEqual([
      null,
      null,
      null,
      '2026-10-01',
      '2026-10-02',
      '2026-10-03',
      '2026-10-04',
    ])
    expect(weeks.at(-1)).toEqual([
      '2026-10-26',
      '2026-10-27',
      '2026-10-28',
      '2026-10-29',
      '2026-10-30',
      '2026-10-31',
      null,
    ])
    expect(weeks).toHaveLength(5)
  })

  it('handles a month starting on Monday', () => {
    // 1 June 2026 is a Monday.
    expect(monthGrid('2026-06')[0][0]).toBe('2026-06-01')
  })

  it('handles a month starting on Sunday', () => {
    // 1 February 2026 is a Sunday: six empty cells first.
    const weeks = monthGrid('2026-02')

    expect(weeks[0].slice(0, 6)).toEqual(Array(6).fill(null))
    expect(weeks[0][6]).toBe('2026-02-01')
    expect(weeks.flat().filter(Boolean)).toHaveLength(28)
  })

  it('handles leap years', () => {
    expect(monthGrid('2028-02').flat().filter(Boolean)).toHaveLength(29)
  })
})

describe('heatLevel', () => {
  it.each([
    [0, 1000, 0],
    [-50, 1000, 0],
    [100, 1000, 1],
    [300, 1000, 2],
    [600, 1000, 3],
    [1000, 1000, 4],
    [100, 0, 0],
  ])('%d of %d is level %d', (value, max, expected) => {
    expect(heatLevel(value, max)).toBe(expected)
  })
})
