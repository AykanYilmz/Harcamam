import { ChevronDown, Search, X } from 'lucide-react'
import type { Category, TransactionSort, TransactionType } from '../../api/types.ts'
import { hasActiveFilters, type TransactionFilters } from '../../lib/transactionFilters.ts'
import { selectClass } from '../ui/SelectField.tsx'

const TYPES: { value: TransactionType | ''; label: string }[] = [
  { value: '', label: 'Tümü' },
  { value: 'expense', label: 'Gider' },
  { value: 'income', label: 'Gelir' },
]

const SORTS: { value: TransactionSort; label: string }[] = [
  { value: 'date_desc', label: 'En yeni' },
  { value: 'date_asc', label: 'En eski' },
  { value: 'amount_desc', label: 'Tutar (yüksek → düşük)' },
  { value: 'amount_asc', label: 'Tutar (düşük → yüksek)' },
]

const inputClass =
  'w-full rounded-lg border border-line-strong bg-surface px-3 py-2 text-sm text-fg shadow-sm focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/30 focus:outline-none'

interface FiltersBarProps {
  filters: TransactionFilters
  categories: Category[]
  onChange(changes: Partial<TransactionFilters>): void
  onClear(): void
}

function CategoryFilter({
  categories,
  selected,
  onChange,
}: {
  categories: Category[]
  selected: string[]
  onChange(ids: string[]): void
}) {
  const label =
    selected.length === 0
      ? 'Tüm kategoriler'
      : selected.length === 1
        ? (categories.find((category) => category.id === selected[0])?.name ?? '1 kategori')
        : `${selected.length} kategori`

  function toggle(id: string) {
    onChange(selected.includes(id) ? selected.filter((item) => item !== id) : [...selected, id])
  }

  return (
    <details className="group relative">
      <summary
        className={`${inputClass} flex cursor-pointer list-none items-center justify-between gap-2`}
      >
        <span className="truncate">{label}</span>
        <ChevronDown
          aria-hidden
          className="size-4 shrink-0 transition-transform group-open:rotate-180"
        />
      </summary>
      <fieldset className="absolute z-10 mt-1 max-h-72 w-full min-w-56 overflow-y-auto rounded-lg bg-surface p-2 shadow-lg ring-1 ring-line">
        <legend className="sr-only">Kategoriler</legend>
        {categories.map((category) => (
          <label
            key={category.id}
            className="flex cursor-pointer items-center gap-2 rounded-md px-2 py-1.5 text-sm text-fg hover:bg-surface-muted"
          >
            <input
              type="checkbox"
              checked={selected.includes(category.id)}
              onChange={() => toggle(category.id)}
              className="accent-emerald-600"
            />
            <span
              aria-hidden
              className="size-2.5 rounded-full"
              style={{ backgroundColor: category.color }}
            />
            {category.name}
          </label>
        ))}
      </fieldset>
    </details>
  )
}

export function TransactionFiltersBar({ filters, categories, onChange, onClear }: FiltersBarProps) {
  return (
    <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-[2fr_1fr_1fr_1.3fr_auto]">
      <div className="relative sm:col-span-2 lg:col-span-1">
        <Search
          aria-hidden
          className="pointer-events-none absolute top-1/2 left-3 size-4 -translate-y-1/2 text-fg-faint"
        />
        <input
          type="search"
          value={filters.query}
          onChange={(event) => onChange({ query: event.target.value })}
          placeholder="Açıklamada ara (ör. migros)"
          aria-label="Açıklamada ara"
          className={`${inputClass} pl-9`}
        />
      </div>
      <input
        type="date"
        value={filters.dateFrom}
        max={filters.dateTo || undefined}
        onChange={(event) => onChange({ dateFrom: event.target.value })}
        aria-label="Başlangıç tarihi"
        className={inputClass}
      />
      <input
        type="date"
        value={filters.dateTo}
        min={filters.dateFrom || undefined}
        onChange={(event) => onChange({ dateTo: event.target.value })}
        aria-label="Bitiş tarihi"
        className={inputClass}
      />
      <CategoryFilter
        categories={categories}
        selected={filters.categoryIds}
        onChange={(categoryIds) => onChange({ categoryIds })}
      />
      <select
        value={filters.sort}
        onChange={(event) => onChange({ sort: event.target.value as TransactionSort })}
        aria-label="Sıralama"
        className={selectClass}
      >
        {SORTS.map((sort) => (
          <option key={sort.value} value={sort.value}>
            {sort.label}
          </option>
        ))}
      </select>

      <div className="flex flex-wrap items-center gap-3 sm:col-span-2 lg:col-span-5">
        <div
          role="radiogroup"
          aria-label="İşlem türü"
          className="inline-flex rounded-lg bg-surface-muted p-1"
        >
          {TYPES.map((type) => (
            <button
              key={type.value}
              type="button"
              role="radio"
              aria-checked={filters.type === type.value}
              onClick={() => onChange({ type: type.value })}
              className={`rounded-md px-3 py-1 text-sm font-medium transition-colors ${
                filters.type === type.value
                  ? 'bg-surface text-fg shadow-sm'
                  : 'text-fg-subtle hover:text-fg'
              }`}
            >
              {type.label}
            </button>
          ))}
        </div>
        {hasActiveFilters(filters) && (
          <button
            type="button"
            onClick={onClear}
            className="inline-flex items-center gap-1 text-sm font-medium text-accent-fg hover:underline"
          >
            <X aria-hidden className="size-4" />
            Filtreleri temizle
          </button>
        )}
      </div>
    </div>
  )
}
