import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { StatTile } from './StatTile.tsx'

function changeLine() {
  return screen.getByText('geçen aya göre', { exact: false }).closest('p')
}

describe('StatTile', () => {
  it('shows the amount in Turkish lira', () => {
    render(<StatTile label="Gelir" amount="45092.10" changePct={0.5} goodWhen="up" />)

    expect(screen.getByText('₺45.092,10')).toBeInTheDocument()
  })

  it('marks rising income as good news', () => {
    render(<StatTile label="Gelir" amount="100.00" changePct={20} goodWhen="up" />)

    expect(changeLine()).toHaveTextContent('%20 arttı · geçen aya göre')
    expect(changeLine()).toHaveClass('text-accent-fg')
  })

  it('marks rising spending as bad news', () => {
    render(<StatTile label="Gider" amount="100.00" changePct={26.1} goodWhen="down" />)

    expect(changeLine()).toHaveTextContent('%26,1 arttı')
    expect(changeLine()).toHaveClass('text-danger-fg')
  })

  it('marks falling spending as good news', () => {
    render(<StatTile label="Gider" amount="100.00" changePct={-10} goodWhen="down" />)

    expect(changeLine()).toHaveTextContent('%10 azaldı')
    expect(changeLine()).toHaveClass('text-accent-fg')
  })

  it('says so when there is no previous month to compare with', () => {
    render(<StatTile label="Gelir" amount="100.00" changePct={null} goodWhen="up" />)

    expect(screen.getByText('Geçen ayla karşılaştırma yok')).toBeInTheDocument()
  })
})
