const REFRESH_TOKEN_KEY = 'harcamam.refreshToken'

export interface TokenStore {
  getAccessToken(): string | null
  getRefreshToken(): string | null
  setTokens(accessToken: string, refreshToken: string): void
  clear(): void
}

/**
 * The access token lives only in memory (gone on reload, short-lived anyway); the refresh
 * token is persisted so the session survives a reload. `storage` is injectable for tests.
 */
export function createTokenStore(storage: Pick<Storage, 'getItem' | 'setItem' | 'removeItem'>) {
  let accessToken: string | null = null

  // Storage can throw (private mode, blocked site data); the app then just keeps no session.
  const safely = <T>(action: () => T, fallback: T): T => {
    try {
      return action()
    } catch {
      return fallback
    }
  }

  const store: TokenStore = {
    getAccessToken: () => accessToken,
    getRefreshToken: () => safely(() => storage.getItem(REFRESH_TOKEN_KEY), null),
    setTokens(access, refresh) {
      accessToken = access
      safely(() => storage.setItem(REFRESH_TOKEN_KEY, refresh), undefined)
    },
    clear() {
      accessToken = null
      safely(() => storage.removeItem(REFRESH_TOKEN_KEY), undefined)
    },
  }
  return store
}

export const tokenStore = createTokenStore(window.localStorage)
