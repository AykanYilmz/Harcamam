import type { CategoryKind } from '../api/types.ts'

export const KIND_LABELS: Record<CategoryKind, string> = {
  expense: 'Harcama',
  income: 'Gelir',
  transfer: 'Transfer',
}

/** Display order: spending first, transfers (left out of reports) last. */
export const KIND_ORDER: CategoryKind[] = ['expense', 'income', 'transfer']
