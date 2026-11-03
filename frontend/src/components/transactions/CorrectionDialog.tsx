import { useState } from 'react'
import type { Category, Transaction } from '../../api/types.ts'
import { suggestKeyword } from '../../lib/text.ts'
import { ErrorAlert } from '../ui/Alert.tsx'
import { Button } from '../ui/Button.tsx'
import { Dialog } from '../ui/Dialog.tsx'
import { TextField } from '../ui/TextField.tsx'

export interface PendingCorrection {
  transaction: Transaction
  category: Category
}

interface CorrectionDialogProps {
  correction: PendingCorrection | null
  saving: boolean
  error: string | null
  onSave(ruleKeyword: string | null): void
  onCancel(): void
}

/** Confirms a category change and offers to teach it as a rule for similar transactions. */
export function CorrectionDialog({ correction, ...props }: CorrectionDialogProps) {
  return (
    <Dialog open={correction !== null} title="Kategoriyi değiştir" onClose={props.onCancel}>
      {/* Keyed so the form starts fresh for each transaction. */}
      {correction && (
        <CorrectionForm key={correction.transaction.id} correction={correction} {...props} />
      )}
    </Dialog>
  )
}

function CorrectionForm({
  correction,
  saving,
  error,
  onSave,
  onCancel,
}: Omit<CorrectionDialogProps, 'correction'> & { correction: PendingCorrection }) {
  const { transaction, category } = correction
  const [saveRule, setSaveRule] = useState(true)
  const [keyword, setKeyword] = useState(() => suggestKeyword(transaction.description))
  const keywordMissing = saveRule && keyword.trim() === ''

  return (
    <form
      onSubmit={(event) => {
        event.preventDefault()
        if (!keywordMissing) onSave(saveRule ? keyword.trim() : null)
      }}
    >
      <p>
        <strong className="text-fg">{transaction.description}</strong> işlemi{' '}
        <strong className="text-fg">{category.name}</strong> kategorisine taşınacak.
      </p>

      <label className="mt-4 flex items-start gap-2 text-fg">
        <input
          type="checkbox"
          checked={saveRule}
          onChange={(event) => setSaveRule(event.target.checked)}
          className="mt-1 accent-emerald-600"
        />
        <span>Benzer işlemler için kural olarak kaydet</span>
      </label>

      {saveRule && (
        <TextField
          label="Anahtar kelime"
          className="mt-3"
          value={keyword}
          onChange={(event) => setKeyword(event.target.value)}
          error={keywordMissing ? 'Bir anahtar kelime girin.' : undefined}
          hint={`Açıklamasında "${keyword.trim() || '…'}" geçen işlemler ${category.name} olur. Elle düzelttiklerine dokunulmaz.`}
        />
      )}

      {error && (
        <div className="mt-4">
          <ErrorAlert>{error}</ErrorAlert>
        </div>
      )}

      <div className="mt-6 flex justify-end gap-3">
        <Button variant="secondary" onClick={onCancel} disabled={saving}>
          Vazgeç
        </Button>
        <Button type="submit" loading={saving} disabled={keywordMissing}>
          Kaydet
        </Button>
      </div>
    </form>
  )
}
