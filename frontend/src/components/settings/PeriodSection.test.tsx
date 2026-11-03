import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import type { User } from '../../api/types.ts'
import { PeriodSection } from './PeriodSection.tsx'

const mutate = vi.fn()
vi.mock('../../api/account.ts', () => ({
  useUpdateSettings: () => ({ mutate, isPending: false, isError: false }),
}))

const USER: User = {
  id: '1',
  email: 'ayse@example.com',
  created_at: '2026-11-01T10:00:00Z',
  email_verified: true,
  pending_email: null,
  period_end_day: null,
}

const select = () => screen.getByLabelText('Ay ne zaman bitsin?')

describe('PeriodSection', () => {
  beforeEach(() => {
    vi.useFakeTimers({ toFake: ['Date'] })
    vi.setSystemTime(new Date(2026, 10, 3))
  })
  afterEach(() => {
    vi.useRealTimers()
    mutate.mockReset()
  })

  it('uses calendar months by default', () => {
    render(<PeriodSection user={USER} />)

    expect(select()).toHaveValue('')
    expect(screen.getByText('1 Kas – 30 Kas')).toBeInTheDocument()
  })

  it('shows the current month of a closing day', () => {
    render(<PeriodSection user={{ ...USER, period_end_day: 6 }} />)

    expect(select()).toHaveValue('6')
    expect(screen.getByText('7 Eki – 6 Kas')).toBeInTheDocument()
  })

  it('saves a new closing day, and going back to calendar months', async () => {
    const { rerender } = render(<PeriodSection user={USER} />)

    await userEvent.selectOptions(select(), 'Her ayın 6. günü')
    expect(mutate).toHaveBeenLastCalledWith({ periodEndDay: 6 })

    rerender(<PeriodSection user={{ ...USER, period_end_day: 6 }} />)
    await userEvent.selectOptions(select(), 'Takvim ayı (ayın son günü)')
    expect(mutate).toHaveBeenLastCalledWith({ periodEndDay: null })
  })

  it('explains closing days that some months do not have', () => {
    render(<PeriodSection user={{ ...USER, period_end_day: 30 }} />)

    expect(screen.getByText(/olmayan aylarda dönem ayın son gününde biter/)).toBeInTheDocument()
  })
})
