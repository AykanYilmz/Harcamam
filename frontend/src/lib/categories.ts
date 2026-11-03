import type { Category, CategoryKind } from '../api/types.ts'

/** The built-in fallback for transactions no rule recognizes (backend OTHER_CATEGORY). */
export const OTHER_CATEGORY = 'Diğer'

export function isOtherCategory(category: Category): boolean {
  return category.is_default && category.name === OTHER_CATEGORY
}

export const KIND_LABELS: Record<CategoryKind, string> = {
  expense: 'Harcama',
  income: 'Gelir',
  transfer: 'Transfer',
}

/** Display order: spending first, transfers (left out of reports) last. */
export const KIND_ORDER: CategoryKind[] = ['expense', 'income', 'transfer']
