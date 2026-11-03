import type { ReactNode } from 'react'
import { ThemeSwitcher } from '../theme/ThemeSwitcher.tsx'
import { Logo } from './Logo.tsx'
import { Card } from './ui/Card.tsx'

/** Centered card used by the login and register pages. */
export function AuthCard({
  title,
  subtitle,
  children,
  footer,
}: {
  title: string
  subtitle: string
  children: ReactNode
  footer: ReactNode
}) {
  return (
    <div className="relative flex min-h-screen flex-col items-center justify-center bg-canvas px-4 py-10">
      <ThemeSwitcher className="absolute top-4 right-4" />
      <Logo className="mb-8 text-xl" />
      <Card className="w-full max-w-sm p-6 sm:p-8">
        <h1 className="text-xl font-semibold text-fg">{title}</h1>
        <p className="mt-1 text-sm text-fg-subtle">{subtitle}</p>
        <div className="mt-6">{children}</div>
      </Card>
      <p className="mt-6 text-sm text-fg-muted">{footer}</p>
    </div>
  )
}
