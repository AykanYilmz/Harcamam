import { ChevronLeft, ChevronRight } from 'lucide-react'
import { formatDateRange, formatMonth, shiftMonth } from '../../lib/format.ts'
import { periodMonthOf } from '../../lib/periods.ts'

interface MonthPickerProps {
  month: string
  onChange(month: string): void
  /** The latest month that can be chosen; defaults to the current calendar month. */
  latest?: string
  /** The days `month` covers, shown under its name when it isn't a calendar month. */
  range?: { start: string; end: string }
}

export function MonthPicker({ month, onChange, latest, range }: MonthPickerProps) {
  const isFuture = shiftMonth(month, 1) > (latest ?? periodMonthOf(new Date(), null))
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
      <span aria-live="polite" className="flex min-w-28 flex-col items-center px-1 text-center">
        <span className="text-sm font-medium text-fg">{formatMonth(month)}</span>
        {range && (
          <span className="text-xs text-fg-subtle">{formatDateRange(range.start, range.end)}</span>
        )}
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
