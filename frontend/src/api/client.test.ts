import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createTokenStore, type TokenStore } from '../auth/tokens.ts'
import { ApiError, createApiClient, NetworkError } from './client.ts'

function memoryStorage() {
  const data = new Map<string, string>()
  return {
    getItem: (key: string) => data.get(key) ?? null,
    setItem: (key: string, value: string) => void data.set(key, value),
    removeItem: (key: string) => void data.delete(key),
  }
}

function json(status: number, body: unknown): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { 'Content-Type': 'application/json' },
  })
}

const NEW_PAIR = { access_token: 'new-access', refresh_token: 'new-refresh', token_type: 'bearer' }

/** A fake backend: /auth/refresh answers `refreshStatus`, other paths accept only `validToken`. */
function fakeServer({ validToken = 'new-access', refreshStatus = 200 } = {}) {
  return vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
    const url = new URL(String(input))
    if (url.pathname === '/auth/refresh') {
      return refreshStatus === 200 ? json(200, NEW_PAIR) : json(refreshStatus, { detail: 'no' })
    }
    const auth = new Headers(init?.headers).get('Authorization')
    if (auth !== `Bearer ${validToken}`) return json(401, { detail: 'Not authenticated' })
    return json(200, { path: url.pathname, query: url.search })
  })
}

function refreshCalls(fetchFn: ReturnType<typeof fakeServer>) {
  return fetchFn.mock.calls.filter(([input]) => String(input).endsWith('/auth/refresh')).length
}

describe('createApiClient', () => {
  let tokens: TokenStore

  beforeEach(() => {
    tokens = createTokenStore(memoryStorage())
  })

  it('sends the access token', async () => {
    tokens.setTokens('new-access', 'refresh')
    const fetchFn = fakeServer()
    const api = createApiClient({ baseUrl: 'http://api', tokens, fetchFn })

    await expect(api.get('/auth/me')).resolves.toEqual({ path: '/auth/me', query: '' })
    expect(refreshCalls(fetchFn)).toBe(0)
  })

  it('refreshes an expired access token and retries the request', async () => {
    tokens.setTokens('expired', 'refresh')
    const fetchFn = fakeServer()
    const api = createApiClient({ baseUrl: 'http://api', tokens, fetchFn })

    await expect(api.get('/auth/me')).resolves.toMatchObject({ path: '/auth/me' })
    expect(refreshCalls(fetchFn)).toBe(1)
    expect(tokens.getAccessToken()).toBe('new-access')
    expect(tokens.getRefreshToken()).toBe('new-refresh')
  })

  it('downloads a file with the name the server suggests, refreshing the session first', async () => {
    tokens.setTokens('expired', 'refresh')
    const server = fakeServer()
    const fetchFn = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      if (!String(input).includes('/exports/')) return server(input, init)
      if (new Headers(init?.headers).get('Authorization') !== 'Bearer new-access') {
        return json(401, { detail: 'Not authenticated' })
      }
      return new Response('Tarih;Tutar', {
        headers: { 'Content-Disposition': 'attachment; filename="hesapkitap_2026.csv"' },
      })
    })
    const api = createApiClient({ baseUrl: 'http://api', tokens, fetchFn })

    const { blob, fileName } = await api.download('/exports/transactions', { format: 'csv' })

    expect(fileName).toBe('hesapkitap_2026.csv')
    expect(await blob.text()).toBe('Tarih;Tutar')
    expect(String(fetchFn.mock.calls.at(-1)?.[0])).toContain('format=csv')
  })

  it('refreshes only once for concurrent requests', async () => {
    tokens.setTokens('expired', 'refresh')
    const fetchFn = fakeServer()
    const api = createApiClient({ baseUrl: 'http://api', tokens, fetchFn })

    await Promise.all([api.get('/a'), api.get('/b'), api.get('/c')])

    expect(refreshCalls(fetchFn)).toBe(1)
  })

  it('gets an access token first after a page reload', async () => {
    tokens.setTokens('ignored', 'refresh')
    // A reload keeps only the refresh token.
    const reloaded = createTokenStore({
      getItem: () => 'refresh',
      setItem: () => undefined,
      removeItem: () => undefined,
    })
    const fetchFn = fakeServer()
    const api = createApiClient({ baseUrl: 'http://api', tokens: reloaded, fetchFn })

    await api.get('/auth/me')

    expect(fetchFn.mock.calls.map(([input]) => new URL(String(input)).pathname)).toEqual([
      '/auth/refresh',
      '/auth/me',
    ])
  })

  it('ends the session when the refresh token is rejected', async () => {
    tokens.setTokens('expired', 'revoked')
    const onSessionExpired = vi.fn()
    const api = createApiClient({
      baseUrl: 'http://api',
      tokens,
      fetchFn: fakeServer({ refreshStatus: 401 }),
      onSessionExpired,
    })

    const error = await api.get('/auth/me').catch((err: unknown) => err)

    expect(error).toBeInstanceOf(ApiError)
    expect((error as ApiError).status).toBe(401)
    expect(onSessionExpired).toHaveBeenCalledOnce()
    expect(tokens.getRefreshToken()).toBeNull()
  })

  it('does not touch tokens on requests without auth', async () => {
    const fetchFn = vi.fn(async () => json(401, { detail: 'Incorrect email or password' }))
    const api = createApiClient({ baseUrl: 'http://api', tokens, fetchFn })

    const error = await api
      .request('/auth/login', { method: 'POST', auth: false })
      .catch((err: unknown) => err)

    expect((error as ApiError).detail).toBe('Incorrect email or password')
    expect(fetchFn).toHaveBeenCalledOnce()
  })

  it('repeats array query parameters and skips empty ones', async () => {
    tokens.setTokens('new-access', 'refresh')
    const api = createApiClient({ baseUrl: 'http://api', tokens, fetchFn: fakeServer() })

    const result = await api.get<{ query: string }>('/transactions', {
      category_id: ['a', 'b'],
      q: '',
      page: 2,
      type: undefined,
    })

    expect(result.query).toBe('?category_id=a&category_id=b&page=2')
  })

  it('turns a failed connection into a NetworkError', async () => {
    const fetchFn = vi.fn(async () => {
      throw new TypeError('Failed to fetch')
    })
    const api = createApiClient({ baseUrl: 'http://api', tokens, fetchFn })

    await expect(api.request('/health', { auth: false })).rejects.toBeInstanceOf(NetworkError)
  })
})
