import { LogOut } from 'lucide-react'
import { NavLink } from 'react-router'
import { useAuth } from '../auth/useAuth.ts'
import { ThemeSwitcher } from '../theme/ThemeSwitcher.tsx'
import { Logo } from './Logo.tsx'
import { NAV_SECTIONS } from './navigation.ts'

export const SIDEBAR_ID = 'app-sidebar'

interface SidebarProps {
  /** Shown on phones (as a drawer over the page). */
  mobileOpen: boolean
  /** Shown on wider screens (next to the page). */
  desktopOpen: boolean
  /** Called after a link is chosen, so the phone drawer can close. */
  onNavigate(): void
}

function linkClass({ isActive }: { isActive: boolean }) {
  // Focus ring only for keyboard users, in the app's green instead of the browser's black.
  return `flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors outline-none focus-visible:ring-2 focus-visible:ring-emerald-500 ${
    isActive
      ? 'bg-accent-soft text-accent-fg'
      : 'text-fg-muted hover:bg-surface-muted hover:text-fg'
  }`
}

export function Sidebar({ mobileOpen, desktopOpen, onNavigate }: SidebarProps) {
  const { user, logout } = useAuth()

  // `invisible` also takes the closed sidebar out of the keyboard tab order.
  const mobileState = mobileOpen ? 'visible translate-x-0' : 'invisible -translate-x-full'
  const desktopState = desktopOpen
    ? 'md:visible md:translate-x-0'
    : 'md:invisible md:-translate-x-full'

  return (
    <aside
      id={SIDEBAR_ID}
      aria-label="Kenar çubuğu"
      // `dark` makes the sidebar a dark-theme island: every color token inside it takes its
      // dark value, so it stays dark (and readable) while the page is in the light theme.
      className={`dark fixed inset-y-0 left-0 z-40 flex w-64 flex-col border-r border-line bg-sidebar text-fg transition-[translate,visibility] duration-300 ease-drawer ${mobileState} ${desktopState}`}
    >
      <div className="flex h-14 shrink-0 items-center border-b border-line px-4">
        <Logo />
      </div>

      <nav aria-label="Ana menü" className="flex-1 overflow-y-auto px-3 py-4">
        {NAV_SECTIONS.map((section, index) => (
          <ul
            key={index}
            className={`space-y-1 ${index > 0 ? 'mt-3 border-t border-line pt-3' : ''}`}
          >
            {section.map(({ to, label, icon: Icon }) => (
              <li key={to}>
                <NavLink to={to} end={to === '/'} className={linkClass} onClick={onNavigate}>
                  <Icon aria-hidden className="size-5 shrink-0" />
                  {label}
                </NavLink>
              </li>
            ))}
          </ul>
        ))}
      </nav>

      <div className="space-y-3 border-t border-line p-4">
        <div className="flex items-center justify-between">
          <span className="text-sm text-fg-subtle">Tema</span>
          <ThemeSwitcher />
        </div>
        <p className="truncate text-sm text-fg-subtle" title={user?.email}>
          {user?.email}
        </p>
        <button
          type="button"
          onClick={logout}
          className="flex w-full items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium text-fg-muted hover:bg-surface-muted hover:text-fg"
        >
          <LogOut aria-hidden className="size-5" />
          Çıkış yap
        </button>
      </div>
    </aside>
  )
}
