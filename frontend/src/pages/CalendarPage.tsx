import { useState } from 'react'
import { Link, useSearchParams } from 'react-router'
import { useCategories } from '../api/categories.ts'
import { useDailySpending, useMonthlyReport } from '../api/reports.ts'
import { useTransactions } from '../api/transactions.ts'
import { CategoryIcon } from '../components/CategoryIcon.tsx'
import { MonthPicker } from '../components/dashboard/MonthPicker.tsx'
import { ErrorAlert } from '../components/ui/Alert.tsx'
import { Card } from '../components/ui/Card.tsx'
import { PageLoader, Spinner } from '../components/ui/Spinner.tsx'
import { heatColor, heatLevel, monthGrid, todayIso, WEEKDAYS } from '../lib/calendar.ts'
import { errorMessage } from '../lib/errors.ts'
import { formatCurrency, formatCurrencyCompact, formatDate } from '../lib/format.ts'
import { DEFAULT_SORT, filtersToParams } from '../lib/transactionFilters.ts'

const MONTH_PARAM = 'ay'

function dayFilters(day: string) {
  return {
    query: '',
    dateFrom: day,
    dateTo: day,
    categoryIds: [],
    type: '' as const,
    sort: DEFAULT_SORT,
    page: 1,
  }
}

/** The transactions of the chosen day. */
function DayPanel({ day }: { day: string }) {
  const transactions = useTransactions(dayFilters(day))
  const categories = useCategories()
  const byId = new Map(categories.data?.map((category) => [category.id, category]))
  const items = transactions.data?.items ?? []

  return (
    <Card>
      <h2 className="font-semibold text-fg">{formatDate(day)}</h2>
      {transactions.isPending ? (
        <Spinner className="mt-4 size-5 text-fg-subtle" />
      ) : items.length === 0 ? (
        <p className="mt-3 text-sm text-fg-subtle">Bu gün işlem yok.</p>
      ) : (
        <ul className="mt-2 divide-y divide-line">
          {items.map((transaction) => {
            const category = byId.get(transaction.category_id)
            const income = transaction.type === 'income'
            return (
              <li key={transaction.id} className="flex items-center gap-3 py-2.5">
                {category && (
                  <CategoryIcon icon={category.icon} color={category.color} className="size-7" />
                )}
                <div className="min-w-0 flex-1">
                  <p className="truncate text-sm font-medium text-fg">{transaction.description}</p>
                  <p className="text-xs text-fg-subtle">{category?.name}</p>
                </div>
                <span
                  className={`text-sm font-semibold tabular-nums ${income ? 'text-accent-fg' : 'text-fg'}`}
                >
                  {income ? '+' : '−'}
                  {formatCurrency(transaction.amount)}
                </span>
              </li>
            )
          })}
        </ul>
      )}
      {transactions.data && transactions.data.total > items.length && (
        <Link
          to={`/islemler?${filtersToParams(dayFilters(day))}`}
          className="mt-3 inline-block text-sm font-medium text-accent-fg hover:underline"
        >
          Tümünü İşlemler'de göster ({transactions.data.total})
        </Link>
      )}
    </Card>
  )
}

export function CalendarPage() {
  const [searchParams, setSearchParams] = useSearchParams()
  const requestedMonth = searchParams.get(MONTH_PARAM) ?? undefined
  // Without ?ay=, start at the latest month with data, like the dashboard (same cached query).
  const latest = useMonthlyReport(undefined)
  const month = requestedMonth ?? latest.data?.month
  const daily = useDailySpending(month)
  const [selectedDay, setSelectedDay] = useState<string | null>(null)

  if (!month) {
    return latest.isError ? <ErrorAlert>{errorMessage(latest.error)}</ErrorAlert> : <PageLoader />
  }

  const amounts = new Map(daily.data?.days.map((day) => [day.date, Number(day.amount)]))
  const max = Math.max(0, ...amounts.values())
  const today = todayIso()
  const shownDay = selectedDay?.startsWith(month) ? selectedDay : null

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div aria-hidden className="flex items-center gap-2 text-xs text-fg-subtle">
          Az
          {[1, 2, 3, 4].map((level) => (
            <span
              key={level}
              className="size-4 rounded ring-1 ring-line"
              style={{ backgroundColor: heatColor(level) }}
            />
          ))}
          Çok harcama
        </div>
        <MonthPicker
          month={month}
          onChange={(next) => {
            setSelectedDay(null)
            setSearchParams({ [MONTH_PARAM]: next })
          }}
        />
      </div>

      {daily.isError && <ErrorAlert>{errorMessage(daily.error)}</ErrorAlert>}

      <div className="grid items-start gap-4 lg:grid-cols-[2fr_1fr]">
        <Card className="p-2 sm:p-4">
          <table className="w-full table-fixed border-separate border-spacing-1">
            <thead>
              <tr>
                {WEEKDAYS.map((weekday) => (
                  <th key={weekday} className="pb-1 text-xs font-medium text-fg-subtle">
                    {weekday}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {monthGrid(month).map((week, index) => (
                <tr key={index}>
                  {week.map((day, dayIndex) => {
                    if (!day) return <td key={dayIndex} />
                    const amount = amounts.get(day) ?? 0
                    const selected = day === shownDay
                    return (
                      <td key={day} className="p-0">
                        <button
                          type="button"
                          onClick={() => setSelectedDay(day)}
                          aria-pressed={selected}
                          aria-label={`${formatDate(day)}: ${amount > 0 ? formatCurrency(amount) + ' harcama' : 'harcama yok'}`}
                          className={`flex h-14 w-full flex-col items-start justify-between rounded-lg p-1.5 text-left ring-1 transition-shadow hover:ring-2 hover:ring-emerald-500 sm:h-20 sm:p-2 ${
                            selected ? 'ring-2 ring-emerald-600' : 'ring-line'
                          }`}
                          style={{ backgroundColor: heatColor(heatLevel(amount, max)) }}
                        >
                          <span
                            className={`text-xs font-medium ${day === today ? 'rounded-full bg-emerald-600 px-1.5 text-white' : 'text-fg-secondary'}`}
                          >
                            {Number(day.slice(8))}
                          </span>
                          {amount > 0 && (
                            <span className="hidden w-full truncate text-xs font-semibold text-fg tabular-nums sm:block">
                              {formatCurrencyCompact(amount)}
                            </span>
                          )}
                        </button>
                      </td>
                    )
                  })}
                </tr>
              ))}
            </tbody>
          </table>
        </Card>

        {shownDay ? (
          <DayPanel day={shownDay} />
        ) : (
          <Card>
            <p className="text-sm text-fg-subtle">İşlemlerini görmek için bir güne tıkla.</p>
          </Card>
        )}
      </div>
    </div>
  )
}
