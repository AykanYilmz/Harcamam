import { createContext } from 'react'

export type ThemePreference = 'light' | 'dark' | 'system'
export type ResolvedTheme = 'light' | 'dark'
/** Animations: follow the OS "reduce motion" setting, or always on / always off. */
export type MotionPreference = 'system' | 'on' | 'off'

export interface ThemeContextValue {
  preference: ThemePreference
  /** What is actually shown: `system` resolved through the OS setting. */
  resolved: ResolvedTheme
  setPreference(preference: ThemePreference): void
  motion: MotionPreference
  /** Whether animations are off right now (`motion` resolved through the OS setting). */
  reducedMotion: boolean
  setMotion(motion: MotionPreference): void
}

export const ThemeContext = createContext<ThemeContextValue | null>(null)

// Also read by the inline script in index.html, which applies both before first paint.
export const THEME_STORAGE_KEY = 'harcamam.theme'
export const MOTION_STORAGE_KEY = 'harcamam.motion'
