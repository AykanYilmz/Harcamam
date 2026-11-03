import { Menu } from 'lucide-react'
import { useEffect, useState } from 'react'
import { Outlet, useLocation } from 'react-router'
import { usePersistentState } from '../lib/usePersistentState.ts'
import { pageTitle } from './navigation.ts'
import { SIDEBAR_ID, Sidebar } from './Sidebar.tsx'

const DESKTOP_QUERY = '(min-width: 768px)'

export function AppLayout() {
  const { pathname } = useLocation()
  // Wide screens remember the choice; on phones the drawer always starts closed.
  const [desktopOpen, setDesktopOpen] = usePersistentState('harcamam.sidebarOpen', true)
  const [mobileOpen, setMobileOpen] = useState(false)

  const isDesktop = () => window.matchMedia?.(DESKTOP_QUERY).matches ?? true
  const sidebarOpen = () => (isDesktop() ? desktopOpen : mobileOpen)

  function toggleSidebar() {
    if (isDesktop()) setDesktopOpen(!desktopOpen)
    else setMobileOpen(!mobileOpen)
  }

  useEffect(() => {
    if (!mobileOpen) return
    const closeOnEscape = (event: KeyboardEvent) => event.key === 'Escape' && setMobileOpen(false)
    window.addEventListener('keydown', closeOnEscape)
    return () => window.removeEventListener('keydown', closeOnEscape)
  }, [mobileOpen])

  return (
    <div className="min-h-screen bg-canvas">
      <Sidebar
        mobileOpen={mobileOpen}
        desktopOpen={desktopOpen}
        onNavigate={() => setMobileOpen(false)}
      />

      {/* Phone drawer backdrop */}
      {mobileOpen && (
        <div
          aria-hidden
          onClick={() => setMobileOpen(false)}
          className="fixed inset-0 z-30 bg-slate-950/50 md:hidden"
        />
      )}

      <div className={`transition-[margin] duration-200 ease-out ${desktopOpen ? 'md:ml-64' : ''}`}>
        <header className="sticky top-0 z-20 flex h-14 items-center gap-3 bg-emerald-600 px-4 text-white shadow-sm dark:bg-emerald-700">
          <button
            type="button"
            onClick={toggleSidebar}
            aria-label={sidebarOpen() ? 'Menüyü kapat' : 'Menüyü aç'}
            aria-expanded={sidebarOpen()}
            aria-controls={SIDEBAR_ID}
            className="rounded-lg p-2 hover:bg-white/15 focus-visible:outline-2 focus-visible:outline-white"
          >
            <Menu aria-hidden className="size-5" />
          </button>
          <h1 className="text-lg font-semibold">{pageTitle(pathname)}</h1>
        </header>

        <main className="px-4 py-6 md:px-8">
          <div className="mx-auto max-w-6xl">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  )
}
