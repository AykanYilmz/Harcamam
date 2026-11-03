import { useState, type FormEvent } from 'react'
import { Link, useLocation, useNavigate } from 'react-router'
import { useAuth } from '../auth/useAuth.ts'
import { AuthCard } from '../components/AuthCard.tsx'
import { ErrorAlert } from '../components/ui/Alert.tsx'
import { Button } from '../components/ui/Button.tsx'
import { TextField } from '../components/ui/TextField.tsx'
import { errorMessage } from '../lib/errors.ts'

export function LoginPage() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setError(null)
    setSubmitting(true)
    try {
      await login(email.trim(), password)
      // Back to the page that sent the user here, if any.
      const from = (location.state as { from?: string } | null)?.from
      navigate(from ?? '/', { replace: true })
    } catch (err) {
      setError(errorMessage(err, { 401: 'E-posta adresi veya şifre hatalı.' }))
      setSubmitting(false)
    }
  }

  return (
    <AuthCard
      title="Giriş yap"
      subtitle="Harcamalarını görmek için hesabına giriş yap."
      footer={
        <>
          Hesabın yok mu?{' '}
          <Link to="/kayit" className="font-medium text-emerald-700 hover:underline">
            Kayıt ol
          </Link>
        </>
      }
    >
      <form onSubmit={handleSubmit} className="space-y-4" noValidate>
        {error && <ErrorAlert>{error}</ErrorAlert>}
        <TextField
          label="E-posta"
          type="email"
          autoComplete="email"
          required
          value={email}
          onChange={(event) => setEmail(event.target.value)}
        />
        <TextField
          label="Şifre"
          type="password"
          autoComplete="current-password"
          required
          value={password}
          onChange={(event) => setPassword(event.target.value)}
        />
        <Button type="submit" loading={submitting} className="w-full">
          Giriş yap
        </Button>
      </form>
    </AuthCard>
  )
}
