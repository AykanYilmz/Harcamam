import { keepPreviousData, useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { filtersToApiQuery, type TransactionFilters } from '../lib/transactionFilters.ts'
import { invalidateCategorization } from './categories.ts'
import { api } from './index.ts'
import { TRANSACTIONS_KEY } from './statements.ts'
import type {
  BulkCategoryResult,
  TransactionCorrectionResult,
  TransactionPage,
  UncategorizedReport,
} from './types.ts'

/**
 * Outside TRANSACTIONS_KEY on purpose: saving a rule from the list must not refetch it, or
 * the merchant just categorized would vanish before the user sees it confirmed. It is
 * fetched fresh whenever a page using it opens.
 */
const UNCATEGORIZED_KEY = ['uncategorized'] as const

export function useUncategorized() {
  return useQuery({
    queryKey: UNCATEGORIZED_KEY,
    queryFn: () => api.get<UncategorizedReport>('/transactions/uncategorized'),
  })
}

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
