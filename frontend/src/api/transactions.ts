import { keepPreviousData, useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { filtersToApiQuery, type TransactionFilters } from '../lib/transactionFilters.ts'
import { invalidateCategorization } from './categories.ts'
import { api } from './index.ts'
import { TRANSACTIONS_KEY } from './statements.ts'
import type { BulkCategoryResult, TransactionCorrectionResult, TransactionPage } from './types.ts'

export function useTransactions(filters: TransactionFilters) {
  return useQuery({
    queryKey: [...TRANSACTIONS_KEY, filters],
    queryFn: () => api.get<TransactionPage>('/transactions', filtersToApiQuery(filters)),
    // Keep showing the current page while the next one loads, instead of a spinner.
    placeholderData: keepPreviousData,
  })
}

export function useCorrectCategory() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({
      transactionId,
      categoryId,
      ruleKeyword,
    }: {
      transactionId: string
      categoryId: string
      ruleKeyword?: string
    }) =>
      api.patch<TransactionCorrectionResult>(`/transactions/${transactionId}`, {
        category_id: categoryId,
        rule_keyword: ruleKeyword || undefined,
      }),
    onSuccess: () => invalidateCategorization(queryClient),
  })
}

export function useBulkCategory() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({
      transactionIds,
      categoryId,
    }: {
      transactionIds: string[]
      categoryId: string
    }) =>
      api.patch<BulkCategoryResult>('/transactions/bulk', {
        transaction_ids: transactionIds,
        category_id: categoryId,
      }),
    onSuccess: () => invalidateCategorization(queryClient),
  })
}
