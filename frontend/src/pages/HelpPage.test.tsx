import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router'
import { describe, expect, it } from 'vitest'
import { HelpPage } from './HelpPage.tsx'

function question(name: string) {
  return screen.getByText(name).closest('details')!
}

describe('HelpPage', () => {
  it('keeps only one answer open', async () => {
    render(
      <MemoryRouter>
        <HelpPage />
      </MemoryRouter>,
    )
    const files = question('Hangi dosyaları yükleyebilirim?')
    const privacy = question('Verilerim güvende mi?')

    await userEvent.click(screen.getByText('Hangi dosyaları yükleyebilirim?'))
    expect(files).toHaveAttribute('open')

    await userEvent.click(screen.getByText('Verilerim güvende mi?'))
    expect(privacy).toHaveAttribute('open')
    expect(files).not.toHaveAttribute('open')

    await userEvent.click(screen.getByText('Verilerim güvende mi?'))
    expect(privacy).not.toHaveAttribute('open')
  })
})
