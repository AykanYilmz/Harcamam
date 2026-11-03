import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { MOTION_STORAGE_KEY, THEME_STORAGE_KEY } from './ThemeContext.ts'
import { ThemeProvider } from './ThemeProvider.tsx'
import { ThemeSwitcher } from './ThemeSwitcher.tsx'
import { useTheme } from './useTheme.ts'

function mockSystemTheme(dark: boolean) {
  vi.stubGlobal(
    'matchMedia',
    vi.fn((query: string) => ({
      matches: dark && query === '(prefers-color-scheme: dark)',
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
    })),
  )
}

function renderSwitcher() {
  render(
    <ThemeProvider>
      <ThemeSwitcher />
    </ThemeProvider>,
  )
}

const isDark = () => document.documentElement.classList.contains('dark')

describe('ThemeProvider', () => {
  beforeEach(() => {
    localStorage.clear()
    document.documentElement.classList.remove('dark')
  })

  afterEach(() => vi.unstubAllGlobals())

  it('follows the system theme by default', () => {
    mockSystemTheme(true)
    renderSwitcher()

    expect(isDark()).toBe(true)
    expect(screen.getByRole('radio', { name: 'Sistem teması' })).toBeChecked()
  })

  it('applies and remembers an explicit choice', async () => {
    mockSystemTheme(true)
    renderSwitcher()

    await userEvent.click(screen.getByRole('radio', { name: 'Açık tema' }))

    expect(isDark()).toBe(false)
    expect(localStorage.getItem(THEME_STORAGE_KEY)).toBe('light')
  })

  it('restores the saved choice', () => {
    mockSystemTheme(false)
    localStorage.setItem(THEME_STORAGE_KEY, 'dark')
    renderSwitcher()

    expect(isDark()).toBe(true)
    expect(screen.getByRole('radio', { name: 'Koyu tema' })).toBeChecked()
  })

  it('forgets the saved choice when switching back to system', async () => {
    mockSystemTheme(false)
    localStorage.setItem(THEME_STORAGE_KEY, 'dark')
    renderSwitcher()

    await userEvent.click(screen.getByRole('radio', { name: 'Sistem teması' }))

    expect(isDark()).toBe(false)
    expect(localStorage.getItem(THEME_STORAGE_KEY)).toBeNull()
  })
})

describe('ThemeProvider motion', () => {
  function mockReducedMotion(reduce: boolean) {
    vi.stubGlobal(
      'matchMedia',
      vi.fn((query: string) => ({
        matches: reduce && query === '(prefers-reduced-motion: reduce)',
        addEventListener: vi.fn(),
        removeEventListener: vi.fn(),
      })),
    )
  }

  function MotionChoice({ value }: { value: 'on' | 'off' | 'system' }) {
    const { setMotion } = useTheme()
    return <button onClick={() => setMotion(value)}>{value}</button>
  }

  function renderMotion() {
    render(
      <ThemeProvider>
        <MotionChoice value="on" />
        <MotionChoice value="off" />
        <MotionChoice value="system" />
      </ThemeProvider>,
    )
  }

  const reduced = () => document.documentElement.dataset.motion === 'reduce'

  beforeEach(() => {
    localStorage.clear()
    delete document.documentElement.dataset.motion
  })
  afterEach(() => vi.unstubAllGlobals())

  it('follows the OS by default', () => {
    mockReducedMotion(true)
    renderMotion()

    expect(reduced()).toBe(true)
  })

  it('can turn animations on even when the OS reduces motion', async () => {
    mockReducedMotion(true)
    renderMotion()

    await userEvent.click(screen.getByRole('button', { name: 'on' }))

    expect(reduced()).toBe(false)
    expect(localStorage.getItem(MOTION_STORAGE_KEY)).toBe('on')
  })

  it('can turn animations off', async () => {
    mockReducedMotion(false)
    renderMotion()

    await userEvent.click(screen.getByRole('button', { name: 'off' }))

    expect(reduced()).toBe(true)
  })
})
