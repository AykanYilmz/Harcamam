import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import type { Category, UncategorizedReport } from '../api/types.ts'
import { UncategorizedPage } from './UncategorizedPage.tsx'

const CATEGORIES: Category[] = [
  {
    id: 'market',
    name: 'Market',
    color: '#22c55e',
    icon: 'shopping-cart',
    kind: 'expense',
    is_default: true,
  },
  { id: 'other', name: 'Diğer', color: '#94a3b8', icon: 'tag', kind: 'expense', is_default: true },
  {
    id: 'travel',
    name: 'Ulaşım',
    color: '#0ea5e9',
    icon: 'car',
    kind: 'expense',
    is_default: true,
  },
]

const transaction = (id: string, description: string, amount: string) => ({
  id,
  statement_id: 's',
  date: '2026-09-10',
  description,
  amount,
  type: 'expense' as const,
  category_id: 'other',
  is_manually_categorized: false,
})

const REPORT: UncategorizedReport = {
  transaction_count: 3,
  merchants: [
    {
      name: 'ÖRNEK KASAP',
      keyword: 'ÖRNEK KASAP',
      amount: '500.00',
      transactions: [
        transaction('1', 'ÖRNEK KASAP BOLU', '300.00'),
        transaction('2', 'ÖRNEK KASAP BOLU', '200.00'),
      ],
    },
    {
      name: 'ÖRNEKBILET.COM',
      keyword: 'ÖRNEKBILET.COM',
      amount: '100.00',
      transactions: [transaction('3', 'S/ÖRNEKBILET.COM', '100.00')],
    },
  ],
}

const mocks = vi.hoisted(() => ({
  report: null as unknown,
  rule: {
    mutate: vi.fn(),
    isPending: false,
    isSuccess: false,
    isError: false,
    variables: undefined as unknown,
  },
}))

vi.mock('../api/transactions.ts', () => ({
  useUncategorized: () => ({ isPending: false, isError: false, data: mocks.report }),
}))
vi.mock('../api/categories.ts', () => ({
  useCategories: () => ({ isPending: false, isError: false, data: CATEGORIES }),
  useCreateRule: () => mocks.rule,
}))

function renderPage() {
  render(
    <MemoryRouter>
      <UncategorizedPage />
    </MemoryRouter>,
  )
}

describe('UncategorizedPage', () => {
  beforeEach(() => {
    mocks.report = REPORT
    mocks.rule = {
      mutate: vi.fn(),
      isPending: false,
      isSuccess: false,
      isError: false,
      variables: undefined,
    }
  })

  it('lists merchants with their totals', () => {
    renderPage()

    expect(screen.getByRole('heading', { name: '2 yerden 3 işlem tanınmadı' })).toBeInTheDocument()
    expect(screen.getByText('ÖRNEK KASAP')).toBeInTheDocument()
    expect(screen.getByText('2 işlem · ₺500,00')).toBeInTheDocument()
  })

  it('saves the merchant as a rule for the chosen category', async () => {
    renderPage()

    await userEvent.selectOptions(screen.getByLabelText('ÖRNEK KASAP için kategori'), 'Market')

    expect(mocks.rule.mutate).toHaveBeenCalledWith({
      keyword: 'ÖRNEK KASAP',
      category_id: 'market',
      apply_to_existing: true,
    })
  })

  it('does not offer the fallback category itself', () => {
    renderPage()

    expect(screen.getAllByRole('option', { name: 'Market' })).toHaveLength(2)
    expect(screen.queryByRole('option', { name: 'Diğer' })).not.toBeInTheDocument()
  })

  it('confirms the chosen category once saved', () => {
    mocks.rule = { ...mocks.rule, isSuccess: true, variables: { category_id: 'travel' } }
    renderPage()

    expect(screen.getAllByText('Ulaşım')).toHaveLength(2)
    expect(screen.queryByLabelText('ÖRNEK KASAP için kategori')).not.toBeInTheDocument()
  })

  it('shows the transactions behind a merchant', async () => {
    renderPage()

    await userEvent.click(screen.getByRole('button', { name: /ÖRNEK KASAP/ }))

    expect(screen.getAllByText('ÖRNEK KASAP BOLU')).toHaveLength(2)
  })

  it('celebrates when nothing is left', () => {
    mocks.report = { transaction_count: 0, merchants: [] }
    renderPage()

    expect(screen.getByText('Tanınmayan işlem kalmadı')).toBeInTheDocument()
  })
})
