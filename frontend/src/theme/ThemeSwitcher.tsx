import { Monitor, Moon, Sun, type LucideIcon } from 'lucide-react'
import type { ThemePreference } from './ThemeContext.ts'
import { useTheme } from './useTheme.ts'

const OPTIONS: { value: ThemePreference; label: string; icon: LucideIcon }[] = [
  { value: 'light', label: 'Açık tema', icon: Sun },
  { value: 'dark', label: 'Koyu tema', icon: Moon },
  { value: 'system', label: 'Sistem teması', icon: Monitor },
]

/** Three-way switch: light, dark or follow the operating system. */
export function ThemeSwitcher({ className = '' }: { className?: string }) {
  const { preference, setPreference } = useTheme()

  return (
    <div
      role="radiogroup"
      aria-label="Tema"
      className={`inline-flex rounded-lg bg-surface-muted p-1 ${className}`}
    >
      {OPTIONS.map(({ value, label, icon: Icon }) => {
        const selected = preference === value
        return (
          <button
            key={value}
            type="button"
            role="radio"
            aria-checked={selected}
            aria-label={label}
            title={label}
            onClick={() => setPreference(value)}
            className={`flex flex-1 items-center justify-center rounded-md px-2.5 py-1.5 transition-colors ${
              selected ? 'bg-surface text-fg shadow-sm' : 'text-fg-subtle hover:text-fg'
            }`}
          >
            <Icon aria-hidden className="size-4" />
          </button>
        )
      })}
    </div>
  )
}
