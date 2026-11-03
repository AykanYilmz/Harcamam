import { useEffect, useMemo, useState, type ReactNode } from 'react'
import {
  MOTION_STORAGE_KEY,
  THEME_STORAGE_KEY,
  ThemeContext,
  type Theme,
  type ThemeContextValue,
} from './ThemeContext.ts'

function readStored(key: string): string | null {
  try {
    return window.localStorage.getItem(key)
  } catch {
    return null
  }
}

function store(key: string, value: string) {
  try {
    window.localStorage.setItem(key, value)
  } catch {
    // Not persisted (e.g. storage blocked); the choice still applies to this visit.
  }
}

/** The saved theme, or on a first visit whichever one the operating system uses. */
function initialTheme(): Theme {
  const stored = readStored(THEME_STORAGE_KEY)
  if (stored === 'light' || stored === 'dark') return stored
  return window.matchMedia?.('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
}

export function ThemeProvider({ children }: { children: ReactNode }) {
  const [theme, setThemeState] = useState(initialTheme)
  const [animations, setAnimationsState] = useState(() => readStored(MOTION_STORAGE_KEY) !== 'off')

  useEffect(() => {
    document.documentElement.classList.toggle('dark', theme === 'dark')
  }, [theme])

  useEffect(() => {
    // index.css switches every animation and transition off under this attribute.
    if (animations) delete document.documentElement.dataset.motion
    else document.documentElement.dataset.motion = 'reduce'
  }, [animations])

  const value = useMemo<ThemeContextValue>(
    () => ({
      theme,
      setTheme(next) {
        setThemeState(next)
        store(THEME_STORAGE_KEY, next)
      },
      animations,
      setAnimations(on) {
        setAnimationsState(on)
        store(MOTION_STORAGE_KEY, on ? 'on' : 'off')
      },
    }),
    [theme, animations],
  )

  return <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>
}
