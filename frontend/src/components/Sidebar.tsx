import { LogOut, PanelLeftClose, PanelLeftOpen } from 'lucide-react'
import { NavLink } from 'react-router'
import { useAuth } from '../auth/useAuth.ts'
import { ThemeSwitcher } from '../theme/ThemeSwitcher.tsx'
import { LogoMark } from './Logo.tsx'
import { NAV_ITEMS } from './navigation.ts'

interface SidebarProps {
  collapsed: boolean
  onCollapsedChange(collapsed: boolean): void
}

/**
 * Desktop sidebar. Collapsed, it is an icon rail that slides open over the page while the
 * pointer (or keyboard focus) is on it; the wallet logo or the panel button pins it open.
 *
 * The content always has the expanded width and the aside clips it, so icons never move:
 * only the width animates and the labels fade.
 */
export function Sidebar({ collapsed, onCollapsedChange }: SidebarProps) {
  const { user, logout } = useAuth()

  // Hidden while collapsed, shown while the rail is hovered or focused.
  const revealed = collapsed
    ? 'opacity-0 transition-opacity group-hover/sidebar:opacity-100 group-hover/sidebar:delay-150 group-has-[:focus-visible]/sidebar:opacity-100'
    : ''

  return (
    <aside
      aria-label="Kenar çubuğu"
      className={`group/sidebar fixed inset-y-0 left-0 z-20 hidden overflow-hidden border-r border-line bg-surface px-3 py-6 transition-[width,box-shadow] duration-200 ease-out md:flex ${
        collapsed
          ? 'w-[4.5rem] hover:w-60 hover:shadow-xl hover:delay-150 has-[:focus-visible]:w-60 has-[:focus-visible]:shadow-xl'
          : 'w-60'
      }`}
    >
      <div className="flex w-[13.5rem] shrink-0 flex-col">
        <div className="flex items-center justify-between px-2">
          <button
            type="button"
            onClick={() => collapsed && onCollapsedChange(false)}
            aria-label={collapsed ? 'Menüyü sabitle' : undefined}
            title={collapsed ? 'Menüyü sabitle' : undefined}
            className={`flex items-center gap-2 font-bold text-fg ${collapsed ? '' : 'cursor-default'}`}
            tabIndex={collapsed ? 0 : -1}
          >
            <LogoMark />
            <span className={revealed}>Harcamam</span>
          </button>
          <button
            type="button"
            onClick={() => onCollapsedChange(!collapsed)}
            aria-label={collapsed ? 'Menüyü sabitle' : 'Menüyü daralt'}
            title={collapsed ? 'Menüyü sabitle' : 'Menüyü daralt'}
            className={`rounded-lg p-1.5 text-fg-subtle hover:bg-surface-muted hover:text-fg ${revealed}`}
          >
            {collapsed ? (
              <PanelLeftOpen aria-hidden className="size-5" />
            ) : (
              <PanelLeftClose aria-hidden className="size-5" />
            )}
          </button>
        </div>

        <nav aria-label="Ana menü" className="mt-8 flex flex-1 flex-col gap-1">
          {NAV_ITEMS.map(({ to, label, icon: Icon }) => (
            <NavLink
              key={to}
              to={to}
              end={to === '/'}
              title={collapsed ? label : undefined}
              className={({ isActive }) =>
                `flex items-center gap-3 rounded-lg px-3.5 py-2 text-sm font-medium whitespace-nowrap transition-colors ${
                  isActive
                    ? 'bg-accent-soft text-accent-fg'
                    : 'text-fg-muted hover:bg-surface-muted'
                }`
              }
            >
              <Icon aria-hidden className="size-5 shrink-0" />
              <span className={revealed}>{label}</span>
            </NavLink>
          ))}
        </nav>

        <div className="border-t border-line pt-4">
          <ThemeSwitcher className={`mb-4 flex w-full ${revealed}`} />
          <p className={`truncate px-3.5 text-sm text-fg-subtle ${revealed}`} title={user?.email}>
            {user?.email}
          </p>
          <button
            type="button"
            onClick={logout}
            title={collapsed ? 'Çıkış yap' : undefined}
            className="mt-2 flex w-full items-center gap-3 rounded-lg px-3.5 py-2 text-sm font-medium whitespace-nowrap text-fg-muted hover:bg-surface-muted"
          >
            <LogOut aria-hidden className="size-5 shrink-0" />
            <span className={revealed}>Çıkış yap</span>
          </button>
        </div>
      </div>
    </aside>
  )
}
