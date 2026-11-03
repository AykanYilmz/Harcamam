import { useState, type FormEvent } from 'react'
import { Link, useNavigate } from 'react-router'
import { useAuth } from '../auth/useAuth.ts'
import { AuthCard } from '../components/AuthCard.tsx'
import { ErrorAlert } from '../components/ui/Alert.tsx'
import { Button } from '../components/ui/Button.tsx'
import { TextField } from '../components/ui/TextField.tsx'
import { errorMessage } from '../lib/errors.ts'

// Mirrors the backend's rules so most mistakes are caught before a request is sent.
const MIN_PASSWORD_LENGTH = 8
const MAX_PASSWORD_LENGTH = 128

interface FieldErrors {
  email?: string
  password?: string
  passwordConfirm?: string
}

function validate(email: string, password: string, passwordConfirm: string): FieldErrors {
  const errors: FieldErrors = {}
  if (!/^\S+@\S+\.\S+$/.test(email)) errors.email = 'Geçerli bir e-posta adresi girin.'
  if (password.length < MIN_PASSWORD_LENGTH) {
    errors.password = `Şifre en az ${MIN_PASSWORD_LENGTH} karakter olmalı.`
  } else if (password.length > MAX_PASSWORD_LENGTH) {
    errors.password = `Şifre en fazla ${MAX_PASSWORD_LENGTH} karakter olabilir.`
  }
  if (passwordConfirm !== password) errors.passwordConfirm = 'Şifreler eşleşmiyor.'
  return errors
}

export function RegisterPage() {
  const { register } = useAuth()
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [passwordConfirm, setPasswordConfirm] = useState('')
  const [fieldErrors, setFieldErrors] = useState<FieldErrors>({})
  const [error, setError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setError(null)
    const errors = validate(email.trim(), password, passwordConfirm)
    setFieldErrors(errors)
    if (Object.keys(errors).length > 0) return

    setSubmitting(true)
    try {
      await register(email.trim(), password)
      navigate('/', { replace: true })
    } catch (err) {
      setError(errorMessage(err, { 409: 'Bu e-posta adresiyle zaten bir hesap var.' }))
      setSubmitting(false)
    }
  }

  return (
    <AuthCard
      title="Kayıt ol"
      subtitle="Ekstreni yükle, harcamaların otomatik kategorilensin."
      footer={
        <>
          Zaten hesabın var mı?{' '}
          <Link to="/giris" className="font-medium text-accent-fg hover:underline">
            Giriş yap
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
          value={email}
          error={fieldErrors.email}
          onChange={(event) => setEmail(event.target.value)}
        />
        <TextField
          label="Şifre"
          type="password"
          autoComplete="new-password"
          value={password}
          error={fieldErrors.password}
          hint={`En az ${MIN_PASSWORD_LENGTH} karakter`}
          onChange={(event) => setPassword(event.target.value)}
        />
        <TextField
          label="Şifre (tekrar)"
          type="password"
          autoComplete="new-password"
          value={passwordConfirm}
          error={fieldErrors.passwordConfirm}
          onChange={(event) => setPasswordConfirm(event.target.value)}
        />
        <Button type="submit" loading={submitting} className="w-full">
          Hesap oluştur
        </Button>
      </form>
    </AuthCard>
  )
}
