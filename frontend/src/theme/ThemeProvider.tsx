import { useEffect, useMemo, useState, type ReactNode } from 'react'
import {
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

  useEffect(() => {
    const root = document.documentElement
    root.classList.toggle('dark', theme === 'dark')
    // Paper is white and browsers don't print backgrounds: print in the light theme, or the
    // dark theme's light text would be nearly invisible.
    const printLight = () => root.classList.remove('dark')
    const restore = () => root.classList.toggle('dark', theme === 'dark')
    window.addEventListener('beforeprint', printLight)
    window.addEventListener('afterprint', restore)
    return () => {
      window.removeEventListener('beforeprint', printLight)
      window.removeEventListener('afterprint', restore)
    }
  }, [theme])

  const value = useMemo<ThemeContextValue>(
    () => ({
      theme,
      setTheme(next) {
        setThemeState(next)
        store(THEME_STORAGE_KEY, next)
      },
    }),
    [theme],
  )

  return <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>
}
