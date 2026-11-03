import { useState } from 'react'
import type { Category } from '../../api/types.ts'
import { CategoryOptions } from '../CategoryOptions.tsx'
import { Button } from '../ui/Button.tsx'
import { selectClass } from '../ui/SelectField.tsx'

interface BulkBarProps {
  count: number
  categories: Category[]
  saving: boolean
  onApply(categoryId: string): void
  onClear(): void
}

/** Shown while transactions are selected: move them all to one category. */
export function BulkBar({ count, categories, saving, onApply, onClear }: BulkBarProps) {
  const [categoryId, setCategoryId] = useState('')

  return (
    <div className="flex flex-wrap items-center gap-3 rounded-xl bg-accent-soft px-4 py-3 ring-1 ring-emerald-500/30">
      <span className="text-sm font-medium text-accent-fg">{count} işlem seçildi</span>
      <select
        value={categoryId}
        onChange={(event) => setCategoryId(event.target.value)}
        aria-label="Seçilen işlemler için kategori"
        className={`${selectClass} w-auto min-w-44`}
      >
        <option value="" disabled>
          Kategori seç…
        </option>
        <CategoryOptions categories={categories} />
      </select>
      <Button onClick={() => onApply(categoryId)} disabled={!categoryId} loading={saving}>
        Uygula
      </Button>
      <Button variant="ghost" onClick={onClear}>
        Seçimi temizle
      </Button>
    </div>
  )
}
