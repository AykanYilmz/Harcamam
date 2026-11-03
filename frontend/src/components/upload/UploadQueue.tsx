import { CircleAlert, CircleCheck, FileText } from 'lucide-react'
import { Link } from 'react-router'
import type { StatementImportResult } from '../../api/types.ts'
import { UNCATEGORIZED_PATH } from '../navigation.ts'
import { Spinner } from '../ui/Spinner.tsx'

export type UploadItem =
  | { id: number; fileName: string; status: 'waiting' | 'uploading' }
  | { id: number; fileName: string; status: 'done'; result: StatementImportResult }
  | { id: number; fileName: string; status: 'failed'; message: string }

function ResultText({ result }: { result: StatementImportResult }) {
  const skipped = result.skipped_duplicates
  return (
    <>
      {result.imported} işlem eklendi
      {skipped > 0 && `, ${skipped} işlem zaten kayıtlı olduğu için atlandı`}.
      {result.uncategorized > 0 && (
        <>
          {' '}
          {result.uncategorized} işlem tanınmadı.{' '}
          <Link to={UNCATEGORIZED_PATH} className="font-medium text-accent-fg hover:underline">
            Kategorize et
          </Link>
        </>
      )}
    </>
  )
}

export function UploadQueue({ items }: { items: UploadItem[] }) {
  if (items.length === 0) return null

  return (
    <ul aria-live="polite" className="mt-4 space-y-2">
      {items.map((item) => (
        <li
          key={item.id}
          className="flex items-start gap-3 rounded-xl bg-surface px-4 py-3 ring-1 ring-line"
        >
          <FileText aria-hidden className="mt-0.5 size-5 shrink-0 text-fg-faint" />
          <div className="min-w-0 flex-1">
            <p className="truncate text-sm font-medium text-fg">{item.fileName}</p>
            <p
              className={`text-sm ${item.status === 'failed' ? 'text-danger-fg' : 'text-fg-subtle'}`}
            >
              {item.status === 'waiting' && 'Sırada bekliyor'}
              {item.status === 'uploading' && 'Yükleniyor ve işlemler okunuyor…'}
              {item.status === 'done' && <ResultText result={item.result} />}
              {item.status === 'failed' && item.message}
            </p>
          </div>
          {item.status === 'uploading' && <Spinner className="mt-0.5 size-5 text-fg-subtle" />}
          {item.status === 'done' && (
            <CircleCheck aria-label="Yüklendi" className="mt-0.5 size-5 text-accent-fg" />
          )}
          {item.status === 'failed' && (
            <CircleAlert aria-label="Yüklenemedi" className="mt-0.5 size-5 text-danger-fg" />
          )}
        </li>
      ))}
    </ul>
  )
}
