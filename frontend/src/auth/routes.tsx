import { Navigate, Outlet, useLocation } from 'react-router'
import { PageLoader } from '../components/ui/Spinner.tsx'
import { useAuth } from './useAuth.ts'

/** Pages that need a logged-in user; others are sent to the login page and brought back. */
export function RequireAuth() {
  const { status } = useAuth()
  const location = useLocation()

  if (status === 'loading') return <PageLoader />
  if (status === 'anonymous') {
    return <Navigate to="/giris" replace state={{ from: location.pathname }} />
  }
  return <Outlet />
}

/** Login and register pages: a logged-in user has nothing to do there. */
export function GuestOnly() {
  const { status } = useAuth()

  if (status === 'loading') return <PageLoader />
  if (status === 'authenticated') return <Navigate to="/" replace />
  return <Outlet />
}
