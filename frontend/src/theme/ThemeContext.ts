import { createContext } from 'react'

export type Theme = 'light' | 'dark'

export interface ThemeContextValue {
  theme: Theme
  setTheme(theme: Theme): void
}

export const ThemeContext = createContext<ThemeContextValue | null>(null)

// Also read by the inline script in index.html, which applies it before first paint.
export const THEME_STORAGE_KEY = 'harcamam.theme'
