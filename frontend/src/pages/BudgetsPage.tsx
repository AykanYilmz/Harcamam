import { Plus, Target } from 'lucide-react'
import { useState } from 'react'
import { useSearchParams } from 'react-router'
import { useBudgets, useDeleteBudget } from '../api/budgets.ts'
import { useCategories } from '../api/categories.ts'
import type { Budget } from '../api/types.ts'
import { useAuth } from '../auth/useAuth.ts'
import { BudgetFormDialog } from '../components/budgets/BudgetFormDialog.tsx'
import { BudgetRow } from '../components/budgets/BudgetRow.tsx'
import { MonthPicker } from '../components/dashboard/MonthPicker.tsx'
import { ErrorAlert } from '../components/ui/Alert.tsx'
import { Button } from '../components/ui/Button.tsx'
import { Card } from '../components/ui/Card.tsx'
import { ConfirmDialog } from '../components/ui/ConfirmDialog.tsx'
import { PageLoader } from '../components/ui/Spinner.tsx'
import { errorMessage } from '../lib/errors.ts'
import { formatCurrency } from '../lib/format.ts'
import { periodMonthOf } from '../lib/periods.ts'

const MONTH_PARAM = 'ay'

type FormState = { open: false } | { open: true; budget: Budget | null }

export function BudgetsPage() {
  const { user } = useAuth()
  const endDay = user?.period_end_day ?? null
  const [searchParams, setSearchParams] = useSearchParams()
  const requestedMonth = searchParams.get(MONTH_PARAM) ?? undefined
  const report = useBudgets(requestedMonth)
  const categories = useCategories()
  const remove = useDeleteBudget()
  const [form, setForm] = useState<FormState>({ open: false })
  const [toDelete, setToDelete] = useState<Budget | null>(null)

  if (report.isPending || categories.isPending) return <PageLoader />
  if (report.isError) return <ErrorAlert>{errorMessage(report.error)}</ErrorAlert>
  if (categories.isError) return <ErrorAlert>{errorMessage(categories.error)}</ErrorAlert>

  const data = report.data
  const budgeted = new Set(data.budgets.map((budget) => budget.category_id))
  const available = categories.data.filter((c) => c.kind === 'expense' && !budgeted.has(c.id))
  const totalLimit = Number(data.total_limit)
  const totalSpent = Number(data.total_spent)
  const addButton = (
    <Button onClick={() => setForm({ open: true, budget: null })} disabled={!available.length}>
      <Plus aria-hidden className="size-4" />
      Bütçe ekle
    </Button>
  )

  return (
    <div className="mx-auto max-w-3xl space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        {addButton}
        <MonthPicker
          month={data.month}
          onChange={(next) => setSearchParams({ [MONTH_PARAM]: next })}
          latest={periodMonthOf(new Date(), endDay)}
          range={endDay ? { start: data.start, end: data.end } : undefined}
        />
      </div>

      {data.budgets.length === 0 ? (
        <Card className="flex flex-col items-center py-12 text-center">
          <Target aria-hidden className="size-10 text-fg-faint" />
          <p className="mt-3 font-medium text-fg-secondary">Henüz bütçen yok</p>
          <p className="mt-1 max-w-sm text-sm text-fg-subtle">
            Bir kategori için aylık limit belirle; harcaman limite yaklaşınca ya da aşınca burada ve
            Özet'te uyarı görürsün.
          </p>
        </Card>
      ) : (
        <Card>
          <div className="flex flex-wrap items-baseline justify-between gap-x-4 gap-y-1">
            <h2 className="font-semibold text-fg">Toplam</h2>
            <p className="text-sm text-fg-muted tabular-nums">
              <span className="text-lg font-semibold text-fg">{formatCurrency(totalSpent)}</span> /{' '}
              {formatCurrency(totalLimit)}
            </p>
          </div>
          {data.days_elapsed && (
            <p className="mt-1 text-xs text-fg-subtle">
              Ayın {data.days_elapsed}. günü ({data.days_in_period} günlük dönem); tahminler bu ana
              kadarki harcama hızına göre.
            </p>
          )}
          <ul className="mt-2 divide-y divide-line">
            {data.budgets.map((budget) => (
              <BudgetRow
                key={budget.id}
                budget={budget}
                onEdit={() => setForm({ open: true, budget })}
                onDelete={() => {
                  remove.reset()
                  setToDelete(budget)
                }}
              />
            ))}
          </ul>
        </Card>
      )}

      <BudgetFormDialog
        open={form.open}
        budget={form.open ? form.budget : null}
        available={available}
        onClose={() => setForm({ open: false })}
      />
      <ConfirmDialog
        open={toDelete !== null}
        title="Bütçeyi sil"
        confirmLabel="Sil"
        loading={remove.isPending}
        onCancel={() => setToDelete(null)}
        onConfirm={() =>
          toDelete && remove.mutate(toDelete.id, { onSuccess: () => setToDelete(null) })
        }
      >
        <p>
          <strong>{toDelete?.name}</strong> bütçesi silinecek. Harcamaların ve işlemlerin
          etkilenmez.
        </p>
        {remove.isError && <ErrorAlert>{errorMessage(remove.error)}</ErrorAlert>}
      </ConfirmDialog>
    </div>
  )
}
