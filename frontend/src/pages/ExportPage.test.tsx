import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { AuthContext, type AuthContextValue } from '../auth/AuthContext.ts'
import { ExportPage } from './ExportPage.tsx'

const mocks = vi.hoisted(() => ({ mutate: vi.fn() }))

vi.mock('../api/reports.ts', () => ({
  useMonthlyReport: () => ({ isPending: false, isError: false, data: { month: '2026-10' } }),
}))
vi.mock('../api/exports.ts', () => ({
  useExportTransactions: () => ({ mutate: mocks.mutate, isPending: false, isError: false }),
}))

function renderPage(periodEndDay: number | null = null) {
  const auth = {
    status: 'authenticated',
    user: {
      id: '1',
      email: 'ayse@example.com',
      created_at: '2026-11-01T00:00:00Z',
      email_verified: true,
      pending_email: null,
      period_end_day: periodEndDay,
    },
  } as AuthContextValue
  render(
    <AuthContext.Provider value={auth}>
      <MemoryRouter>
        <ExportPage />
      </MemoryRouter>
    </AuthContext.Provider>,
  )
}

const dates = () => [screen.getByLabelText('Başlangıç'), screen.getByLabelText('Bitiş')]

describe('ExportPage', () => {
  beforeEach(() => mocks.mutate.mockReset())

  it('starts with the last six months that have data', () => {
    renderPage()

    expect(dates().map((input) => (input as HTMLInputElement).value)).toEqual([
      '2026-05-01',
      '2026-10-31',
    ])
  })

  it('follows the closing day the reports use', () => {
    renderPage(6)

    expect(dates().map((input) => (input as HTMLInputElement).value)).toEqual([
      '2026-04-07',
      '2026-10-06',
    ])
  })

  it('downloads the chosen range as Excel or CSV', async () => {
    renderPage()

    await userEvent.click(screen.getByRole('button', { name: 'Son 3 ay' }))
    await userEvent.click(screen.getByRole('button', { name: 'Excel indir' }))
    expect(mocks.mutate).toHaveBeenLastCalledWith({
      format: 'xlsx',
      start: '2026-08-01',
      end: '2026-10-31',
    })

    await userEvent.click(screen.getByRole('button', { name: 'CSV indir' }))
    expect(mocks.mutate).toHaveBeenLastCalledWith(expect.objectContaining({ format: 'csv' }))
  })
})
