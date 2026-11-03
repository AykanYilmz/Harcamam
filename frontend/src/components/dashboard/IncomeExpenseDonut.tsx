import { Cell, Pie, PieChart, ResponsiveContainer } from 'recharts'
import { formatCurrency, formatPercent } from '../../lib/format.ts'
import { AnimatedNumber } from '../ui/AnimatedNumber.tsx'
import { Card } from '../ui/Card.tsx'

interface IncomeExpenseDonutProps {
  income: string
  expense: string
  net: string
}

const SLICES = [
  { key: 'income', label: 'Gelir', color: 'var(--chart-income)' },
  { key: 'expense', label: 'Gider', color: 'var(--chart-expense)' },
] as const

/** This month's income against spending, with the net in the middle. */
export function IncomeExpenseDonut({ income, expense, net }: IncomeExpenseDonutProps) {
  const values = { income: Number(income), expense: Number(expense) }
  // A month with more refunds than spending has negative spending: nothing to draw.
  const data = SLICES.map((slice) => ({ ...slice, value: Math.max(values[slice.key], 0) }))
  const hasData = data.some((slice) => slice.value > 0)
  const spentShare = values.income > 0 ? (values.expense / values.income) * 100 : null
  const netNegative = Number(net) < 0

  return (
    <Card className="flex h-full flex-col">
      <h2 className="font-semibold text-fg">Bu ay</h2>
      <div className="mt-2 flex flex-1 flex-col items-center gap-4 sm:flex-row lg:flex-col xl:flex-row">
        <div className="relative size-44 shrink-0">
          {hasData && (
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={data}
                  dataKey="value"
                  nameKey="label"
                  innerRadius="72%"
                  outerRadius="100%"
                  startAngle={90}
                  endAngle={-270}
                  paddingAngle={3}
                  cornerRadius={4}
                  stroke="none"
                  isAnimationActive={false}
                >
                  {data.map((slice) => (
                    <Cell key={slice.key} fill={slice.color} />
                  ))}
                </Pie>
              </PieChart>
            </ResponsiveContainer>
          )}
          <div className="absolute inset-0 flex flex-col items-center justify-center text-center">
            <span className="text-xs text-fg-subtle">Elde kalan</span>
            <span
              className={`text-lg font-semibold tabular-nums ${netNegative ? 'text-danger-fg' : 'text-accent-fg'}`}
            >
              <AnimatedNumber value={Number(net)} format={formatCurrency} />
            </span>
          </div>
        </div>

        <div className="w-full space-y-3">
          {SLICES.map((slice) => (
            <div key={slice.key} className="flex items-center gap-2 text-sm">
              <span
                aria-hidden
                className="size-2.5 rounded-full"
                style={{ backgroundColor: slice.color }}
              />
              <span className="text-fg-muted">{slice.label}</span>
              <span className="ml-auto font-semibold text-fg tabular-nums">
                <AnimatedNumber value={values[slice.key]} format={formatCurrency} />
              </span>
            </div>
          ))}
          {spentShare !== null && (
            <p className="border-t border-line pt-3 text-sm text-fg-subtle">
              Harcama / gelir oranı:{' '}
              <span className="font-semibold text-fg">{formatPercent(spentShare)}</span>
            </p>
          )}
        </div>
      </div>
    </Card>
  )
}
