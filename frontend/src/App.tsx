import { lazy, Suspense } from 'react'
import { Route, Routes } from 'react-router'
import { GuestOnly, RequireAuth } from './auth/routes.tsx'
import { AppLayout } from './components/AppLayout.tsx'
import { CalendarPage } from './pages/CalendarPage.tsx'
import { CategoriesPage } from './pages/CategoriesPage.tsx'
import { HelpPage } from './pages/HelpPage.tsx'
import { LoginPage } from './pages/LoginPage.tsx'
import { NotFoundPage } from './pages/NotFoundPage.tsx'
import { RegisterPage } from './pages/RegisterPage.tsx'
import { SettingsPage } from './pages/SettingsPage.tsx'
import { TransactionsPage } from './pages/TransactionsPage.tsx'
import { UploadPage } from './pages/UploadPage.tsx'
import { VerifyEmailPage } from './pages/VerifyEmailPage.tsx'
import { PageLoader } from './components/ui/Spinner.tsx'

// Pages with charts pull in the chart library; loading them on demand keeps the login page light.
const DashboardPage = lazy(() =>
  import('./pages/DashboardPage.tsx').then((module) => ({ default: module.DashboardPage })),
)
const ReportsPage = lazy(() =>
  import('./pages/ReportsPage.tsx').then((module) => ({ default: module.ReportsPage })),
)

function App() {
  return (
    <Routes>
      <Route element={<GuestOnly />}>
        <Route path="/giris" element={<LoginPage />} />
        <Route path="/kayit" element={<RegisterPage />} />
      </Route>
      <Route element={<RequireAuth />}>
        <Route element={<AppLayout />}>
          <Route
            index
            element={
              <Suspense fallback={<PageLoader />}>
                <DashboardPage />
              </Suspense>
            }
          />
          <Route path="/islemler" element={<TransactionsPage />} />
          <Route path="/takvim" element={<CalendarPage />} />
          <Route
            path="/raporlar"
            element={
              <Suspense fallback={<PageLoader />}>
                <ReportsPage />
              </Suspense>
            }
          />
          <Route path="/yukle" element={<UploadPage />} />
          <Route path="/kategoriler" element={<CategoriesPage />} />
          <Route path="/ayarlar" element={<SettingsPage />} />
          <Route path="/yardim" element={<HelpPage />} />
        </Route>
      </Route>
      {/* Opened from an email, logged in or not. */}
      <Route path="/eposta-dogrula" element={<VerifyEmailPage />} />
      <Route path="*" element={<NotFoundPage />} />
    </Routes>
  )
}

export default App
