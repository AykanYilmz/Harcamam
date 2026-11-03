import { useState } from 'react'
import { Link } from 'react-router'
import { useAuth } from '../../auth/useAuth.ts'
import type { CategorySpending } from '../../api/types.ts'
import { formatCurrency, formatPercent } from '../../lib/format.ts'
import { categoryMonthLink } from '../../lib/transactionFilters.ts'
import { CategoryIcon } from '../CategoryIcon.tsx'
import { Card } from '../ui/Card.tsx'

const INITIALLY_SHOWN = 6

function ChangeText({ changePct }: { changePct: number | null }) {
  if (changePct === null) return <span>yeni</span>
  if (changePct === 0) return <span>değişmedi</span>
  return (
    <span>
      {changePct > 0 ? '↑' : '↓'} {formatPercent(Math.abs(changePct))}
    </span>
  )
}

/**
 * Spending per category as ranked bars on one baseline (easier to compare than pie slices).
 * The bars share one hue; the category's own color sits on its icon, beside its name.
 */
export function CategoryBreakdown({
  categories,
  month,
}: {
  categories: CategorySpending[]
  month: string
}) {
  const endDay = useAuth().user?.period_end_day ?? null
  const [showAll, setShowAll] = useState(false)
  const spent = categories.filter((category) => Number(category.amount) > 0)
  const largest = Math.max(...spent.map((category) => Number(category.amount)), 0)
  const shown = showAll ? spent : spent.slice(0, INITIALLY_SHOWN)

  return (
    <Card>
      <h2 className="font-semibold text-fg">Kategorilere göre harcama</h2>
      {spent.length === 0 ? (
        <p className="mt-4 text-sm text-fg-subtle">Bu ay harcama yok.</p>
      ) : (
        <ul className="mt-4 space-y-4">
          {shown.map((category) => (
            <li key={category.category_id} className="flex items-center gap-3">
              <CategoryIcon icon={category.icon} color={category.color} />
              <div className="min-w-0 flex-1">
                <div className="flex items-baseline justify-between gap-2">
                  <Link
                    to={categoryMonthLink(category.category_id, month, endDay)}
                    title="Bu ayın işlemlerini göster"
                    className="truncate text-sm font-medium text-fg hover:text-accent-fg hover:underline"
                  >
                    {category.name}
                  </Link>
                  <span className="text-sm font-semibold text-fg tabular-nums">
                    {formatCurrency(category.amount)}
                  </span>
                </div>
                <div className="mt-1.5 flex items-center gap-3">
                  <div className="h-2 flex-1 rounded-r bg-surface-muted">
                    <div
                      className="h-2 origin-left animate-bar-grow rounded-r bg-chart-expense"
                      style={{ width: `${(Number(category.amount) / largest) * 100}%` }}
                    />
                  </div>
                  <span className="w-28 shrink-0 text-right text-xs text-fg-subtle tabular-nums">
                    {category.share_pct !== null && formatPercent(category.share_pct)} ·{' '}
                    <ChangeText changePct={category.change_pct} />
                  </span>
                </div>
              </div>
            </li>
          ))}
        </ul>
      )}
      {spent.length > INITIALLY_SHOWN && (
        <button
          type="button"
          onClick={() => setShowAll(!showAll)}
          className="mt-4 text-sm font-medium text-accent-fg hover:underline"
        >
          {showAll ? 'Daha az göster' : `Tümünü göster (${spent.length})`}
        </button>
      )}
    </Card>
  )
}
