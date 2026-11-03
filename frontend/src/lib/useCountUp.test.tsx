import { act, render, screen } from '@testing-library/react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { AnimatedNumber } from '../components/ui/AnimatedNumber.tsx'

const format = (value: number) => value.toFixed(2)

function setReducedMotion(reduce: boolean) {
  vi.stubGlobal(
    'matchMedia',
    vi.fn(() => ({ matches: reduce, addEventListener: vi.fn(), removeEventListener: vi.fn() })),
  )
}

describe('AnimatedNumber', () => {
  beforeEach(() => vi.useFakeTimers({ toFake: ['requestAnimationFrame', 'performance'] }))
  afterEach(() => {
    vi.useRealTimers()
    vi.unstubAllGlobals()
  })

  it('counts up from zero and lands exactly on the value', () => {
    setReducedMotion(false)
    const { container } = render(<AnimatedNumber value={45092.1} format={format} />)
    const visible = () => container.querySelector('[aria-hidden]')!.textContent

    expect(visible()).toBe('0.00')
    act(() => vi.advanceTimersByTime(400))
    expect(Number(visible())).toBeGreaterThan(0)
    expect(Number(visible())).toBeLessThan(45092.1)
    act(() => vi.advanceTimersByTime(600))
    expect(visible()).toBe('45092.10')
  })

  it('gives screen readers only the final value', () => {
    setReducedMotion(false)
    render(<AnimatedNumber value={45092.1} format={format} />)

    expect(screen.getByText('45092.10')).toHaveClass('sr-only')
  })

  it('skips the animation when the user prefers reduced motion', () => {
    setReducedMotion(true)
    const { container } = render(<AnimatedNumber value={45092.1} format={format} />)

    expect(container.querySelector('[aria-hidden]')!.textContent).toBe('45092.10')
  })
})
