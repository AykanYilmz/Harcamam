import { Construction } from 'lucide-react'
import { Card } from '../components/ui/Card.tsx'

/** Placeholder for pages built in the next steps of Phase 5. */
export function ComingSoonPage({ title }: { title: string }) {
  return (
    <>
      <h1 className="text-2xl font-semibold text-fg">{title}</h1>
      <Card className="mt-6 flex flex-col items-center py-12 text-center">
        <Construction aria-hidden className="size-10 text-fg-faint" />
        <p className="mt-3 font-medium text-fg-secondary">Bu sayfa hazırlanıyor</p>
        <p className="mt-1 text-sm text-fg-subtle">Çok yakında burada olacak.</p>
      </Card>
    </>
  )
}
