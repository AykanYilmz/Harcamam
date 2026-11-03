import { ChevronLeft, ChevronRight } from 'lucide-react'
import { formatMonth, shiftMonth } from '../../lib/format.ts'

function currentMonth(): string {
  const now = new Date()
  return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`
}

export function MonthPicker({ month, onChange }: { month: string; onChange(month: string): void }) {
  const isFuture = shiftMonth(month, 1) > currentMonth()
  const buttonClass =
    'rounded-lg p-2 text-fg-muted hover:bg-surface-muted hover:text-fg disabled:cursor-not-allowed disabled:opacity-40 disabled:hover:bg-transparent'

  return (
    <div className="flex items-center gap-1 rounded-xl bg-surface p-1 shadow-sm ring-1 ring-line">
      <button
        type="button"
        onClick={() => onChange(shiftMonth(month, -1))}
        aria-label="Önceki ay"
        className={buttonClass}
      >
        <ChevronLeft aria-hidden className="size-5" />
      </button>
      <span aria-live="polite" className="min-w-28 text-center text-sm font-medium text-fg">
        {formatMonth(month)}
      </span>
      <button
        type="button"
        onClick={() => onChange(shiftMonth(month, 1))}
        disabled={isFuture}
        aria-label="Sonraki ay"
        className={buttonClass}
      >
        <ChevronRight aria-hidden className="size-5" />
      </button>
    </div>
  )
}
