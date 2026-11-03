import { createContext } from 'react'

export type ThemePreference = 'light' | 'dark' | 'system'
export type ResolvedTheme = 'light' | 'dark'

export interface ThemeContextValue {
  preference: ThemePreference
  /** What is actually shown: `system` resolved through the OS setting. */
  resolved: ResolvedTheme
  setPreference(preference: ThemePreference): void
}

export const ThemeContext = createContext<ThemeContextValue | null>(null)

// Also read by the inline script in index.html, which applies the theme before first paint.
export const THEME_STORAGE_KEY = 'harcamam.theme'
