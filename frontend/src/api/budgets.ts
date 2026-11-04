import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { api } from './index.ts'
import { REPORTS_KEY } from './reports.ts'
import type { BudgetReport } from './types.ts'

// Under REPORTS_KEY: spending changes with uploads and recategorization, which refresh all
// reports, so budgets are refreshed with them.
const BUDGETS_KEY = [...REPORTS_KEY, 'budgets'] as const

/** `month` undefined lets the API pick the latest month that has data. */
export function useBudgets(month: string | undefined) {
  return useQuery({
    queryKey: [...BUDGETS_KEY, month ?? 'latest'],
    queryFn: () => api.get<BudgetReport>('/budgets', { month }),
  })
}

function useBudgetMutation<T>(mutationFn: (values: T) => Promise<unknown>) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: BUDGETS_KEY }),
  })
}

export function useCreateBudget() {
  return useBudgetMutation((budget: { categoryId: string; monthlyLimit: string }) =>
    api.post('/budgets', { category_id: budget.categoryId, monthly_limit: budget.monthlyLimit }),
  )
}

export function useUpdateBudget() {
  return useBudgetMutation((budget: { id: string; monthlyLimit: string }) =>
    api.patch(`/budgets/${budget.id}`, { monthly_limit: budget.monthlyLimit }),
  )
}

export function useDeleteBudget() {
  return useBudgetMutation((id: string) => api.delete(`/budgets/${id}`))
}
