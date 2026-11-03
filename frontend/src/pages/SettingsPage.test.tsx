import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter, Route, Routes, useLocation } from 'react-router'
import { describe, expect, it, vi } from 'vitest'
import { ApiError } from '../api/client.ts'
import { AuthContext, type AuthContextValue } from '../auth/AuthContext.ts'
import { ThemeProvider } from '../theme/ThemeProvider.tsx'
import { SettingsPage } from './SettingsPage.tsx'

function LoginStub() {
  const location = useLocation()
  return <p>{(location.state as { notice?: string } | null)?.notice}</p>
}

function renderSettings(overrides: Partial<AuthContextValue> = {}) {
  const auth: AuthContextValue = {
    status: 'authenticated',
    user: { id: '1', email: 'ayse@example.com', created_at: '2026-11-01T10:00:00Z' },
    login: vi.fn(),
    register: vi.fn(),
    changePassword: vi.fn().mockResolvedValue(undefined),
    deleteAccount: vi.fn().mockResolvedValue(undefined),
    logout: vi.fn(),
    ...overrides,
  }
  render(
    <ThemeProvider>
      <AuthContext.Provider value={auth}>
        <MemoryRouter initialEntries={['/ayarlar']}>
          <Routes>
            <Route path="/ayarlar" element={<SettingsPage />} />
            <Route path="/giris" element={<LoginStub />} />
          </Routes>
        </MemoryRouter>
      </AuthContext.Provider>
    </ThemeProvider>,
  )
  return auth
}

async function fillPasswords(current: string, next: string, confirm: string) {
  await userEvent.type(screen.getByLabelText('Mevcut şifre'), current)
  await userEvent.type(screen.getByLabelText('Yeni şifre'), next)
  await userEvent.type(screen.getByLabelText('Yeni şifre (tekrar)'), confirm)
  await userEvent.click(screen.getByRole('button', { name: 'Şifreyi değiştir' }))
}

describe('SettingsPage', () => {
  it('shows the account', () => {
    renderSettings()

    expect(screen.getByText('ayse@example.com')).toBeInTheDocument()
    expect(screen.getByText('1 Kas 2026')).toBeInTheDocument()
  })

  it('checks that the new passwords match before sending', async () => {
    const auth = renderSettings()

    await fillPasswords('eski-sifre-123', 'yeni-sifre-456', 'baska-sifre-789')

    expect(screen.getByText('Şifreler eşleşmiyor.')).toBeInTheDocument()
    expect(auth.changePassword).not.toHaveBeenCalled()
  })

  it('changes the password', async () => {
    const auth = renderSettings()

    await fillPasswords('eski-sifre-123', 'yeni-sifre-456', 'yeni-sifre-456')

    expect(auth.changePassword).toHaveBeenCalledWith('eski-sifre-123', 'yeni-sifre-456')
    expect(await screen.findByRole('status')).toHaveTextContent('Şifren değiştirildi')
  })

  it('explains a wrong current password', async () => {
    renderSettings({ changePassword: vi.fn().mockRejectedValue(new ApiError(400, 'x')) })

    await fillPasswords('yanlis-sifre', 'yeni-sifre-456', 'yeni-sifre-456')

    expect(await screen.findByRole('alert')).toHaveTextContent('Mevcut şifre hatalı.')
  })

  it('deletes the account and leaves with a message', async () => {
    const auth = renderSettings()

    await userEvent.click(screen.getByRole('button', { name: 'Hesabımı sil' }))
    await userEvent.type(screen.getByLabelText('Şifre'), 'guclu-sifre-123')
    await userEvent.click(screen.getByRole('button', { name: 'Hesabımı kalıcı olarak sil' }))

    expect(auth.deleteAccount).toHaveBeenCalledWith('guclu-sifre-123')
    expect(auth.logout).toHaveBeenCalled()
    expect(await screen.findByText('Hesabın ve tüm verilerin silindi.')).toBeInTheDocument()
  })

  it('keeps the account when the password is wrong', async () => {
    const auth = renderSettings({
      deleteAccount: vi.fn().mockRejectedValue(new ApiError(400, 'x')),
    })

    await userEvent.click(screen.getByRole('button', { name: 'Hesabımı sil' }))
    await userEvent.type(screen.getByLabelText('Şifre'), 'yanlis-sifre')
    await userEvent.click(screen.getByRole('button', { name: 'Hesabımı kalıcı olarak sil' }))

    expect(await screen.findByRole('alert')).toHaveTextContent('Şifre hatalı.')
    expect(auth.logout).not.toHaveBeenCalled()
  })
})
