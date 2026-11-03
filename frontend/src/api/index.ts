import { tokenStore } from '../auth/tokens.ts'
import { createApiClient } from './client.ts'

const SESSION_EXPIRED = 'session-expired'
const sessionEvents = new EventTarget()

export const api = createApiClient({
  baseUrl: import.meta.env.VITE_API_URL ?? 'http://localhost:8000',
  tokens: tokenStore,
  onSessionExpired: () => sessionEvents.dispatchEvent(new Event(SESSION_EXPIRED)),
})

/** Subscribe to "the user must log in again"; returns an unsubscribe function. */
export function onSessionExpired(listener: () => void): () => void {
  sessionEvents.addEventListener(SESSION_EXPIRED, listener)
  return () => sessionEvents.removeEventListener(SESSION_EXPIRED, listener)
}
