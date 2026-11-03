import { useUpdateSettings } from '../../api/account.ts'
import type { User } from '../../api/types.ts'
import { errorMessage } from '../../lib/errors.ts'
import { formatDateRange, formatMonth } from '../../lib/format.ts'
import { periodMonthOf, periodRange } from '../../lib/periods.ts'
import { ErrorAlert } from '../ui/Alert.tsx'
import { Card } from '../ui/Card.tsx'
import { SelectField } from '../ui/SelectField.tsx'

// 31 is left out: a month ending on the 31st (or its last day) is the calendar month.
const CLOSING_DAYS = Array.from({ length: 30 }, (_, index) => index + 1)

/** Which day the user's months end on, e.g. their credit card's statement closing day. */
export function PeriodSection({ user }: { user: User }) {
  const update = useUpdateSettings()
  // Shown right away while saving, so the example below follows the choice.
  const endDay = update.isPending ? (update.variables.periodEndDay ?? null) : user.period_end_day
  const month = periodMonthOf(new Date(), endDay)
  const { start, end } = periodRange(month, endDay)

  return (
    <Card>
      <h2 className="font-semibold text-fg">Dönem</h2>
      <p className="mt-1 text-sm text-fg-subtle">
        Özet ve Raporlar ayları buna göre hesaplar. Kredi kartının hesap kesim gününü seçersen
        harcamaların ekstrendeki aya düşer.
      </p>

      <SelectField
        label="Ay ne zaman bitsin?"
        className="mt-4 max-w-sm"
        value={endDay ?? ''}
        disabled={update.isPending}
        onChange={(event) =>
          update.mutate({ periodEndDay: event.target.value ? Number(event.target.value) : null })
        }
      >
        <option value="">Takvim ayı (ayın son günü)</option>
        {CLOSING_DAYS.map((day) => (
          <option key={day} value={day}>
            Her ayın {day}. günü
          </option>
        ))}
      </SelectField>

      <p className="mt-3 text-sm text-fg-muted">
        {formatMonth(month)} dönemi:{' '}
        <span className="font-medium text-fg">{formatDateRange(start, end)}</span>
      </p>
      {endDay && endDay > 28 && (
        <p className="mt-1 text-xs text-fg-subtle">
          Bu gün olmayan aylarda dönem ayın son gününde biter.
        </p>
      )}

      {update.isError && (
        <div className="mt-3">
          <ErrorAlert>{errorMessage(update.error)}</ErrorAlert>
        </div>
      )}
    </Card>
  )
}
