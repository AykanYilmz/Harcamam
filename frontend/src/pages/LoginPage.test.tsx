import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter, Route, Routes } from 'react-router'
import { describe, expect, it, vi } from 'vitest'
import { ApiError } from '../api/client.ts'
import { AuthContext, type AuthContextValue } from '../auth/AuthContext.ts'
import { LoginPage } from './LoginPage.tsx'

function renderLogin(login: AuthContextValue['login']) {
  const auth: AuthContextValue = {
    status: 'anonymous',
    user: null,
    login,
    register: vi.fn(),
    logout: vi.fn(),
  }
  render(
    <AuthContext.Provider value={auth}>
      <MemoryRouter initialEntries={['/giris']}>
        <Routes>
          <Route path="/giris" element={<LoginPage />} />
          <Route path="/" element={<p>Ana sayfa</p>} />
        </Routes>
      </MemoryRouter>
    </AuthContext.Provider>,
  )
}

async function fillAndSubmit() {
  const user = userEvent.setup()
  await user.type(screen.getByLabelText('E-posta'), '  ayse@example.com ')
  await user.type(screen.getByLabelText('Şifre'), 'guclu-sifre-123')
  await user.click(screen.getByRole('button', { name: 'Giriş yap' }))
}

describe('LoginPage', () => {
  it('logs in with the trimmed email and goes to the home page', async () => {
    const login = vi.fn().mockResolvedValue(undefined)
    renderLogin(login)

    await fillAndSubmit()

    expect(login).toHaveBeenCalledWith('ayse@example.com', 'guclu-sifre-123')
    expect(await screen.findByText('Ana sayfa')).toBeInTheDocument()
  })

  it('shows a Turkish message for wrong credentials', async () => {
    const login = vi.fn().mockRejectedValue(new ApiError(401, 'Incorrect email or password'))
    renderLogin(login)

    await fillAndSubmit()

    expect(await screen.findByRole('alert')).toHaveTextContent('E-posta adresi veya şifre hatalı.')
    expect(screen.getByRole('button', { name: 'Giriş yap' })).toBeEnabled()
  })
})
