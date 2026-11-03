import {
  ArrowDownLeft,
  ArrowUpRight,
  Minus,
  PiggyBank,
  TrendingDown,
  TrendingUp,
  type LucideIcon,
} from 'lucide-react'
import { formatCurrency, formatPercent } from '../../lib/format.ts'
import { AnimatedNumber } from '../ui/AnimatedNumber.tsx'
import { Card } from '../ui/Card.tsx'

type Tone = 'income' | 'expense' | 'net'

// Income and expense reuse the chart colors, so a hue means the same thing on the whole page.
const TONES: Record<Tone, { icon: LucideIcon; chip: string }> = {
  income: { icon: ArrowDownLeft, chip: 'bg-chart-income/15 text-chart-income' },
  expense: { icon: ArrowUpRight, chip: 'bg-chart-expense/15 text-chart-expense' },
  net: { icon: PiggyBank, chip: 'bg-accent-soft text-accent-fg' },
}

interface StatTileProps {
  label: string
  amount: string
  tone: Tone
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

export function StatTile({ label, amount, tone, changePct, goodWhen }: StatTileProps) {
  const { icon: Icon, chip } = TONES[tone]
  const negative = Number(amount) < 0
  const amountColor = tone === 'net' ? (negative ? 'text-danger-fg' : 'text-accent-fg') : 'text-fg'

  return (
    <Card>
      <div className="flex items-center gap-3">
        <span className={`flex size-10 items-center justify-center rounded-xl ${chip}`}>
          <Icon aria-hidden className="size-5" />
        </span>
        <p className="text-sm font-medium text-fg-subtle">{label}</p>
      </div>
      <p
        className={`mt-3 text-2xl font-semibold tracking-tight tabular-nums sm:text-3xl ${amountColor}`}
      >
        <AnimatedNumber value={Number(amount)} format={formatCurrency} />
      </p>
      <ChangeBadge changePct={changePct} goodWhen={goodWhen} />
    </Card>
  )
}
