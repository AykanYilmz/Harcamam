import { useEffect, useState } from 'react'

const API_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

type ApiStatus = 'checking' | 'online' | 'offline'

const statusLabels: Record<ApiStatus, string> = {
  checking: 'Kontrol ediliyor…',
  online: 'Bağlı',
  offline: 'Bağlantı yok',
}

const statusColors: Record<ApiStatus, string> = {
  checking: 'bg-slate-400',
  online: 'bg-emerald-500',
  offline: 'bg-rose-500',
}

function App() {
  const [status, setStatus] = useState<ApiStatus>('checking')

  useEffect(() => {
    const controller = new AbortController()

    fetch(`${API_URL}/health`, { signal: controller.signal })
      .then((response) => setStatus(response.ok ? 'online' : 'offline'))
      .catch((error: unknown) => {
        if (!(error instanceof DOMException && error.name === 'AbortError')) {
          setStatus('offline')
        }
      })

    return () => controller.abort()
  }, [])

  return (
    <main className="flex min-h-screen items-center justify-center bg-slate-50 px-4">
      <div className="w-full max-w-md rounded-2xl bg-white p-8 text-center shadow-sm ring-1 ring-slate-200">
        <h1 className="text-3xl font-bold text-slate-900">Harcamam</h1>
        <p className="mt-2 text-slate-600">Kişisel finans ve harcama analizi</p>

        <div className="mt-6 inline-flex items-center gap-2 rounded-full bg-slate-100 px-4 py-2 text-sm text-slate-700">
          <span className={`h-2.5 w-2.5 rounded-full ${statusColors[status]}`} />
          API durumu: {statusLabels[status]}
        </div>
      </div>
    </main>
  )
}

export default App
