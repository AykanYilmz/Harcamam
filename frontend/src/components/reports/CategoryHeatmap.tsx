import { Link } from 'react-router'
import { useAuth } from '../../auth/useAuth.ts'
import type { CategoryTrendReport } from '../../api/types.ts'
import { heatColor, heatLevel } from '../../lib/calendar.ts'
import {
  formatCurrency,
  formatCurrencyCompact,
  formatMonth,
  formatMonthShort,
} from '../../lib/format.ts'
import { categoryMonthLink } from '../../lib/transactionFilters.ts'
import { CategoryIcon } from '../CategoryIcon.tsx'
import { Card } from '../ui/Card.tsx'

/**
 * Categories × months. Each row is shaded against its own busiest month, so a category's
 * rise and fall show up whatever its size; the totals column compares categories.
 */
export function CategoryHeatmap({ report }: { report: CategoryTrendReport }) {
  const endDay = useAuth().user?.period_end_day ?? null
  return (
    <Card className="p-0">
      <div className="px-5 pt-5">
        <h2 className="font-semibold text-fg">Kategorilerin aylık harcaması</h2>
        <p className="mt-1 text-sm text-fg-subtle">
          Renk ne kadar koyuysa o kategoride o ay o kadar çok harcanmış. Bir hücreye tıklayınca o
          ayın işlemleri açılır.
        </p>
      </div>

      {report.categories.length === 0 ? (
        <p className="px-5 py-6 text-sm text-fg-subtle">Bu dönemde harcama yok.</p>
      ) : (
        <div className="mt-4 overflow-x-auto pb-2">
          <table className="w-full border-separate border-spacing-1 px-4 text-sm">
            <thead>
              <tr className="text-xs text-fg-subtle">
                <th className="sticky left-0 bg-surface px-1 text-left font-medium">Kategori</th>
                {report.months.map((month) => (
                  <th key={month} className="min-w-16 px-1 text-center font-medium">
                    <abbr title={formatMonth(month)} className="no-underline">
                      {formatMonthShort(month)}
                    </abbr>
                  </th>
                ))}
                <th className="px-2 text-right font-medium">Toplam</th>
              </tr>
            </thead>
            <tbody>
              {report.categories.map((category) => {
                const amounts = category.amounts.map(Number)
                const max = Math.max(...amounts)
                return (
                  <tr key={category.category_id}>
                    <th
                      scope="row"
                      className="sticky left-0 bg-surface pr-3 text-left font-medium whitespace-nowrap text-fg"
                    >
                      <span className="flex items-center gap-2">
                        <CategoryIcon
                          icon={category.icon}
                          color={category.color}
                          className="size-6"
                        />
                        {category.name}
                      </span>
                    </th>
                    {amounts.map((amount, index) => {
                      const month = report.months[index]
                      return (
                        <td key={month} className="p-0">
                          {amount > 0 ? (
                            <Link
                              to={categoryMonthLink(category.category_id, month, endDay)}
                              title={`${category.name}, ${formatMonth(month)}: ${formatCurrency(amount)}`}
                              className="block rounded-md px-1.5 py-2 text-center text-xs font-medium text-fg tabular-nums ring-1 ring-line hover:ring-2 hover:ring-emerald-500"
                              style={{ backgroundColor: heatColor(heatLevel(amount, max)) }}
                            >
                              {formatCurrencyCompact(amount)}
                            </Link>
                          ) : (
                            <span className="block py-2 text-center text-xs text-fg-faint">–</span>
                          )}
                        </td>
                      )
                    })}
                    <td className="px-2 text-right font-semibold whitespace-nowrap text-fg tabular-nums">
                      {formatCurrency(category.total)}
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      )}
    </Card>
  )
}
