import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import type { Subscription, SubscriptionReport } from '../api/types.ts'
import { SubscriptionsPage } from './SubscriptionsPage.tsx'

const mocks = vi.hoisted(() => ({ report: null as unknown, dismiss: vi.fn(), restore: vi.fn() }))

vi.mock('../api/subscriptions.ts', () => ({
  useSubscriptions: () => ({ isPending: false, isError: false, data: mocks.report }),
  useDismissSubscription: () => ({ mutate: mocks.dismiss, isPending: false, isError: false }),
  useRestoreSubscription: () => ({ mutate: mocks.restore, isPending: false }),
}))

const subscription = (overrides: Partial<Subscription>): Subscription => ({
  key: 'netflix com',
  name: 'NETFLIX.COM',
  category_id: 'c',
  category_name: 'Abonelikler',
  color: '#6366f1',
  icon: 'repeat',
  amount: '189.99',
  yearly_amount: '2279.88',
  previous_amount: null,
  charge_count: 4,
  first_charge: '2026-06-05',
  last_charge: '2026-09-05',
  next_charge: '2026-10-05',
  active: true,
  ...overrides,
})

const report = (overrides: Partial<SubscriptionReport>): SubscriptionReport => ({
  monthly_total: '189.99',
  yearly_total: '2279.88',
  subscriptions: [subscription({})],
  dismissed: [],
  ...overrides,
})

describe('SubscriptionsPage', () => {
  beforeEach(() => {
    mocks.dismiss.mockReset()
    mocks.restore.mockReset()
  })

  it('totals what the active ones cost and shows the next charge', () => {
    mocks.report = report({})
    render(<SubscriptionsPage />)

    expect(screen.getByText('₺189,99', { selector: 'p.text-2xl' })).toBeInTheDocument()
    expect(screen.getByText('₺2.279,88')).toBeInTheDocument()
    expect(screen.getByText('Sonraki: 5 Eki 2026')).toBeInTheDocument()
  })

  it('points out a price rise', () => {
    mocks.report = report({ subscriptions: [subscription({ previous_amount: '149.99' })] })
    render(<SubscriptionsPage />)

    expect(screen.getByText(/Zam: ₺149,99 → ₺189,99/)).toBeInTheDocument()
  })

  it('lists stopped ones separately with their last charge', () => {
    mocks.report = report({
      subscriptions: [subscription({ name: 'ORNEK SPOR', active: false, next_charge: null })],
    })
    render(<SubscriptionsPage />)

    expect(screen.getByRole('heading', { name: 'Durmuş görünenler' })).toBeInTheDocument()
    expect(screen.getByText('Son ödeme: 5 Eyl 2026')).toBeInTheDocument()
  })

  it('dismisses a false positive and restores a dismissed one', async () => {
    mocks.report = report({ dismissed: [{ key: 'yemeksepeti', name: 'YEMEKSEPETİ' }] })
    render(<SubscriptionsPage />)

    await userEvent.click(screen.getByRole('button', { name: 'Abonelik değil' }))
    expect(mocks.dismiss).toHaveBeenCalledWith('netflix com')

    await userEvent.click(screen.getByRole('button', { name: 'Gizlenenler (1)' }))
    await userEvent.click(screen.getByRole('button', { name: 'Geri al' }))
    expect(mocks.restore).toHaveBeenCalledWith('yemeksepeti')
  })

  it('explains what it needs when nothing is found', () => {
    mocks.report = report({ subscriptions: [], monthly_total: '0.00', yearly_total: '0.00' })
    render(<SubscriptionsPage />)

    expect(screen.getByText('Düzenli ödeme bulunamadı')).toBeInTheDocument()
  })
})
