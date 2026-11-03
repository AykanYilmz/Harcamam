import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { THEME_STORAGE_KEY } from './ThemeContext.ts'
import { ThemeProvider } from './ThemeProvider.tsx'
import { ThemeSwitcher } from './ThemeSwitcher.tsx'

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
const themeSwitch = () => screen.getByRole('switch', { name: 'Koyu tema' })

describe('ThemeProvider', () => {
  beforeEach(() => {
    localStorage.clear()
    document.documentElement.classList.remove('dark')
  })

  afterEach(() => vi.unstubAllGlobals())

  it('starts from the system theme on a first visit', () => {
    mockSystemTheme(true)
    renderSwitcher()

    expect(isDark()).toBe(true)
    expect(themeSwitch()).toBeChecked()
  })

  it('toggles and remembers the choice', async () => {
    mockSystemTheme(true)
    renderSwitcher()

    await userEvent.click(themeSwitch())

    expect(isDark()).toBe(false)
    expect(themeSwitch()).not.toBeChecked()
    expect(localStorage.getItem(THEME_STORAGE_KEY)).toBe('light')
  })

  it('restores the saved choice over the system theme', () => {
    mockSystemTheme(false)
    localStorage.setItem(THEME_STORAGE_KEY, 'dark')
    renderSwitcher()

    expect(isDark()).toBe(true)
    expect(themeSwitch()).toBeChecked()
  })
})
