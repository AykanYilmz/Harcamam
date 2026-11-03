import { Link } from 'react-router'

export function NotFoundPage() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-canvas px-4 text-center">
      <p className="text-5xl font-bold text-fg-faint">404</p>
      <h1 className="mt-4 text-xl font-semibold text-fg">Sayfa bulunamadı</h1>
      <Link to="/" className="mt-6 font-medium text-accent-fg hover:underline">
        Ana sayfaya dön
      </Link>
    </div>
  )
}
