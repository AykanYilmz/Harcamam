import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'
import type { Category, Transaction } from '../../api/types.ts'
import { CorrectionDialog } from './CorrectionDialog.tsx'

const transaction: Transaction = {
  id: 't1',
  statement_id: 's1',
  date: '2026-10-09',
  description: 'MIGROS KADIKÖY İSTANBUL',
  amount: '1088.40',
  type: 'expense',
  category_id: 'market',
  is_manually_categorized: false,
}

const category: Category = {
  id: 'food',
  name: 'Yemek',
  color: '#f97316',
  icon: 'utensils',
  kind: 'expense',
  is_default: true,
}

function renderDialog(onSave = vi.fn()) {
  render(
    <CorrectionDialog
      correction={{ transaction, category }}
      saving={false}
      error={null}
      onSave={onSave}
      onCancel={vi.fn()}
    />,
  )
  return onSave
}

describe('CorrectionDialog', () => {
  it('suggests the first word as the rule keyword and saves it', async () => {
    const onSave = renderDialog()

    expect(screen.getByLabelText('Anahtar kelime')).toHaveValue('MIGROS')
    await userEvent.click(screen.getByRole('button', { name: 'Kaydet' }))

    expect(onSave).toHaveBeenCalledWith('MIGROS')
  })

  it('saves an edited keyword', async () => {
    const onSave = renderDialog()

    const keyword = screen.getByLabelText('Anahtar kelime')
    await userEvent.clear(keyword)
    await userEvent.type(keyword, 'MIGROS KADIKÖY')
    await userEvent.click(screen.getByRole('button', { name: 'Kaydet' }))

    expect(onSave).toHaveBeenCalledWith('MIGROS KADIKÖY')
  })

  it('can change only this transaction', async () => {
    const onSave = renderDialog()

    await userEvent.click(screen.getByLabelText('Benzer işlemler için kural olarak kaydet'))
    expect(screen.queryByLabelText('Anahtar kelime')).not.toBeInTheDocument()
    await userEvent.click(screen.getByRole('button', { name: 'Kaydet' }))

    expect(onSave).toHaveBeenCalledWith(null)
  })

  it('does not save a rule without a keyword', async () => {
    const onSave = renderDialog()

    await userEvent.clear(screen.getByLabelText('Anahtar kelime'))

    expect(screen.getByRole('button', { name: 'Kaydet' })).toBeDisabled()
    expect(screen.getByText('Bir anahtar kelime girin.')).toBeInTheDocument()
    expect(onSave).not.toHaveBeenCalled()
  })
})
