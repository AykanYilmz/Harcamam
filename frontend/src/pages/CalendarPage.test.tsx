import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router'
import { describe, expect, it, vi } from 'vitest'
import { CalendarPage } from './CalendarPage.tsx'

const requested = vi.hoisted(() => ({ transactionDays: [] as string[] }))

vi.mock('../api/reports.ts', () => ({
  useMonthlyReport: () => ({ data: { month: '2026-10' }, isError: false }),
  useDailySpending: () => ({
    data: {
      month: '2026-10',
      days: [
        { date: '2026-10-01', amount: '15000.00' },
        { date: '2026-10-02', amount: '1432.60' },
        { date: '2026-10-03', amount: '0.00' },
      ],
    },
    isError: false,
  }),
}))

vi.mock('../api/categories.ts', () => ({
  useCategories: () => ({
    data: [{ id: 'kira', name: 'Kira', color: '#a855f7', icon: 'home', kind: 'expense' }],
  }),
}))

vi.mock('../api/transactions.ts', () => ({
  useTransactions: (filters: { dateFrom: string }) => {
    requested.transactionDays.push(filters.dateFrom)
    return {
      isPending: false,
      data: {
        total: 1,
        items: [
          {
            id: 't1',
            description: 'KİRA ÖDEMESİ',
            amount: '15000.00',
            type: 'expense',
            category_id: 'kira',
          },
        ],
      },
    }
  },
}))

function renderCalendar() {
  render(
    <MemoryRouter initialEntries={['/takvim']}>
      <CalendarPage />
    </MemoryRouter>,
  )
}

describe('CalendarPage', () => {
  it('lays out the month with its spending', () => {
    renderCalendar()

    expect(screen.getAllByRole('button', { name: /Eki 2026/ })).toHaveLength(31)
    expect(
      screen.getByRole('button', { name: '1 Eki 2026: ₺15.000,00 harcama' }),
    ).toBeInTheDocument()
    expect(screen.getByRole('button', { name: '3 Eki 2026: harcama yok' })).toBeInTheDocument()
  })

  it('shows the transactions of a chosen day', async () => {
    renderCalendar()
    expect(screen.getByText('İşlemlerini görmek için bir güne tıkla.')).toBeInTheDocument()

    await userEvent.click(screen.getByRole('button', { name: /^1 Eki 2026/ }))

    expect(requested.transactionDays).toContain('2026-10-01')
    expect(screen.getByText('KİRA ÖDEMESİ')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /^1 Eki 2026/ })).toHaveAttribute(
      'aria-pressed',
      'true',
    )
  })
})
