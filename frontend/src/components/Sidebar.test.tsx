import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { useState } from 'react'
import { MemoryRouter } from 'react-router'
import { describe, expect, it, vi } from 'vitest'
import { AuthContext, type AuthContextValue } from '../auth/AuthContext.ts'
import { ThemeProvider } from '../theme/ThemeProvider.tsx'
import { Sidebar } from './Sidebar.tsx'

const auth: AuthContextValue = {
  status: 'authenticated',
  user: { id: '1', email: 'ayse@example.com', created_at: '2026-11-01T00:00:00Z' },
  login: vi.fn(),
  register: vi.fn(),
  logout: vi.fn(),
}

function Harness({ initiallyCollapsed }: { initiallyCollapsed: boolean }) {
  const [collapsed, setCollapsed] = useState(initiallyCollapsed)
  return <Sidebar collapsed={collapsed} onCollapsedChange={setCollapsed} />
}

function renderSidebar(initiallyCollapsed: boolean) {
  render(
    <ThemeProvider>
      <AuthContext.Provider value={auth}>
        <MemoryRouter>
          <Harness initiallyCollapsed={initiallyCollapsed} />
        </MemoryRouter>
      </AuthContext.Provider>
    </ThemeProvider>,
  )
  return screen.getByRole('complementary', { name: 'Kenar çubuğu' })
}

describe('Sidebar', () => {
  it('collapses to an icon rail', async () => {
    const sidebar = renderSidebar(false)
    expect(sidebar).toHaveClass('w-60')

    await userEvent.click(screen.getByRole('button', { name: 'Menüyü daralt' }))

    expect(sidebar).toHaveClass('w-[4.5rem]')
  })

  it('is pinned open again from the wallet logo', async () => {
    const sidebar = renderSidebar(true)

    // Both the logo and the panel button are labelled; the logo comes first.
    await userEvent.click(screen.getAllByRole('button', { name: 'Menüyü sabitle' })[0])

    expect(sidebar).toHaveClass('w-60')
  })

  it('keeps links accessible by name when collapsed', () => {
    renderSidebar(true)

    expect(screen.getByRole('link', { name: 'İşlemler' })).toBeInTheDocument()
  })
})
