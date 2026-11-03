import { useQuery, useQueryClient } from '@tanstack/react-query'
import { useCallback, useEffect, useMemo, useState, type ReactNode } from 'react'
import { api, onSessionExpired } from '../api/index.ts'
import type { TokenPair, User } from '../api/types.ts'
import { AuthContext, type AuthContextValue, type AuthStatus } from './AuthContext.ts'
import { tokenStore } from './tokens.ts'

const ME_QUERY_KEY = ['me']

export function AuthProvider({ children }: { children: ReactNode }) {
  const queryClient = useQueryClient()
  // A stored refresh token means we may still be logged in; /auth/me confirms it.
  const [hasSession, setHasSession] = useState(() => tokenStore.getRefreshToken() !== null)

  const me = useQuery({
    queryKey: ME_QUERY_KEY,
    queryFn: () => api.get<User>('/auth/me'),
    enabled: hasSession,
    retry: false,
    staleTime: Infinity,
  })

  const endSession = useCallback(() => {
    tokenStore.clear()
    setHasSession(false)
    // Drop every cached response so the next user never sees the previous one's data.
    queryClient.clear()
  }, [queryClient])

  useEffect(() => onSessionExpired(endSession), [endSession])

  const login = useCallback(
    async (email: string, password: string) => {
      const form = new URLSearchParams({ username: email, password })
      const pair = await api.request<TokenPair>('/auth/login', {
        method: 'POST',
        body: form,
        auth: false,
      })
      tokenStore.setTokens(pair.access_token, pair.refresh_token)
      await queryClient.fetchQuery({
        queryKey: ME_QUERY_KEY,
        queryFn: () => api.get<User>('/auth/me'),
      })
      setHasSession(true)
    },
    [queryClient],
  )

  const register = useCallback(
    async (email: string, password: string) => {
      await api.request('/auth/register', {
        method: 'POST',
        json: { email, password },
        auth: false,
      })
      await login(email, password)
    },
    [login],
  )

  const changePassword = useCallback(async (currentPassword: string, newPassword: string) => {
    const pair = await api.post<TokenPair>('/auth/change-password', {
      current_password: currentPassword,
      new_password: newPassword,
    })
    tokenStore.setTokens(pair.access_token, pair.refresh_token)
  }, [])

  const deleteAccount = useCallback(async (password: string) => {
    await api.request('/auth/me', { method: 'DELETE', json: { password } })
  }, [])

  let status: AuthStatus
  if (!hasSession || me.isError) status = 'anonymous'
  else if (me.isSuccess) status = 'authenticated'
  else status = 'loading'

  const value = useMemo<AuthContextValue>(
    () => ({
      status,
      user: status === 'authenticated' ? (me.data ?? null) : null,
      login,
      register,
      changePassword,
      deleteAccount,
      logout: endSession,
    }),
    [status, me.data, login, register, changePassword, deleteAccount, endSession],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}
