import type { BudgetStatus } from '../api/types.ts'

export const BUDGET_STATUS_LABELS: Record<BudgetStatus, string> = {
  ok: 'Yolunda',
  warning: 'Limite yakın',
  over: 'Limit aşıldı',
}
