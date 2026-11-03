import { createContext } from 'react'
import type { User } from '../api/types.ts'

export type AuthStatus = 'loading' | 'authenticated' | 'anonymous'

export interface AuthContextValue {
  status: AuthStatus
  user: User | null
  login(email: string, password: string): Promise<void>
  register(email: string, password: string): Promise<void>
  logout(): void
}

export const AuthContext = createContext<AuthContextValue | null>(null)
