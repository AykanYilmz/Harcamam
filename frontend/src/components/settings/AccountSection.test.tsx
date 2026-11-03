import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import type { User } from '../../api/types.ts'
import { AccountSection } from './AccountSection.tsx'

const mocks = vi.hoisted(() => ({
  resend: vi.fn(),
  changeEmail: vi.fn(),
  cancel: vi.fn(),
}))

vi.mock('../../api/account.ts', () => {
  const mutation = (mutate: () => void) => ({
    mutate,
    isPending: false,
    isError: false,
    isSuccess: false,
    error: null,
  })
  return {
    useResendVerification: () => mutation(mocks.resend),
    useChangeEmail: () => mutation(mocks.changeEmail),
    useCancelEmailChange: () => mutation(mocks.cancel),
  }
})

const USER: User = {
  id: '1',
  email: 'ayse@example.com',
  created_at: '2026-11-01T10:00:00Z',
  email_verified: true,
  pending_email: null,
}

describe('AccountSection', () => {
  beforeEach(() => vi.clearAllMocks())

  it('marks a verified account', () => {
    render(<AccountSection user={USER} />)

    expect(screen.getByText('Doğrulanmış hesap')).toBeInTheDocument()
    expect(screen.queryByText(/tekrar gönder/)).not.toBeInTheDocument()
  })

  it('offers to resend the link for an unverified account', async () => {
    render(<AccountSection user={{ ...USER, email_verified: false }} />)

    expect(screen.getByText('Doğrulanmadı')).toBeInTheDocument()
    await userEvent.click(screen.getByRole('button', { name: /tekrar gönder/ }))

    expect(mocks.resend).toHaveBeenCalled()
  })

  it('shows a pending change that can be cancelled', async () => {
    render(<AccountSection user={{ ...USER, pending_email: 'ayse.yeni@example.com' }} />)

    expect(screen.getByText('ayse.yeni@example.com')).toBeInTheDocument()
    await userEvent.click(screen.getByRole('button', { name: 'Değişikliği iptal et' }))

    expect(mocks.cancel).toHaveBeenCalled()
  })

  it('asks for the new address and the password', async () => {
    render(<AccountSection user={USER} />)

    await userEvent.click(screen.getByRole('button', { name: 'E-posta adresini değiştir' }))
    await userEvent.type(screen.getByLabelText('Yeni e-posta adresi'), ' ayse.yeni@example.com ')
    await userEvent.type(screen.getByLabelText('Şifren'), 'guclu-sifre-123')
    await userEvent.click(screen.getByRole('button', { name: 'Doğrulama bağlantısı gönder' }))

    expect(mocks.changeEmail).toHaveBeenCalledWith(
      { newEmail: 'ayse.yeni@example.com', password: 'guclu-sifre-123' },
      expect.anything(),
    )
  })
})
