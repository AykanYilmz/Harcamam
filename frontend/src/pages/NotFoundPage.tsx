import { Link } from 'react-router'

export function NotFoundPage() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-slate-50 px-4 text-center">
      <p className="text-5xl font-bold text-slate-300">404</p>
      <h1 className="mt-4 text-xl font-semibold text-slate-900">Sayfa bulunamadı</h1>
      <Link to="/" className="mt-6 font-medium text-emerald-700 hover:underline">
        Ana sayfaya dön
      </Link>
    </div>
  )
}
