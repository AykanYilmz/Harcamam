import { CircleAlert, CircleCheck } from 'lucide-react'
import { Link, useSearchParams } from 'react-router'
import { ApiError } from '../api/client.ts'
import { useVerifyEmail } from '../api/account.ts'
import { useAuth } from '../auth/useAuth.ts'
import { Logo } from '../components/Logo.tsx'
import { Card } from '../components/ui/Card.tsx'
import { Spinner } from '../components/ui/Spinner.tsx'

const linkButton =
  'mt-6 inline-flex rounded-lg bg-emerald-600 px-4 py-2 text-sm font-medium text-white hover:bg-emerald-700'

/** Opened from the link in a verification email; works whether or not the user is logged in. */
export function VerifyEmailPage() {
  const [searchParams] = useSearchParams()
  const token = searchParams.get('token') ?? ''
  const verification = useVerifyEmail(token)
  const { status } = useAuth()
  const next =
    status === 'authenticated'
      ? { to: '/', label: 'Uygulamaya dön' }
      : { to: '/giris', label: 'Giriş yap' }

  let content
  if (verification.isSuccess) {
    content = (
      <>
        <CircleCheck aria-hidden className="mx-auto size-12 text-accent-fg" />
        <h1 className="mt-4 text-xl font-semibold text-fg">E-posta adresin doğrulandı</h1>
        <p className="mt-2 text-sm text-fg-muted">{verification.data.email}</p>
        <Link to={next.to} className={linkButton}>
          {next.label}
        </Link>
      </>
    )
  } else if (token && verification.isPending) {
    content = (
      <div role="status" className="flex flex-col items-center text-fg-subtle">
        <Spinner className="size-8" />
        <p className="mt-3 text-sm">Doğrulanıyor…</p>
      </div>
    )
  } else {
    const taken = verification.error instanceof ApiError && verification.error.status === 409
    content = (
      <>
        <CircleAlert aria-hidden className="mx-auto size-12 text-danger-fg" />
        <h1 className="mt-4 text-xl font-semibold text-fg">
          {taken
            ? 'Bu adres başka bir hesapta kullanılıyor'
            : 'Bağlantı geçersiz ya da süresi dolmuş'}
        </h1>
        <p className="mt-2 text-sm text-fg-muted">
          Ayarlar sayfasından yeni bir doğrulama bağlantısı isteyebilirsin.
        </p>
        <Link to={next.to} className={linkButton}>
          {next.label}
        </Link>
      </>
    )
  }

  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-canvas px-4 py-10">
      <Logo className="mb-8 text-xl" />
      <Card className="w-full max-w-sm p-8 text-center">{content}</Card>
    </div>
  )
}
