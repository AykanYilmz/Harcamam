import { LayoutDashboard, List, LogOut, Tags, Upload, type LucideIcon } from 'lucide-react'
import { NavLink, Outlet } from 'react-router'
import { useAuth } from '../auth/useAuth.ts'
import { Logo } from './Logo.tsx'

interface NavItem {
  to: string
  label: string
  icon: LucideIcon
}

const NAV_ITEMS: NavItem[] = [
  { to: '/', label: 'Özet', icon: LayoutDashboard },
  { to: '/yukle', label: 'Ekstre Yükle', icon: Upload },
  { to: '/islemler', label: 'İşlemler', icon: List },
  { to: '/kategoriler', label: 'Kategoriler', icon: Tags },
]

function sidebarLinkClass({ isActive }: { isActive: boolean }) {
  return `flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors ${
    isActive ? 'bg-emerald-50 text-emerald-700' : 'text-slate-600 hover:bg-slate-100'
  }`
}

function tabLinkClass({ isActive }: { isActive: boolean }) {
  return `flex flex-1 flex-col items-center gap-1 py-2 text-xs font-medium ${
    isActive ? 'text-emerald-700' : 'text-slate-500'
  }`
}

export function AppLayout() {
  const { user, logout } = useAuth()

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Desktop: fixed sidebar */}
      <aside className="fixed inset-y-0 left-0 hidden w-60 flex-col border-r border-slate-200 bg-white px-4 py-6 md:flex">
        <Logo className="px-2" />
        <nav aria-label="Ana menü" className="mt-8 flex flex-1 flex-col gap-1">
          {NAV_ITEMS.map(({ to, label, icon: Icon }) => (
            <NavLink key={to} to={to} end={to === '/'} className={sidebarLinkClass}>
              <Icon aria-hidden className="size-5" />
              {label}
            </NavLink>
          ))}
        </nav>
        <div className="border-t border-slate-200 pt-4">
          <p className="truncate px-3 text-sm text-slate-500" title={user?.email}>
            {user?.email}
          </p>
          <button
            type="button"
            onClick={logout}
            className="mt-2 flex w-full items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium text-slate-600 hover:bg-slate-100"
          >
            <LogOut aria-hidden className="size-5" />
            Çıkış yap
          </button>
        </div>
      </aside>

      {/* Mobile: top bar */}
      <header className="sticky top-0 z-10 flex items-center justify-between border-b border-slate-200 bg-white px-4 py-3 md:hidden">
        <Logo />
        <button
          type="button"
          onClick={logout}
          aria-label="Çıkış yap"
          className="rounded-lg p-2 text-slate-600 hover:bg-slate-100"
        >
          <LogOut aria-hidden className="size-5" />
        </button>
      </header>

      <main className="px-4 pt-6 pb-24 md:ml-60 md:px-8 md:pb-10">
        <div className="mx-auto max-w-6xl">
          <Outlet />
        </div>
      </main>

      {/* Mobile: bottom tab bar */}
      <nav
        aria-label="Ana menü"
        className="fixed inset-x-0 bottom-0 z-10 flex border-t border-slate-200 bg-white md:hidden"
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
