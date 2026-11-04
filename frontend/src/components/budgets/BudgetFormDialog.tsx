import { useState, type FormEvent } from 'react'
import { useCreateBudget, useUpdateBudget } from '../../api/budgets.ts'
import type { Budget, Category } from '../../api/types.ts'
import { parseAmountInput } from '../../lib/amount.ts'
import { errorMessage } from '../../lib/errors.ts'
import { ErrorAlert } from '../ui/Alert.tsx'
import { Button } from '../ui/Button.tsx'
import { Dialog } from '../ui/Dialog.tsx'
import { SelectField } from '../ui/SelectField.tsx'
import { TextField } from '../ui/TextField.tsx'

const SAVE_ERRORS = { 409: 'Bu kategorinin zaten bir bütçesi var.' }

interface BudgetFormDialogProps {
  open: boolean
  /** The budget to change; a new one is added when null. */
  budget: Budget | null
  /** Categories a new budget can be added for (spending ones without a budget yet). */
  available: Category[]
  onClose(): void
}

export function BudgetFormDialog(props: BudgetFormDialogProps) {
  // Remounted each time it opens, so the form starts from the budget being edited.
  return props.open ? <BudgetForm key={props.budget?.id ?? 'new'} {...props} /> : null
}

function BudgetForm({ budget, available, onClose }: BudgetFormDialogProps) {
  const create = useCreateBudget()
  const update = useUpdateBudget()
  const [categoryId, setCategoryId] = useState(available[0]?.id ?? '')
  const [amount, setAmount] = useState(budget ? budget.monthly_limit.replace('.', ',') : '')
  const [amountError, setAmountError] = useState<string | null>(null)
  const saving = create.isPending || update.isPending
  const error = create.error ?? update.error

  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    const monthlyLimit = parseAmountInput(amount)
    if (!monthlyLimit) {
      setAmountError('Sıfırdan büyük bir tutar gir (ör. 8.000 ya da 1.250,50).')
      return
    }
    setAmountError(null)
    const done = { onSuccess: onClose }
    if (budget) update.mutate({ id: budget.id, monthlyLimit }, done)
    else create.mutate({ categoryId, monthlyLimit }, done)
  }

  return (
    <Dialog
      open
      title={budget ? `${budget.name} bütçesi` : 'Bütçe ekle'}
      onClose={onClose}
      footer={
        <>
          <Button variant="secondary" onClick={onClose} disabled={saving}>
            Vazgeç
          </Button>
          <Button type="submit" form="budget-form" loading={saving}>
            Kaydet
          </Button>
        </>
      }
    >
      <form id="budget-form" onSubmit={submit} noValidate className="space-y-4">
        {!budget && (
          <SelectField
            label="Kategori"
            value={categoryId}
            onChange={(event) => setCategoryId(event.target.value)}
          >
            {available.map((category) => (
              <option key={category.id} value={category.id}>
                {category.name}
              </option>
            ))}
          </SelectField>
        )}
        <TextField
          label="Aylık limit (TL)"
          inputMode="decimal"
          autoFocus
          value={amount}
          onChange={(event) => setAmount(event.target.value)}
          error={amountError ?? undefined}
          hint="Her ay için geçerli olur."
        />
        {error && <ErrorAlert>{errorMessage(error, SAVE_ERRORS)}</ErrorAlert>}
      </form>
    </Dialog>
  )
}
