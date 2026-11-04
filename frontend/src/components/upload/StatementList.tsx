import { FileText, Trash2 } from 'lucide-react'
import { useState } from 'react'
import { useDeleteStatement, useStatements } from '../../api/statements.ts'
import type { Statement } from '../../api/types.ts'
import { errorMessage } from '../../lib/errors.ts'
import { formatCurrency, formatDate } from '../../lib/format.ts'
import { ErrorAlert } from '../ui/Alert.tsx'
import { Card } from '../ui/Card.tsx'
import { ConfirmDialog } from '../ui/ConfirmDialog.tsx'
import { Spinner } from '../ui/Spinner.tsx'

export function StatementList() {
  const statements = useStatements()
  const deleteStatement = useDeleteStatement()
  const [toDelete, setToDelete] = useState<Statement | null>(null)

  function confirmDelete() {
    if (!toDelete) return
    deleteStatement.mutate(toDelete.id, { onSuccess: () => setToDelete(null) })
  }

  return (
    <Card className="mt-8">
      <h2 className="font-semibold text-fg">Yüklenen ekstreler</h2>

      {statements.isPending && <Spinner className="mt-4 size-6 text-fg-subtle" />}
      {statements.isError && (
        <div className="mt-4">
          <ErrorAlert>{errorMessage(statements.error)}</ErrorAlert>
        </div>
      )}
      {statements.data?.length === 0 && (
        <p className="mt-4 text-sm text-fg-subtle">Henüz bir ekstre yüklemedin.</p>
      )}

      {statements.data && statements.data.length > 0 && (
        <ul className="mt-2 divide-y divide-line">
          {statements.data.map((statement) => (
            <li key={statement.id} className="flex items-center gap-3 py-3">
              <FileText aria-hidden className="size-5 shrink-0 text-fg-faint" />
              <div className="min-w-0 flex-1">
                <p className="truncate text-sm font-medium text-fg">{statement.file_name}</p>
                <p className="text-xs text-fg-subtle">
                  {formatDate(statement.period_start)} – {formatDate(statement.period_end)} ·{' '}
                  {statement.transaction_count} işlem · {formatDate(statement.uploaded_at)}{' '}
                  tarihinde yüklendi
                </p>
                {/* As printed on the statement, so it can be checked against the bank's total. */}
                <p className="mt-0.5 text-xs text-fg-muted tabular-nums">
                  <span className="font-medium text-fg">{formatCurrency(statement.money_out)}</span>{' '}
                  çıkış · {formatCurrency(statement.money_in)} giriş
                </p>
              </div>
              <button
                type="button"
                onClick={() => setToDelete(statement)}
                aria-label={`${statement.file_name} ekstresini sil`}
                title="Sil"
                className="rounded-lg p-2 text-fg-subtle hover:bg-danger-soft hover:text-danger-fg"
              >
                <Trash2 aria-hidden className="size-4" />
              </button>
            </li>
          ))}
        </ul>
      )}

      <ConfirmDialog
        open={toDelete !== null}
        title="Ekstreyi sil"
        confirmLabel="Sil"
        loading={deleteStatement.isPending}
        onConfirm={confirmDelete}
        onCancel={() => {
          setToDelete(null)
          deleteStatement.reset()
        }}
      >
        <p>
          <strong className="text-fg">{toDelete?.file_name}</strong> ve içindeki{' '}
          {toDelete?.transaction_count} işlem silinecek. Bu işlem geri alınamaz.
        </p>
        {deleteStatement.isError && (
          <div className="mt-3">
            <ErrorAlert>{errorMessage(deleteStatement.error)}</ErrorAlert>
          </div>
        )}
      </ConfirmDialog>
    </Card>
  )
}
