import { Upload } from 'lucide-react'
import { Link, useSearchParams } from 'react-router'
import { useMonthlyReport, useTopMerchants, useTrend } from '../api/reports.ts'
import { CategoryBreakdown } from '../components/dashboard/CategoryBreakdown.tsx'
import { MonthPicker } from '../components/dashboard/MonthPicker.tsx'
import { StatTile } from '../components/dashboard/StatTile.tsx'
import { TopMerchantsList } from '../components/dashboard/TopMerchantsList.tsx'
import { TrendChart } from '../components/dashboard/TrendChart.tsx'
import { ErrorAlert } from '../components/ui/Alert.tsx'
import { Card } from '../components/ui/Card.tsx'
import { PageLoader } from '../components/ui/Spinner.tsx'
import { errorMessage } from '../lib/errors.ts'

const MONTH_PARAM = 'ay'

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
  const [searchParams, setSearchParams] = useSearchParams()
  // Without ?ay= the API picks the latest month with data; the URL keeps a chosen month
  // so a reload or a shared link shows the same month.
  const requestedMonth = searchParams.get(MONTH_PARAM) ?? undefined
  const report = useMonthlyReport(requestedMonth)
  const month = requestedMonth ?? report.data?.month
  const trend = useTrend(month)
  const merchants = useTopMerchants(month)

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
        />
      </div>

      {isEmpty ? (
        <EmptyState />
      ) : (
        <>
          <section aria-label="Aylık özet" className="mt-6 grid gap-4 sm:grid-cols-3">
            <StatTile
              label="Gelir"
              amount={data.income}
              changePct={data.income_change_pct}
              goodWhen="up"
            />
            <StatTile
              label="Gider"
              amount={data.expense}
              changePct={data.expense_change_pct}
              goodWhen="down"
            />
            <StatTile label="Net" amount={data.net} changePct={data.net_change_pct} goodWhen="up" />
          </section>

          <div className="mt-4 grid gap-4 lg:grid-cols-5">
            <div className="lg:col-span-3">
              {trend.data ? (
                <TrendChart months={trend.data.months} />
              ) : (
                <Card className="h-80">
                  {trend.isError && <ErrorAlert>{errorMessage(trend.error)}</ErrorAlert>}
                </Card>
              )}
            </div>
            <div className="lg:col-span-2">
              {merchants.data ? (
                <TopMerchantsList merchants={merchants.data.merchants} />
              ) : (
                <Card className="h-80" />
              )}
            </div>
          </div>

          <div className="mt-4">
            <CategoryBreakdown categories={data.categories} />
          </div>
        </>
      )}
    </>
  )
}
