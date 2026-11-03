import { Route, Routes } from 'react-router'
import { GuestOnly, RequireAuth } from './auth/routes.tsx'
import { AppLayout } from './components/AppLayout.tsx'
import { ComingSoonPage } from './pages/ComingSoonPage.tsx'
import { LoginPage } from './pages/LoginPage.tsx'
import { NotFoundPage } from './pages/NotFoundPage.tsx'
import { RegisterPage } from './pages/RegisterPage.tsx'

function App() {
  return (
    <Routes>
      <Route element={<GuestOnly />}>
        <Route path="/giris" element={<LoginPage />} />
        <Route path="/kayit" element={<RegisterPage />} />
      </Route>
      <Route element={<RequireAuth />}>
        <Route element={<AppLayout />}>
          <Route index element={<ComingSoonPage title="Özet" />} />
          <Route path="/yukle" element={<ComingSoonPage title="Ekstre Yükle" />} />
          <Route path="/islemler" element={<ComingSoonPage title="İşlemler" />} />
          <Route path="/kategoriler" element={<ComingSoonPage title="Kategoriler" />} />
        </Route>
      </Route>
      <Route path="*" element={<NotFoundPage />} />
    </Routes>
  )
}

export default App
