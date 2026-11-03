import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter, Route, Routes } from 'react-router'
import { describe, expect, it, vi } from 'vitest'
import { AuthContext, type AuthContextValue } from '../auth/AuthContext.ts'
import { ThemeProvider } from '../theme/ThemeProvider.tsx'
import { AppLayout } from './AppLayout.tsx'

vi.mock('../api/account.ts', () => ({
  useResendVerification: () => ({ mutate: vi.fn(), isPending: false, isSuccess: false }),
}))

const auth: AuthContextValue = {
  status: 'authenticated',
  user: {
    id: '1',
    email: 'ayse@example.com',
    created_at: '2026-11-01T00:00:00Z',
    email_verified: true,
    pending_email: null,
  },
  login: vi.fn(),
  register: vi.fn(),
  changePassword: vi.fn(),
  deleteAccount: vi.fn(),
  logout: vi.fn(),
}

function renderLayout(value: AuthContextValue = auth) {
  render(
    <ThemeProvider>
      <AuthContext.Provider value={value}>
        <MemoryRouter initialEntries={['/yukle']}>
          <Routes>
            <Route element={<AppLayout />}>
              <Route path="/yukle" element={<p>Yükleme sayfası</p>} />
              <Route path="/" element={<p>Özet sayfası</p>} />
            </Route>
          </Routes>
        </MemoryRouter>
      </AuthContext.Provider>
    </ThemeProvider>,
  )
  return {
    sidebar: screen.getByRole('complementary', { name: 'Kenar çubuğu' }),
    toggle: () => screen.getByRole('button', { name: /Menüyü (aç|kapat)/ }),
  }
}

describe('AppLayout', () => {
  it('shows the current page title in the app bar', () => {
    renderLayout()

    expect(screen.getByRole('heading', { level: 1 })).toHaveTextContent('Ekstre Yükle')
  })

  it('opens the menu over the page and closes it after navigating', async () => {
    const { sidebar, toggle } = renderLayout()
    expect(sidebar).toHaveClass('invisible')
    expect(toggle()).toHaveAttribute('aria-expanded', 'false')

    await userEvent.click(toggle())
    expect(sidebar).toHaveClass('visible')
    expect(toggle()).toHaveAttribute('aria-expanded', 'true')

    await userEvent.click(screen.getByRole('link', { name: 'Özet' }))
    expect(sidebar).toHaveClass('invisible')
    expect(screen.getByText('Özet sayfası')).toBeInTheDocument()
  })

  it('closes the menu with Escape', async () => {
    const { sidebar, toggle } = renderLayout()

    await userEvent.click(toggle())
    await userEvent.keyboard('{Escape}')

    expect(sidebar).toHaveClass('invisible')
  })

  it('shows the app name in the middle of the app bar, linking home', () => {
    renderLayout()

    expect(screen.getByRole('link', { name: 'HesapKitap' })).toHaveAttribute('href', '/')
  })
})

describe('AppLayout email verification banner', () => {
  it('reminds an unverified user, who can dismiss it', async () => {
    renderLayout({ ...auth, user: { ...auth.user!, email_verified: false } })

    expect(screen.getByText('E-posta adresini doğrula.')).toBeInTheDocument()
    await userEvent.click(screen.getByRole('button', { name: 'Uyarıyı kapat' }))

    expect(screen.queryByText('E-posta adresini doğrula.')).not.toBeInTheDocument()
  })

  it('stays out of the way for a verified user', () => {
    renderLayout()

    expect(screen.queryByText('E-posta adresini doğrula.')).not.toBeInTheDocument()
  })
})
