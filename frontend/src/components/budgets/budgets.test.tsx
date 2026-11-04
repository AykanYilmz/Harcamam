import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import type { Budget, BudgetReport, Category } from '../../api/types.ts'
import { BudgetAlerts } from '../dashboard/BudgetAlerts.tsx'
import { BudgetFormDialog } from './BudgetFormDialog.tsx'
import { BudgetRow } from './BudgetRow.tsx'

const mocks = vi.hoisted(() => ({
  report: undefined as unknown,
  create: vi.fn(),
  update: vi.fn(),
}))

vi.mock('../../api/budgets.ts', () => ({
  useBudgets: () => ({ data: mocks.report }),
  useCreateBudget: () => ({ mutate: mocks.create, isPending: false, error: null }),
  useUpdateBudget: () => ({ mutate: mocks.update, isPending: false, error: null }),
}))

const budget = (overrides: Partial<Budget>): Budget => ({
  id: 'b1',
  category_id: 'market',
  name: 'Market',
  color: '#22c55e',
  icon: 'shopping-cart',
  monthly_limit: '1000.00',
  spent: '400.00',
  remaining: '600.00',
  used_pct: 40,
  status: 'ok',
  projected: null,
  ...overrides,
})

const CATEGORIES: Category[] = [
  {
    id: 'market',
    name: 'Market',
    color: '#22c55e',
    icon: 'shopping-cart',
    kind: 'expense',
    is_default: true,
  },
  {
    id: 'food',
    name: 'Yemek',
    color: '#f97316',
    icon: 'utensils',
    kind: 'expense',
    is_default: true,
  },
]

function renderRow(overrides: Partial<Budget>) {
  render(
    <ul>
      <BudgetRow budget={budget(overrides)} onEdit={vi.fn()} onDelete={vi.fn()} />
    </ul>,
  )
}

describe('BudgetRow', () => {
  it('shows what is left when on track', () => {
    renderRow({})

    expect(screen.getByText(/₺600,00 kaldı/)).toBeInTheDocument()
    expect(screen.getByRole('progressbar')).toHaveAttribute('aria-valuenow', '40')
  })

  it('warns when the pace leads over the limit', () => {
    renderRow({ projected: '1240.00' })

    expect(
      screen.getByText(/Bu hızla ay sonunda ₺1.240,00 olur; limitin ₺240,00 üstü/),
    ).toBeInTheDocument()
  })

  it('caps the bar and says by how much the limit is exceeded', () => {
    renderRow({ spent: '1150.00', remaining: '-150.00', used_pct: 115, status: 'over' })

    expect(screen.getByText(/Limit ₺150,00 aşıldı/)).toBeInTheDocument()
    expect(screen.getByRole('progressbar')).toHaveAttribute('aria-valuenow', '100')
  })
})

describe('BudgetFormDialog', () => {
  beforeEach(() => {
    mocks.create.mockReset()
    mocks.update.mockReset()
  })

  it('adds a budget for the chosen category, reading Turkish amounts', async () => {
    render(<BudgetFormDialog open budget={null} available={CATEGORIES} onClose={vi.fn()} />)

    await userEvent.selectOptions(screen.getByLabelText('Kategori'), 'Yemek')
    await userEvent.type(screen.getByLabelText('Aylık limit (TL)'), '1.250,50')
    await userEvent.click(screen.getByRole('button', { name: 'Kaydet' }))

    expect(mocks.create).toHaveBeenCalledWith(
      { categoryId: 'food', monthlyLimit: '1250.50' },
      expect.anything(),
    )
  })

  it('rejects an amount that is not positive', async () => {
    render(<BudgetFormDialog open budget={null} available={CATEGORIES} onClose={vi.fn()} />)

    await userEvent.type(screen.getByLabelText('Aylık limit (TL)'), '0')
    await userEvent.click(screen.getByRole('button', { name: 'Kaydet' }))

    expect(screen.getByText(/Sıfırdan büyük bir tutar gir/)).toBeInTheDocument()
    expect(mocks.create).not.toHaveBeenCalled()
  })

  it('changes the limit of an existing budget', async () => {
    render(<BudgetFormDialog open budget={budget({})} available={[]} onClose={vi.fn()} />)

    const input = screen.getByLabelText('Aylık limit (TL)')
    expect(input).toHaveValue('1000,00')
    await userEvent.clear(input)
    await userEvent.type(input, '1500')
    await userEvent.click(screen.getByRole('button', { name: 'Kaydet' }))

    expect(mocks.update).toHaveBeenCalledWith({ id: 'b1', monthlyLimit: '1500' }, expect.anything())
  })
})

describe('BudgetAlerts', () => {
  const report = (budgets: Budget[]): BudgetReport => ({
    month: '2026-10',
    start: '2026-10-01',
    end: '2026-10-31',
    days_elapsed: null,
    days_in_period: 31,
    total_limit: '0',
    total_spent: '0',
    budgets,
  })

  function renderAlerts() {
    render(
      <MemoryRouter>
        <BudgetAlerts month="2026-10" />
      </MemoryRouter>,
    )
  }

  it('lists budgets close to or over their limit', () => {
    mocks.report = report([
      budget({ id: '1', name: 'Yemek', status: 'over', remaining: '-50.00', used_pct: 106.2 }),
      budget({ id: '2', name: 'Market', status: 'warning', used_pct: 90 }),
      budget({ id: '3', name: 'Giyim' }),
    ])
    renderAlerts()

    expect(screen.getByText(/limit ₺50,00 aşıldı/)).toBeInTheDocument()
    expect(screen.getByText(/%90 dolu/)).toBeInTheDocument()
    expect(screen.queryByText('Giyim')).not.toBeInTheDocument()
    expect(screen.getByRole('link', { name: /Bütçeler/ })).toHaveAttribute(
      'href',
      '/butceler?ay=2026-10',
    )
  })

  it('stays out of the way when every budget is on track', () => {
    mocks.report = report([budget({})])
    renderAlerts()

    expect(screen.queryByText('Bütçe uyarıları')).not.toBeInTheDocument()
  })
})
