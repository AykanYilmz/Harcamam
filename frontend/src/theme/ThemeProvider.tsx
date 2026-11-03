import { useEffect, useMemo, useState, useSyncExternalStore, type ReactNode } from 'react'
import {
  MOTION_STORAGE_KEY,
  THEME_STORAGE_KEY,
  ThemeContext,
  type MotionPreference,
  type ResolvedTheme,
  type ThemeContextValue,
  type ThemePreference,
} from './ThemeContext.ts'

const DARK_QUERY = '(prefers-color-scheme: dark)'
const REDUCED_MOTION_QUERY = '(prefers-reduced-motion: reduce)'

function readStored<T extends string>(key: string, allowed: T[], fallback: T): T {
  try {
    const stored = window.localStorage.getItem(key) as T | null
    return stored && allowed.includes(stored) ? stored : fallback
  } catch {
    return fallback
  }
}

/** Remember a choice; the default ("system") is stored as nothing at all. */
function store(key: string, value: string) {
  try {
    if (value === 'system') window.localStorage.removeItem(key)
    else window.localStorage.setItem(key, value)
  } catch {
    // Not persisted (e.g. storage blocked); the choice still applies to this visit.
  }
}

/** Live value of a media query; re-renders when the OS setting changes. */
function useMediaQuery(query: string): boolean {
  return useSyncExternalStore(
    (onChange) => {
      const media = window.matchMedia?.(query)
      media?.addEventListener('change', onChange)
      return () => media?.removeEventListener('change', onChange)
    },
    () => window.matchMedia?.(query).matches ?? false,
  )
}

export function ThemeProvider({ children }: { children: ReactNode }) {
  const [preference, setPreferenceState] = useState(() =>
    readStored<ThemePreference>(THEME_STORAGE_KEY, ['light', 'dark'], 'system'),
  )
  const [motion, setMotionState] = useState(() =>
    readStored<MotionPreference>(MOTION_STORAGE_KEY, ['on', 'off'], 'system'),
  )
  const systemDark = useMediaQuery(DARK_QUERY)
  const systemReducedMotion = useMediaQuery(REDUCED_MOTION_QUERY)

  const resolved: ResolvedTheme =
    preference === 'system' ? (systemDark ? 'dark' : 'light') : preference
  const reducedMotion = motion === 'off' || (motion === 'system' && systemReducedMotion)

  useEffect(() => {
    document.documentElement.classList.toggle('dark', resolved === 'dark')
  }, [resolved])

  useEffect(() => {
    // index.css switches every animation and transition off under this attribute.
    if (reducedMotion) document.documentElement.dataset.motion = 'reduce'
    else delete document.documentElement.dataset.motion
  }, [reducedMotion])

  const value = useMemo<ThemeContextValue>(
    () => ({
      preference,
      resolved,
      setPreference(next) {
        setPreferenceState(next)
        store(THEME_STORAGE_KEY, next)
      },
      motion,
      reducedMotion,
      setMotion(next) {
        setMotionState(next)
        store(MOTION_STORAGE_KEY, next)
      },
    }),
    [preference, resolved, motion, reducedMotion],
  )

  return <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>
}
