import { Construction } from 'lucide-react'
import { Card } from '../components/ui/Card.tsx'

/** Placeholder for pages built in the next steps of Phase 5. */
export function ComingSoonPage({ title }: { title: string }) {
  return (
    <>
      <h1 className="text-2xl font-semibold text-slate-900">{title}</h1>
      <Card className="mt-6 flex flex-col items-center py-12 text-center">
        <Construction aria-hidden className="size-10 text-slate-400" />
        <p className="mt-3 font-medium text-slate-700">Bu sayfa hazırlanıyor</p>
        <p className="mt-1 text-sm text-slate-500">Çok yakında burada olacak.</p>
      </Card>
    </>
  )
}
