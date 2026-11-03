import { useState } from 'react'
import type { Category, CategoryCreate, CategoryKind } from '../../api/types.ts'
import { KIND_LABELS, KIND_ORDER } from '../../lib/categories.ts'
import { CATEGORY_ICONS, CategoryIcon } from '../CategoryIcon.tsx'
import { ErrorAlert } from '../ui/Alert.tsx'
import { Button } from '../ui/Button.tsx'
import { Dialog } from '../ui/Dialog.tsx'
import { TextField } from '../ui/TextField.tsx'

// Tailwind 600 shades: all keep the white icon on the chip readable.
const COLORS = [
  '#dc2626',
  '#ea580c',
  '#d97706',
  '#65a30d',
  '#16a34a',
  '#0d9488',
  '#0891b2',
  '#2563eb',
  '#4f46e5',
  '#9333ea',
  '#db2777',
  '#475569',
]

const KIND_HINTS: Record<CategoryKind, string> = {
  expense: 'Harcamalara eklenir; iadeler harcamadan düşülür.',
  income: 'Gelire eklenir (ör. maaş, serbest çalışma).',
  transfer: 'Raporlara girmez (ör. kendi hesapların arası para aktarımı).',
}

interface CategoryFormDialogProps {
  open: boolean
  /** Edit this category; create a new one when null. */
  category: Category | null
  saving: boolean
  error: string | null
  onSave(values: CategoryCreate): void
  onClose(): void
}

export function CategoryFormDialog({ open, category, ...props }: CategoryFormDialogProps) {
  return (
    <Dialog
      open={open}
      title={category ? 'Kategoriyi düzenle' : 'Yeni kategori'}
      onClose={props.onClose}
    >
      {open && <CategoryForm key={category?.id ?? 'new'} category={category} {...props} />}
    </Dialog>
  )
}

function CategoryForm({
  category,
  saving,
  error,
  onSave,
  onClose,
}: Omit<CategoryFormDialogProps, 'open'>) {
  const [name, setName] = useState(category?.name ?? '')
  const [kind, setKind] = useState<CategoryKind>(category?.kind ?? 'expense')
  const [color, setColor] = useState(category?.color ?? COLORS[7])
  const [icon, setIcon] = useState(category?.icon ?? 'tag')
  const nameMissing = name.trim() === ''

  return (
    <form
      onSubmit={(event) => {
        event.preventDefault()
        if (!nameMissing) onSave({ name: name.trim(), kind, color, icon })
      }}
      className="space-y-5"
    >
      <div className="flex items-end gap-3">
        <CategoryIcon icon={icon} color={color} className="size-10" />
        <TextField
          label="Ad"
          className="flex-1"
          value={name}
          maxLength={50}
          onChange={(event) => setName(event.target.value)}
          autoFocus
        />
      </div>

      <fieldset>
        <legend className="mb-2 text-sm font-medium text-fg-secondary">Tür</legend>
        <div className="grid grid-cols-3 gap-2">
          {KIND_ORDER.map((value) => (
            <label
              key={value}
              className={`cursor-pointer rounded-lg px-3 py-2 text-center text-sm font-medium ring-1 transition-colors has-[:focus-visible]:outline-2 has-[:focus-visible]:outline-emerald-600 ${
                kind === value
                  ? 'bg-accent-soft text-accent-fg ring-emerald-500'
                  : 'text-fg-muted ring-line-strong hover:bg-surface-muted'
              }`}
            >
              <input
                type="radio"
                name="kind"
                value={value}
                checked={kind === value}
                onChange={() => setKind(value)}
                className="sr-only"
              />
              {KIND_LABELS[value]}
            </label>
          ))}
        </div>
        <p className="mt-2 text-xs text-fg-subtle">{KIND_HINTS[kind]}</p>
      </fieldset>

      <fieldset>
        <legend className="mb-2 text-sm font-medium text-fg-secondary">Renk</legend>
        <div className="flex flex-wrap gap-2">
          {COLORS.map((value) => (
            <label key={value} className="cursor-pointer">
              <input
                type="radio"
                name="color"
                value={value}
                checked={color === value}
                onChange={() => setColor(value)}
                aria-label={value}
                className="peer sr-only"
              />
              <span
                aria-hidden
                className="block size-7 rounded-full ring-offset-2 ring-offset-surface peer-checked:ring-2 peer-checked:ring-fg peer-focus-visible:ring-2 peer-focus-visible:ring-emerald-500"
                style={{ backgroundColor: value }}
              />
            </label>
          ))}
        </div>
      </fieldset>

      <fieldset>
        <legend className="mb-2 text-sm font-medium text-fg-secondary">İkon</legend>
        <div className="grid grid-cols-7 gap-1.5">
          {Object.entries(CATEGORY_ICONS).map(([value, Icon]) => (
            <label
              key={value}
              className={`flex cursor-pointer items-center justify-center rounded-lg p-2 transition-colors has-[:focus-visible]:outline-2 has-[:focus-visible]:outline-emerald-600 ${
                icon === value
                  ? 'bg-accent-soft text-accent-fg'
                  : 'text-fg-muted hover:bg-surface-muted'
              }`}
            >
              <input
                type="radio"
                name="icon"
                value={value}
                checked={icon === value}
                onChange={() => setIcon(value)}
                aria-label={value}
                className="sr-only"
              />
              <Icon aria-hidden className="size-5" />
            </label>
          ))}
        </div>
      </fieldset>

      {error && <ErrorAlert>{error}</ErrorAlert>}

      <div className="flex justify-end gap-3">
        <Button variant="secondary" onClick={onClose} disabled={saving}>
          Vazgeç
        </Button>
        <Button type="submit" loading={saving} disabled={nameMissing}>
          Kaydet
        </Button>
      </div>
    </form>
  )
}
