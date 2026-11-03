import type { Category } from '../api/types.ts'
import { KIND_LABELS, KIND_ORDER } from '../lib/categories.ts'

/** <option>s for a category <select>, grouped by kind so "Gelir" isn't lost among spending. */
export function CategoryOptions({ categories }: { categories: Category[] }) {
  return KIND_ORDER.map((kind) => {
    const inKind = categories.filter((category) => category.kind === kind)
    if (inKind.length === 0) return null
    return (
      <optgroup key={kind} label={KIND_LABELS[kind]}>
        {inKind.map((category) => (
          <option key={category.id} value={category.id}>
            {category.name}
          </option>
        ))}
      </optgroup>
    )
  })
}
