import { Minus, TrendingDown, TrendingUp } from 'lucide-react'
import { formatCurrency, formatPercent } from '../../lib/format.ts'
import { Card } from '../ui/Card.tsx'

interface StatTileProps {
  label: string
  amount: string
  /** Change against the previous month; null when there is nothing to compare with. */
  changePct: number | null
  /** Which direction is good news: more income is, more spending isn't. */
  goodWhen: 'up' | 'down'
}

function ChangeBadge({ changePct, goodWhen }: Pick<StatTileProps, 'changePct' | 'goodWhen'>) {
  if (changePct === null) {
    return <p className="mt-2 text-sm text-fg-subtle">Geçen ayla karşılaştırma yok</p>
  }
  if (changePct === 0) {
    return (
      <p className="mt-2 flex items-center gap-1 text-sm text-fg-subtle">
        <Minus aria-hidden className="size-4" />
        Geçen ayla aynı
      </p>
    )
  }

  const up = changePct > 0
  const good = up === (goodWhen === 'up')
  const Icon = up ? TrendingUp : TrendingDown
  // Color is never the only cue: the icon and the words say the same thing.
  return (
    <p
      className={`mt-2 flex items-center gap-1 text-sm ${good ? 'text-accent-fg' : 'text-danger-fg'}`}
    >
      <Icon aria-hidden className="size-4" />
      <span className="font-medium">{formatPercent(Math.abs(changePct))}</span>{' '}
      <span className="text-fg-subtle">{up ? 'arttı' : 'azaldı'} · geçen aya göre</span>
    </p>
  )
}

export function StatTile({ label, amount, changePct, goodWhen }: StatTileProps) {
  return (
    <Card>
      <p className="text-sm font-medium text-fg-subtle">{label}</p>
      <p className="mt-1 text-2xl font-semibold tracking-tight text-fg tabular-nums sm:text-3xl">
        {formatCurrency(amount)}
      </p>
      <ChangeBadge changePct={changePct} goodWhen={goodWhen} />
    </Card>
  )
}
