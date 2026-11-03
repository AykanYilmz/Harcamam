import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { ApiError } from '../api/client.ts'
import { AuthContext, type AuthContextValue } from '../auth/AuthContext.ts'
import { VerifyEmailPage } from './VerifyEmailPage.tsx'

const verification = vi.hoisted(() => ({ state: {} as Record<string, unknown>, token: '' }))

vi.mock('../api/account.ts', () => ({
  useVerifyEmail: (token: string) => {
    verification.token = token
    return verification.state
  },
}))

function renderPage(status: AuthContextValue['status'], url = '/eposta-dogrula?token=abc') {
  const auth = { status, user: null } as AuthContextValue
  render(
    <AuthContext.Provider value={auth}>
      <MemoryRouter initialEntries={[url]}>
        <VerifyEmailPage />
      </MemoryRouter>
    </AuthContext.Provider>,
  )
}

describe('VerifyEmailPage', () => {
  beforeEach(() => {
    verification.state = { isPending: true, isSuccess: false }
  })

  it('verifies the token from the link', () => {
    renderPage('anonymous')

    expect(verification.token).toBe('abc')
    expect(screen.getByText('Doğrulanıyor…')).toBeInTheDocument()
  })

  it('confirms and sends a logged-out user to log in', () => {
    verification.state = { isSuccess: true, data: { email: 'ayse@example.com' } }
    renderPage('anonymous')

    expect(screen.getByText('E-posta adresin doğrulandı')).toBeInTheDocument()
    expect(screen.getByRole('link', { name: 'Giriş yap' })).toHaveAttribute('href', '/giris')
  })

  it('sends a logged-in user back to the app', () => {
    verification.state = { isSuccess: true, data: { email: 'ayse@example.com' } }
    renderPage('authenticated')

    expect(screen.getByRole('link', { name: 'Uygulamaya dön' })).toHaveAttribute('href', '/')
  })

  it('explains an invalid or expired link', () => {
    verification.state = { isError: true, isPending: false, error: new ApiError(400, 'x') }
    renderPage('anonymous')

    expect(screen.getByText('Bağlantı geçersiz ya da süresi dolmuş')).toBeInTheDocument()
  })

  it('explains an address taken in the meantime', () => {
    verification.state = { isError: true, isPending: false, error: new ApiError(409, 'x') }
    renderPage('anonymous')

    expect(screen.getByText('Bu adres başka bir hesapta kullanılıyor')).toBeInTheDocument()
  })

  it('treats a link without a token as invalid', () => {
    verification.state = { isPending: true, isSuccess: false }
    renderPage('anonymous', '/eposta-dogrula')

    expect(screen.getByText('Bağlantı geçersiz ya da süresi dolmuş')).toBeInTheDocument()
  })
})
