import { useState } from 'react'
import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
  type TooltipContentProps,
} from 'recharts'
import type { MonthTotals } from '../../api/types.ts'
import {
  formatCurrency,
  formatCurrencyCompact,
  formatMonth,
  formatMonthShort,
} from '../../lib/format.ts'
import { Card } from '../ui/Card.tsx'

const SERIES = [
  { key: 'income', label: 'Gelir', color: 'var(--chart-income)' },
  { key: 'expense', label: 'Gider', color: 'var(--chart-expense)' },
] as const

interface ChartPoint {
  month: string
  income: number
  expense: number
}

function LineKey({ color }: { color: string }) {
  return <span aria-hidden className="h-0.5 w-3 rounded-full" style={{ backgroundColor: color }} />
}

/** Every series at the hovered month; the value leads, the series name follows. */
function TrendTooltip({ active, payload, label }: TooltipContentProps) {
  if (!active || !payload?.length) return null
  return (
    <div className="rounded-lg bg-surface px-3 py-2 text-sm shadow-lg ring-1 ring-line">
      <p className="mb-1 text-xs text-fg-subtle">{formatMonth(String(label))}</p>
      {SERIES.map((series) => {
        const value = payload.find((item) => item.dataKey === series.key)?.value
        return (
          <p key={series.key} className="flex items-center gap-2">
            <LineKey color={series.color} />
            <span className="font-semibold text-fg tabular-nums">
              {formatCurrency(Number(value ?? 0))}
            </span>
            <span className="text-fg-subtle">{series.label}</span>
          </p>
        )
      })}
    </div>
  )
}

function TrendTable({ months }: { months: MonthTotals[] }) {
  return (
    <div className="mt-4 overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-line text-left text-fg-subtle">
            <th className="py-2 font-medium">Ay</th>
            <th className="py-2 text-right font-medium">Gelir</th>
            <th className="py-2 text-right font-medium">Gider</th>
            <th className="py-2 text-right font-medium">Net</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-line text-fg tabular-nums">
          {months.map((month) => (
            <tr key={month.month}>
              <td className="py-2">{formatMonth(month.month)}</td>
              <td className="py-2 text-right">{formatCurrency(month.income)}</td>
              <td className="py-2 text-right">{formatCurrency(month.expense)}</td>
              <td className="py-2 text-right">{formatCurrency(month.net)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

export function TrendChart({ months }: { months: MonthTotals[] }) {
  const [showTable, setShowTable] = useState(false)
  const data: ChartPoint[] = months.map((month) => ({
    month: month.month,
    income: Number(month.income),
    expense: Number(month.expense),
  }))

  return (
    <Card>
      <div className="flex flex-wrap items-center justify-between gap-2">
        <h2 className="font-semibold text-fg">Son {months.length} ay</h2>
        <div className="flex items-center gap-4">
          <ul className="flex gap-4 text-sm text-fg-muted" aria-label="Seriler">
            {SERIES.map((series) => (
              <li key={series.key} className="flex items-center gap-2">
                <LineKey color={series.color} />
                {series.label}
              </li>
            ))}
          </ul>
          <button
            type="button"
            onClick={() => setShowTable(!showTable)}
            aria-pressed={showTable}
            className="text-sm font-medium text-accent-fg hover:underline"
          >
            {showTable ? 'Grafik olarak göster' : 'Tablo olarak göster'}
          </button>
        </div>
      </div>

      {showTable ? (
        <TrendTable months={months} />
      ) : (
        <div
          className="mt-4 h-64"
          role="img"
          aria-label={`Son ${months.length} ayın gelir ve gider grafiği. Değerler için tablo görünümünü kullanın.`}
        >
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={data} margin={{ top: 8, right: 8, bottom: 0, left: 0 }}>
              <CartesianGrid vertical={false} stroke="var(--line)" />
              <XAxis
                dataKey="month"
                tickFormatter={formatMonthShort}
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
              <Tooltip
                content={TrendTooltip}
                cursor={{ stroke: 'var(--line-strong)', strokeWidth: 1 }}
              />
              {SERIES.map((series) => (
                <Line
                  key={series.key}
                  dataKey={series.key}
                  name={series.label}
                  type="monotone"
                  stroke={series.color}
                  strokeWidth={2}
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  dot={{ r: 4, fill: series.color, stroke: 'var(--surface)', strokeWidth: 2 }}
                  activeDot={{ r: 5, fill: series.color, stroke: 'var(--surface)', strokeWidth: 2 }}
                  isAnimationActive={false}
                />
              ))}
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}
    </Card>
  )
}
