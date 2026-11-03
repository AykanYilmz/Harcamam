import { ArrowRight, Sparkles } from 'lucide-react'
import { Link } from 'react-router'
import { useUncategorized } from '../api/transactions.ts'
import { UNCATEGORIZED_PATH } from './navigation.ts'
import { Card } from './ui/Card.tsx'

/** Points to the page for sorting out unrecognized transactions; hidden when there are none. */
export function UncategorizedHint({ className = '' }: { className?: string }) {
  const { data } = useUncategorized()
  if (!data?.transaction_count) return null

  return (
    <Card className={`flex flex-wrap items-center gap-x-4 gap-y-2 ${className}`}>
      <Sparkles aria-hidden className="size-5 shrink-0 text-accent-fg" />
      <p className="flex-1 text-sm text-fg-muted">
        <span className="font-medium text-fg">{data.transaction_count} işlem</span> hiçbir kurala
        uymadığı için "Diğer"de. Yerleri bir kez tanıtırsan sonraki ekstrelerde kendiliğinden
        ayrılır.
      </p>
      <Link
        to={UNCATEGORIZED_PATH}
        className="inline-flex items-center gap-1 text-sm font-medium text-accent-fg hover:underline"
      >
        Kategorize et
        <ArrowRight aria-hidden className="size-4" />
      </Link>
    </Card>
  )
}
