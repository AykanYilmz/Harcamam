import { createContext } from 'react'

export type Theme = 'light' | 'dark'

export interface ThemeContextValue {
  theme: Theme
  setTheme(theme: Theme): void
  /** Page transitions, count-up numbers, the sliding menu… On unless turned off in Settings. */
  animations: boolean
  setAnimations(on: boolean): void
}

export const ThemeContext = createContext<ThemeContextValue | null>(null)

// Also read by the inline script in index.html, which applies both before first paint.
export const THEME_STORAGE_KEY = 'harcamam.theme'
export const MOTION_STORAGE_KEY = 'harcamam.motion'
