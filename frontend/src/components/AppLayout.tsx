import { Menu, Wallet } from 'lucide-react'
import { useEffect, useState } from 'react'
import { Link, Outlet, useLocation } from 'react-router'
import { useAuth } from '../auth/useAuth.ts'
import { pageTitle } from './navigation.ts'
import { SIDEBAR_ID, Sidebar } from './Sidebar.tsx'
import { VerifyEmailBanner } from './VerifyEmailBanner.tsx'

export function AppLayout() {
  const { pathname } = useLocation()
  const [menuOpen, setMenuOpen] = useState(false)
  const { user } = useAuth()
  // Hidden for the rest of this visit once dismissed; it comes back on the next one.
  const [bannerDismissed, setBannerDismissed] = useState(false)

  useEffect(() => {
    if (!menuOpen) return
    const closeOnEscape = (event: KeyboardEvent) => event.key === 'Escape' && setMenuOpen(false)
    window.addEventListener('keydown', closeOnEscape)
    return () => window.removeEventListener('keydown', closeOnEscape)
  }, [menuOpen])

  return (
    <div className="min-h-screen bg-canvas">
      <Sidebar open={menuOpen} onNavigate={() => setMenuOpen(false)} />

      {/* Backdrop: a click anywhere on the page closes the menu. Always rendered so it can
          fade out as well as in. */}
      <div
        aria-hidden
        onClick={() => setMenuOpen(false)}
        className={`fixed inset-0 z-30 bg-slate-950/40 transition-opacity duration-300 ease-drawer ${
          menuOpen ? 'opacity-100' : 'pointer-events-none opacity-0'
        }`}
      />

      <header className="sticky top-0 z-20 grid h-14 print:hidden grid-cols-[1fr_auto_1fr] items-center gap-3 bg-emerald-600 px-4 text-white shadow-sm dark:bg-emerald-700">
        <div className="flex min-w-0 items-center gap-3">
          <button
            type="button"
            onClick={() => setMenuOpen(!menuOpen)}
            aria-label={menuOpen ? 'Menüyü kapat' : 'Menüyü aç'}
            aria-expanded={menuOpen}
            aria-controls={SIDEBAR_ID}
            className="shrink-0 rounded-lg p-2 hover:bg-white/15 focus-visible:outline-2 focus-visible:outline-white"
          >
            <Menu aria-hidden className="size-5" />
          </button>
          {/* On phones only the app name fits; the title stays for screen readers. */}
          <h1 className="sr-only truncate text-lg font-semibold sm:not-sr-only">
            {pageTitle(pathname)}
          </h1>
        </div>
        <Link
          to="/"
          className="flex items-center gap-2 rounded-lg px-2 py-1 font-bold focus-visible:outline-2 focus-visible:outline-white"
        >
          <Wallet aria-hidden className="size-5" />
          HesapKitap
        </Link>
      </header>

      {user && !user.email_verified && !bannerDismissed && (
        <VerifyEmailBanner email={user.email} onDismiss={() => setBannerDismissed(true)} />
      )}

      <main className="px-4 py-6 md:px-8">
        {/* Keyed by page (not by query string), so each page fades in once on arrival. */}
        <div key={pathname} className="mx-auto max-w-6xl animate-page-in">
          <Outlet />
        </div>
      </main>
    </div>
  )
}
