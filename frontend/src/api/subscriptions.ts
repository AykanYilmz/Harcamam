import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { api } from './index.ts'
import { REPORTS_KEY } from './reports.ts'
import type { SubscriptionReport } from './types.ts'

// Under REPORTS_KEY: detected from transactions, so uploads and corrections refresh it.
const SUBSCRIPTIONS_KEY = [...REPORTS_KEY, 'subscriptions'] as const

export function useSubscriptions() {
  return useQuery({
    queryKey: SUBSCRIPTIONS_KEY,
    queryFn: () => api.get<SubscriptionReport>('/subscriptions'),
  })
}

function useSubscriptionMutation(mutationFn: (key: string) => Promise<unknown>) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: SUBSCRIPTIONS_KEY }),
  })
}

/** "This is not a subscription": hides it from the list. */
export function useDismissSubscription() {
  return useSubscriptionMutation((key) => api.post('/subscriptions/dismissed', { key }))
}

export function useRestoreSubscription() {
  return useSubscriptionMutation((key) =>
    api.delete(`/subscriptions/dismissed/${encodeURIComponent(key)}`),
  )
}
