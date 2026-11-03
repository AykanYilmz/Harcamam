import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'
import { MonthPicker } from './MonthPicker.tsx'

describe('MonthPicker', () => {
  it('shows the days a closing-day month covers', () => {
    render(
      <MonthPicker
        month="2026-10"
        onChange={vi.fn()}
        latest="2026-11"
        range={{ start: '2026-09-07', end: '2026-10-06' }}
      />,
    )

    expect(screen.getByText('Ekim 2026')).toBeInTheDocument()
    expect(screen.getByText('7 Eyl – 6 Eki')).toBeInTheDocument()
  })

  it('moves between months up to the latest one', async () => {
    const onChange = vi.fn()
    const { rerender } = render(
      <MonthPicker month="2026-10" onChange={onChange} latest="2026-11" />,
    )

    await userEvent.click(screen.getByRole('button', { name: 'Sonraki ay' }))
    expect(onChange).toHaveBeenCalledWith('2026-11')

    rerender(<MonthPicker month="2026-11" onChange={onChange} latest="2026-11" />)
    expect(screen.getByRole('button', { name: 'Sonraki ay' })).toBeDisabled()
    await userEvent.click(screen.getByRole('button', { name: 'Önceki ay' }))
    expect(onChange).toHaveBeenLastCalledWith('2026-10')
  })
})
