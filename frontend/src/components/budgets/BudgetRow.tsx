import { Pencil, Trash2 } from 'lucide-react'
import type { Budget, BudgetStatus } from '../../api/types.ts'
import { BUDGET_STATUS_LABELS } from '../../lib/budgets.ts'
import { formatCurrency, formatPercent } from '../../lib/format.ts'
import { CategoryIcon } from '../CategoryIcon.tsx'

const BAR_COLORS: Record<BudgetStatus, string> = {
  ok: 'bg-emerald-500',
  warning: 'bg-amber-500',
  over: 'bg-rose-500',
}

const STATUS_TEXT: Record<BudgetStatus, string> = {
  ok: 'text-accent-fg',
  warning: 'text-warning-fg',
  over: 'text-danger-fg',
}

/** One line of advice under the bar: how much is left, or where the pace leads. */
function outlook(budget: Budget): string {
  const limit = Number(budget.monthly_limit)
  if (budget.status === 'over') {
    return `Limit ${formatCurrency(-Number(budget.remaining))} aşıldı.`
  }
  const projected = budget.projected === null ? null : Number(budget.projected)
  if (projected !== null && projected > limit) {
    return `Bu hızla ay sonunda ${formatCurrency(projected)} olur; limitin ${formatCurrency(projected - limit)} üstü.`
  }
  return `${formatCurrency(budget.remaining)} kaldı.`
}

export function BudgetRow({
  budget,
  onEdit,
  onDelete,
}: {
  budget: Budget
  onEdit(): void
  onDelete(): void
}) {
  const used = budget.used_pct

  return (
    <li className="py-4">
      <div className="flex items-start gap-3">
        <CategoryIcon icon={budget.icon} color={budget.color} />
        <div className="min-w-0 flex-1">
          <div className="flex flex-wrap items-baseline justify-between gap-x-3">
            <span className="font-medium text-fg">{budget.name}</span>
            <span className="text-sm text-fg-muted tabular-nums">
              <span className="font-semibold text-fg">{formatCurrency(budget.spent)}</span> /{' '}
              {formatCurrency(budget.monthly_limit)}
            </span>
          </div>
          <div
            role="progressbar"
            aria-label={`${budget.name} bütçesinin kullanılan kısmı`}
            aria-valuemin={0}
            aria-valuemax={100}
            aria-valuenow={Math.min(Math.round(used), 100)}
            aria-valuetext={`%${used}`}
            className="mt-2 h-2 overflow-hidden rounded-full bg-surface-muted"
          >
            <div
              className={`h-full origin-left animate-bar-grow rounded-full ${BAR_COLORS[budget.status]}`}
              style={{ width: `${Math.min(used, 100)}%` }}
            />
          </div>
          <p className="mt-1.5 text-xs text-fg-subtle">
            <span className={`font-medium ${STATUS_TEXT[budget.status]}`}>
              {BUDGET_STATUS_LABELS[budget.status]} · {formatPercent(used)}
            </span>{' '}
            · {outlook(budget)}
          </p>
        </div>
        <div className="flex shrink-0">
          <button
            type="button"
            onClick={onEdit}
            aria-label={`${budget.name} bütçesini düzenle`}
            title="Düzenle"
            className="rounded-lg p-2 text-fg-subtle hover:bg-surface-muted hover:text-fg"
          >
            <Pencil aria-hidden className="size-4" />
          </button>
          <button
            type="button"
            onClick={onDelete}
            aria-label={`${budget.name} bütçesini sil`}
            title="Sil"
            className="rounded-lg p-2 text-fg-subtle hover:bg-danger-soft hover:text-danger-fg"
          >
            <Trash2 aria-hidden className="size-4" />
          </button>
        </div>
      </div>
    </li>
  )
}
