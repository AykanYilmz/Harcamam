import { createContext } from 'react'
import type { User } from '../api/types.ts'

export type AuthStatus = 'loading' | 'authenticated' | 'anonymous'

export interface AuthContextValue {
  status: AuthStatus
  user: User | null
  login(email: string, password: string): Promise<void>
  register(email: string, password: string): Promise<void>
  /** Other sessions are logged out; this one continues with new tokens. */
  changePassword(currentPassword: string, newPassword: string): Promise<void>
  /** Deletes the account and all its data. The caller logs out afterwards. */
  deleteAccount(password: string): Promise<void>
  logout(): void
}

export const AuthContext = createContext<AuthContextValue | null>(null)
