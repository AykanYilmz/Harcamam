import type { TokenStore } from '../auth/tokens.ts'
import type { TokenPair } from './types.ts'

/** The server answered with an error status. */
export class ApiError extends Error {
  readonly status: number
  readonly detail: unknown

  constructor(status: number, detail: unknown) {
    super(`Request failed with status ${status}`)
    this.name = 'ApiError'
    this.status = status
    this.detail = detail
  }
}

/** The server could not be reached at all. */
export class NetworkError extends Error {
  constructor() {
    super('The server could not be reached')
    this.name = 'NetworkError'
  }
}

type QueryValue = string | number | boolean | null | undefined | ReadonlyArray<string | number>

export interface RequestOptions {
  method?: 'GET' | 'POST' | 'PATCH' | 'DELETE'
  query?: Record<string, QueryValue>
  /** Sent as JSON. */
  json?: unknown
  /** Sent as multipart (file uploads) or urlencoded (OAuth2 login form). */
  body?: FormData | URLSearchParams
  /** Attach the access token and refresh it when it expires. Defaults to true. */
  auth?: boolean
}

export interface ApiClientConfig {
  baseUrl: string
  tokens: TokenStore
  fetchFn?: typeof fetch
  /** Called when the session can't be renewed and the user has to log in again. */
  onSessionExpired?: () => void
}

export function createApiClient({
  baseUrl,
  tokens,
  fetchFn = (...args) => fetch(...args),
  onSessionExpired,
}: ApiClientConfig) {
  // Shared by concurrent requests: when several get a 401 at once, only one refresh is sent.
  let refreshInFlight: Promise<boolean> | null = null

  function buildUrl(path: string, query: RequestOptions['query']): string {
    const url = new URL(path, baseUrl)
    for (const [key, value] of Object.entries(query ?? {})) {
      if (value === null || value === undefined || value === '') continue
      const values = Array.isArray(value) ? value : [value]
      for (const item of values) url.searchParams.append(key, String(item))
    }
    return url.toString()
  }

  async function send(path: string, options: RequestOptions, accessToken: string | null) {
    const headers = new Headers()
    let body: BodyInit | undefined = options.body
    if (options.json !== undefined) {
      headers.set('Content-Type', 'application/json')
      body = JSON.stringify(options.json)
    }
    if (accessToken) headers.set('Authorization', `Bearer ${accessToken}`)

    try {
      return await fetchFn(buildUrl(path, options.query), {
        method: options.method ?? 'GET',
        headers,
        body,
      })
    } catch {
      throw new NetworkError()
    }
  }

  function refreshTokens(): Promise<boolean> {
    const refreshToken = tokens.getRefreshToken()
    if (!refreshToken) return Promise.resolve(false)

    refreshInFlight ??= (async () => {
      try {
        const response = await send(
          '/auth/refresh',
          { method: 'POST', json: { refresh_token: refreshToken } },
          null,
        )
        if (!response.ok) return false
        const pair = (await response.json()) as TokenPair
        tokens.setTokens(pair.access_token, pair.refresh_token)
        return true
      } finally {
        refreshInFlight = null
      }
    })()
    return refreshInFlight
  }

  async function readDetail(response: Response): Promise<unknown> {
    try {
      const data: unknown = await response.json()
      return typeof data === 'object' && data !== null && 'detail' in data ? data.detail : data
    } catch {
      return null
    }
  }

  async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
    const auth = options.auth ?? true

    // After a page reload only the refresh token is left: get an access token first.
    if (auth && !tokens.getAccessToken() && tokens.getRefreshToken()) {
      await refreshTokens()
    }

    let response = await send(path, options, auth ? tokens.getAccessToken() : null)

    if (auth && response.status === 401) {
      if (await refreshTokens()) {
        response = await send(path, options, tokens.getAccessToken())
      }
      if (response.status === 401) {
        tokens.clear()
        onSessionExpired?.()
      }
    }

    if (!response.ok) throw new ApiError(response.status, await readDetail(response))
    if (response.status === 204) return undefined as T
    return (await response.json()) as T
  }

  return {
    request,
    get: <T>(path: string, query?: RequestOptions['query']) => request<T>(path, { query }),
    post: <T>(path: string, json?: unknown) => request<T>(path, { method: 'POST', json }),
    patch: <T>(path: string, json?: unknown) => request<T>(path, { method: 'PATCH', json }),
    delete: (path: string) => request<void>(path, { method: 'DELETE' }),
  }
}

export type ApiClient = ReturnType<typeof createApiClient>
