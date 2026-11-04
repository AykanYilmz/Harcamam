import { describe, expect, it } from 'vitest'
import { parseAmountInput } from './amount.ts'

describe('parseAmountInput', () => {
  it.each([
    ['8000', '8000'],
    ['8.000', '8000'],
    ['1.250.000', '1250000'],
    ['1.250,50', '1250.50'],
    ['850,5', '850.5'],
    ['12.5', '12.5'],
    [' ₺ 2.000 TL ', '2000'],
  ])('reads %s', (text, expected) => {
    expect(parseAmountInput(text)).toBe(expected)
  })

  it.each(['', '0', '0,00', '-50', 'abc', '1,2,3', '12,345', '1.23,45'])('rejects %s', (text) => {
    expect(parseAmountInput(text)).toBeNull()
  })
})
