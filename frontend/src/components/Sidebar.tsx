import { LogOut } from 'lucide-react'
import { NavLink } from 'react-router'
import { useAuth } from '../auth/useAuth.ts'
import { ThemeSwitcher } from '../theme/ThemeSwitcher.tsx'
import { NAV_SECTIONS } from './navigation.ts'

export const SIDEBAR_ID = 'app-sidebar'

interface SidebarProps {
  /** Slides in over the page. */
  open: boolean
  /** Called after a link is chosen, so the menu can close. */
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

export function Sidebar({ open, onNavigate }: SidebarProps) {
  const { user, logout } = useAuth()

  // `invisible` also takes the closed sidebar out of the keyboard tab order.
  const state = open ? 'visible translate-x-0 shadow-xl' : 'invisible -translate-x-full'

  return (
    <aside
      id={SIDEBAR_ID}
      aria-label="Kenar çubuğu"
      className={`fixed inset-y-0 left-0 z-40 flex w-64 print:hidden flex-col border-r border-line bg-surface transition-[translate,visibility] duration-300 ease-drawer ${state}`}
    >
      {/* The app bar already names the app; the menu carries its motto. */}
      <div className="shrink-0 border-b border-line bg-linear-to-br from-accent-soft to-transparent px-5 pt-6 pb-5">
        <p className="font-serif text-[1.35rem] leading-tight text-fg">
          Her kuruşun <em className="text-accent-fg">hesabı</em>,
          <br />
          her ayın <em className="text-accent-fg">kitabı</em>.
        </p>
        <span aria-hidden className="mt-4 block h-1 w-10 rounded-full bg-emerald-500" />
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
