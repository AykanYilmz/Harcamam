import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { Switch } from '../components/ui/Switch.tsx'
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

describe('ThemeProvider animations', () => {
  function AnimationsSwitch() {
    const { animations, setAnimations } = useTheme()
    return <Switch checked={animations} onChange={setAnimations} label="Animasyonlar" />
  }

  function renderAnimations() {
    render(
      <ThemeProvider>
        <AnimationsSwitch />
      </ThemeProvider>,
    )
  }

  const reduced = () => document.documentElement.dataset.motion === 'reduce'
  const animationsSwitch = () => screen.getByRole('switch', { name: 'Animasyonlar' })

  beforeEach(() => {
    localStorage.clear()
    delete document.documentElement.dataset.motion
  })

  it('is on by default', () => {
    renderAnimations()

    expect(animationsSwitch()).toBeChecked()
    expect(reduced()).toBe(false)
  })

  it('can be turned off and remembers it', async () => {
    renderAnimations()

    await userEvent.click(animationsSwitch())

    expect(reduced()).toBe(true)
    expect(localStorage.getItem(MOTION_STORAGE_KEY)).toBe('off')
  })

  it('restores the saved choice', () => {
    localStorage.setItem(MOTION_STORAGE_KEY, 'off')
    renderAnimations()

    expect(animationsSwitch()).not.toBeChecked()
    expect(reduced()).toBe(true)
  })
})
