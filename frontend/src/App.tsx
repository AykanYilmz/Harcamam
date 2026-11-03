import { lazy, Suspense } from 'react'
import { Route, Routes } from 'react-router'
import { GuestOnly, RequireAuth } from './auth/routes.tsx'
import { AppLayout } from './components/AppLayout.tsx'
import { LoginPage } from './pages/LoginPage.tsx'
import { NotFoundPage } from './pages/NotFoundPage.tsx'
import { RegisterPage } from './pages/RegisterPage.tsx'
import { UploadPage } from './pages/UploadPage.tsx'
import { PageLoader } from './components/ui/Spinner.tsx'

// The dashboard pulls in the chart library; loading it on demand keeps the login page light.
const DashboardPage = lazy(() =>
  import('./pages/DashboardPage.tsx').then((module) => ({ default: module.DashboardPage })),
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
          <Route path="/yukle" element={<UploadPage />} />
        </Route>
      </Route>
      <Route path="*" element={<NotFoundPage />} />
    </Routes>
  )
}

export default App
