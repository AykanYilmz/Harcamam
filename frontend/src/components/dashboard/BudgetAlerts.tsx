import { ArrowRight, TriangleAlert } from 'lucide-react'
import { Link } from 'react-router'
import { useBudgets } from '../../api/budgets.ts'
import type { Budget } from '../../api/types.ts'
import { formatCurrency, formatPercent } from '../../lib/format.ts'
import { BUDGETS_PATH } from '../navigation.ts'
import { Card } from '../ui/Card.tsx'

function alertText(budget: Budget): string {
  if (budget.status === 'over') {
    return `limit ${formatCurrency(-Number(budget.remaining))} aşıldı`
  }
  return `${formatPercent(budget.used_pct)} dolu`
}

/** Budgets close to or over their limit in `month`; nothing when all are on track. */
export function BudgetAlerts({ month, className = '' }: { month: string; className?: string }) {
  const { data } = useBudgets(month)
  const alerts = data?.budgets.filter((budget) => budget.status !== 'ok') ?? []
  if (alerts.length === 0) return null

  return (
    <Card className={`border-l-4 border-warning-line ${className}`}>
      <div className="flex items-start gap-3">
        <TriangleAlert aria-hidden className="mt-0.5 size-5 shrink-0 text-warning-fg" />
        <div className="min-w-0 flex-1">
          <h2 className="font-semibold text-fg">Bütçe uyarıları</h2>
          <ul className="mt-1 space-y-0.5 text-sm text-fg-muted">
            {alerts.map((budget) => (
              <li key={budget.id}>
                <span
                  className={`font-medium ${budget.status === 'over' ? 'text-danger-fg' : 'text-warning-fg'}`}
                >
                  {budget.name}
                </span>
                : {alertText(budget)}
              </li>
            ))}
          </ul>
        </div>
        <Link
          to={`${BUDGETS_PATH}?ay=${month}`}
          className="inline-flex shrink-0 items-center gap-1 text-sm font-medium text-accent-fg hover:underline"
        >
          Bütçeler
          <ArrowRight aria-hidden className="size-4" />
        </Link>
      </div>
    </Card>
  )
}
