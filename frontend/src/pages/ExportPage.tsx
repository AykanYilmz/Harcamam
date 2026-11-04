import { FileSpreadsheet, FileText, Printer } from 'lucide-react'
import { useState } from 'react'
import { Link } from 'react-router'
import { useExportTransactions, type ExportFormat } from '../api/exports.ts'
import { useMonthlyReport } from '../api/reports.ts'
import { useAuth } from '../auth/useAuth.ts'
import { ErrorAlert } from '../components/ui/Alert.tsx'
import { Button } from '../components/ui/Button.tsx'
import { Card } from '../components/ui/Card.tsx'
import { PageLoader } from '../components/ui/Spinner.tsx'
import { TextField } from '../components/ui/TextField.tsx'
import { errorMessage } from '../lib/errors.ts'
import { shiftMonth } from '../lib/format.ts'
import { periodRange } from '../lib/periods.ts'
import { isoDate } from '../lib/transactionFilters.ts'

const PRESETS = [1, 3, 6, 12]
const EXPORT_ERRORS = { 422: 'Bitiş tarihi başlangıçtan önce olamaz; en fazla üç yıl seçilebilir.' }

/** The `months` months up to and including `latest`, as the reports count them. */
function lastMonths(latest: string, months: number, endDay: number | null) {
  return {
    start: isoDate(periodRange(shiftMonth(latest, -(months - 1)), endDay).start),
    end: isoDate(periodRange(latest, endDay).end),
  }
}

function ExportForm({ latest, endDay }: { latest: string; endDay: number | null }) {
  const [range, setRange] = useState(() => lastMonths(latest, 6, endDay))
  const exporter = useExportTransactions()
  const running = exporter.isPending ? exporter.variables.format : null

  function download(format: ExportFormat) {
    exporter.mutate({ format, ...range })
  }

  return (
    <Card>
      <h2 className="font-semibold text-fg">İşlemleri dışa aktar</h2>
      <p className="mt-1 text-sm text-fg-subtle">
        Excel dosyasında işlemlerin yanında aylık özet ve kategori toplamları da ayrı sayfalarda
        olur. CSV yalnızca işlemleri içerir; Excel, Google E-Tablolar ya da başka bir uygulamada
        açılabilir.
      </p>

      <div className="mt-4 flex flex-wrap gap-2" role="group" aria-label="Hazır aralıklar">
        {PRESETS.map((months) => (
          <button
            key={months}
            type="button"
            onClick={() => setRange(lastMonths(latest, months, endDay))}
            className="rounded-lg px-3 py-1.5 text-sm font-medium text-fg-muted ring-1 ring-line-strong hover:bg-surface-muted hover:text-fg"
          >
            Son {months} ay
          </button>
        ))}
      </div>

      <div className="mt-4 grid gap-4 sm:grid-cols-2">
        <TextField
          label="Başlangıç"
          type="date"
          value={range.start}
          onChange={(event) => setRange({ ...range, start: event.target.value })}
        />
        <TextField
          label="Bitiş"
          type="date"
          value={range.end}
          onChange={(event) => setRange({ ...range, end: event.target.value })}
        />
      </div>

      <div className="mt-5 flex flex-wrap gap-3">
        <Button
          onClick={() => download('xlsx')}
          loading={running === 'xlsx'}
          disabled={running !== null || !range.start || !range.end}
        >
          <FileSpreadsheet aria-hidden className="size-4" />
          Excel indir
        </Button>
        <Button
          variant="secondary"
          onClick={() => download('csv')}
          loading={running === 'csv'}
          disabled={running !== null || !range.start || !range.end}
        >
          <FileText aria-hidden className="size-4" />
          CSV indir
        </Button>
      </div>
      {exporter.isError && (
        <div className="mt-4">
          <ErrorAlert>{errorMessage(exporter.error, EXPORT_ERRORS)}</ErrorAlert>
        </div>
      )}
    </Card>
  )
}

export function ExportPage() {
  const { user } = useAuth()
  const latest = useMonthlyReport(undefined)

  if (latest.isPending) return <PageLoader />
  if (latest.isError) return <ErrorAlert>{errorMessage(latest.error)}</ErrorAlert>

  return (
    <div className="mx-auto max-w-2xl space-y-4">
      <ExportForm latest={latest.data.month} endDay={user?.period_end_day ?? null} />
      <Card className="flex items-start gap-3">
        <Printer aria-hidden className="mt-0.5 size-5 shrink-0 text-fg-subtle" />
        <div>
          <h2 className="font-semibold text-fg">PDF rapor</h2>
          <p className="mt-1 text-sm text-fg-subtle">
            Grafiklerle birlikte bir rapor için{' '}
            <Link to="/raporlar" className="font-medium text-accent-fg hover:underline">
              Raporlar
            </Link>{' '}
            sayfasındaki "Yazdır / PDF" düğmesini kullan; yazdırma penceresinde hedef olarak "PDF
            olarak kaydet"i seç.
          </p>
        </div>
      </Card>
    </div>
  )
}
