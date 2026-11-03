import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { api } from './index.ts'
import { REPORTS_KEY } from './reports.ts'
import type { User } from './types.ts'

/** The logged-in user (`/auth/me`); refreshed whenever the account's email changes. */
export const ME_QUERY_KEY = ['me'] as const

export function useResendVerification() {
  return useMutation({
    mutationFn: () => api.request<void>('/auth/resend-verification', { method: 'POST' }),
  })
}

export function useChangeEmail() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (values: { newEmail: string; password: string }) =>
      api.post<User>('/auth/change-email', {
        new_email: values.newEmail,
        password: values.password,
      }),
    onSuccess: (user) => queryClient.setQueryData(ME_QUERY_KEY, user),
  })
}

/** Account settings; every report is recalculated when the closing day changes. */
export function useUpdateSettings() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (settings: { periodEndDay: number | null }) =>
      api.patch<User>('/auth/me', { period_end_day: settings.periodEndDay }),
    onSuccess: async (user) => {
      queryClient.setQueryData(ME_QUERY_KEY, user)
      await queryClient.invalidateQueries({ queryKey: REPORTS_KEY })
    },
  })
}

export function useCancelEmailChange() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: () => api.delete('/auth/pending-email'),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ME_QUERY_KEY }),
  })
}

/**
 * Applies the link from a verification email. A query rather than a mutation: it runs once
 * per token even when React renders the page twice, and opening a link twice is harmless.
 */
export function useVerifyEmail(token: string) {
  const queryClient = useQueryClient()
  return useQuery({
    queryKey: ['verify-email', token],
    queryFn: async () => {
      const result = await api.request<{ email: string }>('/auth/verify-email', {
        method: 'POST',
        json: { token },
        auth: false,
      })
      await queryClient.invalidateQueries({ queryKey: ME_QUERY_KEY })
      return result
    },
    enabled: token !== '',
    retry: false,
    staleTime: Infinity,
  })
}
