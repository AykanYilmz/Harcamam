import { Printer } from 'lucide-react'
import { useCategoryTrend, useLongTrend, useMonthlyReport } from '../api/reports.ts'
import type { MonthTotals } from '../api/types.ts'
import { TrendChart } from '../components/dashboard/TrendChart.tsx'
import { CategoryHeatmap } from '../components/reports/CategoryHeatmap.tsx'
import { ErrorAlert } from '../components/ui/Alert.tsx'
import { AnimatedNumber } from '../components/ui/AnimatedNumber.tsx'
import { Card } from '../components/ui/Card.tsx'
import { PageLoader } from '../components/ui/Spinner.tsx'
import { errorMessage } from '../lib/errors.ts'
import { formatCurrency, formatMonth, formatPercent } from '../lib/format.ts'
import { usePersistentState } from '../lib/usePersistentState.ts'

const PERIODS = [6, 12, 24]

function PeriodSummary({ months }: { months: MonthTotals[] }) {
  // Display only: the per-month amounts are already computed exactly by the API.
  const income = months.reduce((sum, month) => sum + Number(month.income), 0)
  const expense = months.reduce((sum, month) => sum + Number(month.expense), 0)
  const net = income - expense
  const tiles = [
    { label: 'Toplam gelir', value: income, format: formatCurrency },
    { label: 'Toplam gider', value: expense, format: formatCurrency },
    { label: 'Aylık ortalama gider', value: expense / months.length, format: formatCurrency },
    {
      label: 'Tasarruf oranı',
      value: income > 0 ? (net / income) * 100 : null,
      format: formatPercent,
      hint: 'Gelirin harcanmayan kısmı',
    },
  ]

  return (
    <section aria-label="Dönem özeti" className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
      {tiles.map((tile) => (
        <Card key={tile.label}>
          <p className="text-sm font-medium text-fg-subtle">{tile.label}</p>
          <p className="mt-1 text-xl font-semibold text-fg tabular-nums">
            {tile.value === null ? '–' : <AnimatedNumber value={tile.value} format={tile.format} />}
          </p>
          {tile.hint && <p className="mt-1 text-xs text-fg-subtle">{tile.hint}</p>}
        </Card>
      ))}
    </section>
  )
}

export function ReportsPage() {
  const [period, setPeriod] = usePersistentState('hesapkitap.reportMonths', 12)
  const latest = useMonthlyReport(undefined)
  const end = latest.data?.month
  const trend = useLongTrend(end, period)
  const categories = useCategoryTrend(end, period)

  const error = latest.error ?? trend.error ?? categories.error
  if (error) return <ErrorAlert>{errorMessage(error)}</ErrorAlert>
  if (!end || !trend.data || !categories.data) return <PageLoader />

  const months = trend.data.months

  return (
    <div className="space-y-4">
      {/* Only on paper, where the app bar with the page title isn't printed. */}
      <h1 className="hidden text-xl font-semibold text-fg print:block">
        HesapKitap raporu · {formatMonth(months[0].month)} – {formatMonth(end)}
      </h1>
      <div className="flex flex-wrap items-center justify-between gap-3 print:hidden">
        <p className="text-sm text-fg-subtle">
          {formatMonth(months[0].month)} – {formatMonth(end)}
        </p>
        <div className="flex flex-wrap items-center gap-2">
          <button
            type="button"
            onClick={() => window.print()}
            className="inline-flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-sm font-medium text-fg-muted ring-1 ring-line-strong hover:bg-surface-muted hover:text-fg"
          >
            <Printer aria-hidden className="size-4" />
            Yazdır / PDF
          </button>
          <div
            role="radiogroup"
            aria-label="Dönem"
            className="inline-flex rounded-lg bg-surface-muted p-1"
          >
            {PERIODS.map((value) => (
              <button
                key={value}
                type="button"
                role="radio"
                aria-checked={period === value}
                onClick={() => setPeriod(value)}
                className={`rounded-md px-3 py-1 text-sm font-medium transition-colors ${
                  period === value ? 'bg-surface text-fg shadow-sm' : 'text-fg-subtle hover:text-fg'
                }`}
              >
                {value} ay
              </button>
            ))}
          </div>
        </div>
      </div>

      <PeriodSummary months={months} />
      <TrendChart months={months} />
      <CategoryHeatmap report={categories.data} />
    </div>
  )
}
