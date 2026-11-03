import { LogOut } from 'lucide-react'
import { NavLink, Outlet } from 'react-router'
import { useAuth } from '../auth/useAuth.ts'
import { usePersistentState } from '../lib/usePersistentState.ts'
import { ThemeSwitcher } from '../theme/ThemeSwitcher.tsx'
import { Logo } from './Logo.tsx'
import { NAV_ITEMS } from './navigation.ts'
import { Sidebar } from './Sidebar.tsx'

function tabLinkClass({ isActive }: { isActive: boolean }) {
  return `flex flex-1 flex-col items-center gap-1 py-2 text-xs font-medium ${
    isActive ? 'text-accent-fg' : 'text-fg-subtle'
  }`
}

export function AppLayout() {
  const { logout } = useAuth()
  const [sidebarCollapsed, setSidebarCollapsed] = usePersistentState(
    'harcamam.sidebarCollapsed',
    false,
  )

  return (
    <div className="min-h-screen bg-canvas">
      <Sidebar collapsed={sidebarCollapsed} onCollapsedChange={setSidebarCollapsed} />

      {/* Mobile: top bar */}
      <header className="sticky top-0 z-10 flex items-center justify-between border-b border-line bg-surface px-4 py-3 md:hidden">
        <Logo />
        <div className="flex items-center gap-2">
          <ThemeSwitcher />
          <button
            type="button"
            onClick={logout}
            aria-label="Çıkış yap"
            className="rounded-lg p-2 text-fg-muted hover:bg-surface-muted"
          >
            <LogOut aria-hidden className="size-5" />
          </button>
        </div>
      </header>

      {/* The hover-expanded rail overlays the page, so the margin follows the pinned state only. */}
      <main
        className={`px-4 pt-6 pb-24 transition-[margin] duration-200 ease-out md:px-8 md:pb-10 ${
          sidebarCollapsed ? 'md:ml-[4.5rem]' : 'md:ml-60'
        }`}
      >
        <div className="mx-auto max-w-6xl">
          <Outlet />
        </div>
      </main>

      {/* Mobile: bottom tab bar */}
      <nav
        aria-label="Ana menü"
        className="fixed inset-x-0 bottom-0 z-10 flex border-t border-line bg-surface md:hidden"
      >
        {NAV_ITEMS.map(({ to, label, icon: Icon }) => (
          <NavLink key={to} to={to} end={to === '/'} className={tabLinkClass}>
            <Icon aria-hidden className="size-5" />
            {label}
          </NavLink>
        ))}
      </nav>
    </div>
  )
}
