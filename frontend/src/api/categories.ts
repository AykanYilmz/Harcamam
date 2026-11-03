import { useMutation, useQuery, useQueryClient, type QueryClient } from '@tanstack/react-query'
import { api } from './index.ts'
import { REPORTS_KEY } from './reports.ts'
import { TRANSACTIONS_KEY } from './statements.ts'
import type { Category, CategoryCreate, CategoryUpdate, Rule, RuleSaveResult } from './types.ts'

export const CATEGORIES_KEY = ['categories'] as const
export const RULES_KEY = ['category-rules'] as const

/** Categories and rules decide where transactions land, so reports change with them. */
export function invalidateCategorization(queryClient: QueryClient) {
  return Promise.all(
    [CATEGORIES_KEY, RULES_KEY, TRANSACTIONS_KEY, REPORTS_KEY].map((queryKey) =>
      queryClient.invalidateQueries({ queryKey }),
    ),
  )
}

export function useCategories() {
  return useQuery({
    queryKey: CATEGORIES_KEY,
    queryFn: () => api.get<Category[]>('/categories'),
    staleTime: 5 * 60_000,
  })
}

export function useCreateCategory() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (category: CategoryCreate) => api.post<Category>('/categories', category),
    onSuccess: () => invalidateCategorization(queryClient),
  })
}

export function useUpdateCategory() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ id, changes }: { id: string; changes: CategoryUpdate }) =>
      api.patch<Category>(`/categories/${id}`, changes),
    onSuccess: () => invalidateCategorization(queryClient),
  })
}

export function useDeleteCategory() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (id: string) => api.delete(`/categories/${id}`),
    onSuccess: () => invalidateCategorization(queryClient),
  })
}

export function useRules() {
  return useQuery({
    queryKey: RULES_KEY,
    queryFn: () => api.get<Rule[]>('/category-rules'),
  })
}

export function useCreateRule() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (rule: { keyword: string; category_id: string; apply_to_existing: boolean }) =>
      api.post<RuleSaveResult>('/category-rules', rule),
    onSuccess: () => invalidateCategorization(queryClient),
  })
}

export function useDeleteRule() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (id: string) => api.delete(`/category-rules/${id}`),
    onSuccess: () => invalidateCategorization(queryClient),
  })
}
