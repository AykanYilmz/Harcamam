import { Upload } from 'lucide-react'
import { Link, useSearchParams } from 'react-router'
import { useDailySpending, useMonthlyReport, useTopMerchants, useTrend } from '../api/reports.ts'
import { useAuth } from '../auth/useAuth.ts'
import { BudgetAlerts } from '../components/dashboard/BudgetAlerts.tsx'
import { CategoryBreakdown } from '../components/dashboard/CategoryBreakdown.tsx'
import { DailySpendingChart } from '../components/dashboard/DailySpendingChart.tsx'
import { IncomeExpenseDonut } from '../components/dashboard/IncomeExpenseDonut.tsx'
import { MonthPicker } from '../components/dashboard/MonthPicker.tsx'
import { StatTile } from '../components/dashboard/StatTile.tsx'
import { TopMerchantsList } from '../components/dashboard/TopMerchantsList.tsx'
import { TrendChart } from '../components/dashboard/TrendChart.tsx'
import { UncategorizedHint } from '../components/UncategorizedHint.tsx'
import { ErrorAlert } from '../components/ui/Alert.tsx'
import { Card } from '../components/ui/Card.tsx'
import { PageLoader } from '../components/ui/Spinner.tsx'
import { errorMessage } from '../lib/errors.ts'
import { periodMonthOf } from '../lib/periods.ts'

const MONTH_PARAM = 'ay'

/** A card-sized placeholder while a section loads, or its error once it fails. */
function Pending({ error, className = 'h-80' }: { error: unknown; className?: string }) {
  return (
    <Card className={className}>
      {error ? <ErrorAlert>{errorMessage(error)}</ErrorAlert> : null}
    </Card>
  )
}

function EmptyState() {
  return (
    <Card className="mt-6 flex flex-col items-center py-12 text-center">
      <Upload aria-hidden className="size-10 text-fg-faint" />
      <p className="mt-3 font-medium text-fg-secondary">Bu ay için veri yok</p>
      <p className="mt-1 max-w-sm text-sm text-fg-subtle">
        Banka ekstreni yüklediğinde harcamaların burada kategorilere ayrılmış olarak görünecek.
      </p>
      <Link
        to="/yukle"
        className="mt-5 rounded-lg bg-emerald-600 px-4 py-2 text-sm font-medium text-white hover:bg-emerald-700"
      >
        Ekstre yükle
      </Link>
    </Card>
  )
}

export function DashboardPage() {
  const { user } = useAuth()
  const endDay = user?.period_end_day ?? null
  const [searchParams, setSearchParams] = useSearchParams()
  // Without ?ay= the API picks the latest month with data; the URL keeps a chosen month
  // so a reload or a shared link shows the same month.
  const requestedMonth = searchParams.get(MONTH_PARAM) ?? undefined
  const report = useMonthlyReport(requestedMonth)
  const month = requestedMonth ?? report.data?.month
  const trend = useTrend(month)
  const merchants = useTopMerchants(month)
  const daily = useDailySpending(month)

  if (report.isPending) return <PageLoader />
  if (report.isError) return <ErrorAlert>{errorMessage(report.error)}</ErrorAlert>

  const data = report.data
  const isEmpty = data.transaction_count === 0

  return (
    <>
      <div className="flex justify-end">
        <MonthPicker
          month={data.month}
          onChange={(next) => setSearchParams({ [MONTH_PARAM]: next })}
          latest={periodMonthOf(new Date(), endDay)}
          range={endDay ? { start: data.start, end: data.end } : undefined}
        />
      </div>

      {isEmpty ? (
        <EmptyState />
      ) : (
        <>
          <BudgetAlerts month={data.month} className="mt-6" />
          <section aria-label="Aylık özet" className="mt-6 grid gap-4 sm:grid-cols-3">
            <StatTile
              label="Gelir"
              tone="income"
              amount={data.income}
              changePct={data.income_change_pct}
              goodWhen="up"
            />
            <StatTile
              label="Gider"
              tone="expense"
              amount={data.expense}
              changePct={data.expense_change_pct}
              goodWhen="down"
            />
            <StatTile
              label="Elde kalan"
              tone="net"
              amount={data.net}
              changePct={data.net_change_pct}
              goodWhen="up"
            />
          </section>

          <div className="mt-4 grid gap-4 lg:grid-cols-5">
            <div className="lg:col-span-2">
              <IncomeExpenseDonut income={data.income} expense={data.expense} net={data.net} />
            </div>
            <div className="lg:col-span-3">
              {daily.data ? (
                <DailySpendingChart days={daily.data.days} />
              ) : (
                <Pending error={daily.error} />
              )}
            </div>
          </div>

          <div className="mt-4 grid gap-4 lg:grid-cols-5">
            <div className="lg:col-span-3">
              {trend.data ? (
                <TrendChart months={trend.data.months} />
              ) : (
                <Pending error={trend.error} />
              )}
            </div>
            <div className="lg:col-span-2">
              {merchants.data ? (
                <TopMerchantsList merchants={merchants.data.merchants} />
              ) : (
                <Pending error={merchants.error} />
              )}
            </div>
          </div>

          <div className="mt-4">
            <CategoryBreakdown categories={data.categories} month={data.month} />
          </div>
          <UncategorizedHint className="mt-4" />
        </>
      )}
    </>
  )
}
