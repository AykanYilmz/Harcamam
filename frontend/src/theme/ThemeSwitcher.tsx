import { Moon, Sun } from 'lucide-react'
import { Switch } from '../components/ui/Switch.tsx'
import { useTheme } from './useTheme.ts'

/** Light/dark switch: the knob slides over and shows a sun or a moon. */
export function ThemeSwitcher({ className = '' }: { className?: string }) {
  const { theme, setTheme } = useTheme()
  const dark = theme === 'dark'

  return (
    <Switch
      checked={dark}
      onChange={(on) => setTheme(on ? 'dark' : 'light')}
      label="Koyu tema"
      knob={dark ? <Moon className="size-3" /> : <Sun className="size-3" />}
      className={className}
    />
  )
}
