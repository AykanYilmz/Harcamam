import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter, Route, Routes } from 'react-router'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { AuthContext, type AuthContextValue } from '../auth/AuthContext.ts'
import { ThemeProvider } from '../theme/ThemeProvider.tsx'
import { AppLayout } from './AppLayout.tsx'

const auth: AuthContextValue = {
  status: 'authenticated',
  user: { id: '1', email: 'ayse@example.com', created_at: '2026-11-01T00:00:00Z' },
  login: vi.fn(),
  register: vi.fn(),
  changePassword: vi.fn(),
  deleteAccount: vi.fn(),
  logout: vi.fn(),
}

function setScreen(desktop: boolean) {
  vi.stubGlobal(
    'matchMedia',
    vi.fn((query: string) => ({
      matches: desktop && query.includes('min-width'),
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
    })),
  )
}

function renderLayout() {
  render(
    <ThemeProvider>
      <AuthContext.Provider value={auth}>
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
  beforeEach(() => localStorage.clear())
  afterEach(() => vi.unstubAllGlobals())

  it('shows the current page title in the app bar', () => {
    setScreen(true)
    renderLayout()

    expect(screen.getByRole('heading', { level: 1 })).toHaveTextContent('Ekstre Yükle')
  })

  it('hides and shows the sidebar on wide screens and remembers it', async () => {
    setScreen(true)
    const { sidebar, toggle } = renderLayout()
    expect(sidebar).toHaveClass('md:visible')
    expect(toggle()).toHaveAttribute('aria-expanded', 'true')

    await userEvent.click(toggle())

    expect(sidebar).toHaveClass('md:invisible')
    expect(toggle()).toHaveAttribute('aria-expanded', 'false')
    expect(localStorage.getItem('harcamam.sidebarOpen')).toBe('false')
  })

  it('opens the phone drawer and closes it after navigating', async () => {
    setScreen(false)
    const { sidebar, toggle } = renderLayout()
    expect(sidebar).toHaveClass('invisible')

    await userEvent.click(toggle())
    expect(sidebar).toHaveClass('visible')

    await userEvent.click(screen.getByRole('link', { name: 'Özet' }))
    expect(sidebar).toHaveClass('invisible')
    expect(screen.getByText('Özet sayfası')).toBeInTheDocument()
  })

  it('closes the phone drawer with Escape', async () => {
    setScreen(false)
    const { sidebar, toggle } = renderLayout()

    await userEvent.click(toggle())
    await userEvent.keyboard('{Escape}')

    expect(sidebar).toHaveClass('invisible')
  })
})
