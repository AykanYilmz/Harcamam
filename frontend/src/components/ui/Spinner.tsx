import { LoaderCircle } from 'lucide-react'

export function Spinner({ className = 'size-5' }: { className?: string }) {
  return <LoaderCircle aria-hidden className={`animate-spin ${className}`} />
}

export function PageLoader() {
  return (
    <div role="status" className="flex min-h-[50vh] items-center justify-center text-slate-500">
      <Spinner className="size-8" />
      <span className="sr-only">Yükleniyor…</span>
    </div>
  )
}
