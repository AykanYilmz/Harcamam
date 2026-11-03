import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
  type TooltipContentProps,
} from 'recharts'
import type { DaySpending } from '../../api/types.ts'
import { formatCurrency, formatCurrencyCompact, formatDate } from '../../lib/format.ts'
import { Card } from '../ui/Card.tsx'

interface ChartPoint {
  // 1-based position in the month: with a closing day the month runs e.g. 7 Sep - 6 Oct,
  // so day-of-month numbers repeat and can't be the axis.
  index: number
  day: number
  date: string
  amount: number
}

function DayTooltip({ active, payload }: TooltipContentProps) {
  const point = payload?.[0]?.payload as ChartPoint | undefined
  if (!active || !point) return null
  return (
    <div className="rounded-lg bg-surface px-3 py-2 text-sm shadow-lg ring-1 ring-line">
      <p className="text-xs text-fg-subtle">{formatDate(point.date)}</p>
      <p className="font-semibold text-fg tabular-nums">{formatCurrency(point.amount)}</p>
    </div>
  )
}

/** One column per day of the month. Single series: the title names it, so no legend. */
export function DailySpendingChart({ days }: { days: DaySpending[] }) {
  const data: ChartPoint[] = days.map((day, position) => ({
    index: position + 1,
    day: Number(day.date.slice(8, 10)),
    date: day.date,
    amount: Number(day.amount),
  }))
  const lastDay = data.length
  const total = data.reduce((sum, point) => sum + point.amount, 0)
  const busiest = data.reduce<ChartPoint | null>(
    (best, point) => (point.amount > (best?.amount ?? 0) ? point : best),
    null,
  )

  return (
    <Card className="flex h-full flex-col">
      <h2 className="font-semibold text-fg">Günlük harcama</h2>
      {/* The key figures as text, so nothing depends on reading the chart. */}
      <p className="mt-1 text-sm text-fg-subtle">
        Günlük ortalama{' '}
        <span className="font-medium text-fg">{formatCurrency(total / (lastDay || 1))}</span>
        {busiest && (
          <>
            {' '}
            · En yüksek{' '}
            <span className="font-medium text-fg">
              {formatDate(busiest.date)}, {formatCurrency(busiest.amount)}
            </span>
          </>
        )}
      </p>
      <div className="mt-4 h-56 flex-1" role="img" aria-label="Ayın her günü için harcama grafiği">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data} margin={{ top: 8, right: 8, bottom: 0, left: 0 }}>
            <CartesianGrid vertical={false} stroke="var(--line)" />
            <XAxis
              dataKey="index"
              ticks={[1, 5, 10, 15, 20, 25, lastDay]}
              tickFormatter={(index: number) => String(data[index - 1]?.day ?? '')}
              axisLine={false}
              tickLine={false}
              tick={{ fill: 'var(--fg-subtle)', fontSize: 12 }}
              tickMargin={8}
            />
            <YAxis
              tickFormatter={formatCurrencyCompact}
              axisLine={false}
              tickLine={false}
              tick={{ fill: 'var(--fg-subtle)', fontSize: 12 }}
              width={72}
            />
            <Tooltip content={DayTooltip} cursor={{ fill: 'var(--surface-muted)' }} />
            <Bar
              dataKey="amount"
              fill="var(--chart-expense)"
              radius={[4, 4, 0, 0]}
              maxBarSize={24}
              isAnimationActive={false}
            />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </Card>
  )
}
