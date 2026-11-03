import { Monitor, Moon, Sun, type LucideIcon } from 'lucide-react'
import { useState, type FormEvent, type ReactNode } from 'react'
import { useNavigate } from 'react-router'
import { useAuth } from '../auth/useAuth.ts'
import { ErrorAlert } from '../components/ui/Alert.tsx'
import { Button } from '../components/ui/Button.tsx'
import { Card } from '../components/ui/Card.tsx'
import { Dialog } from '../components/ui/Dialog.tsx'
import { SuccessNotice } from '../components/ui/Notice.tsx'
import { TextField } from '../components/ui/TextField.tsx'
import { errorMessage } from '../lib/errors.ts'
import { formatDate } from '../lib/format.ts'
import type { ThemePreference } from '../theme/ThemeContext.ts'
import { useTheme } from '../theme/useTheme.ts'

const MIN_PASSWORD_LENGTH = 8
const WRONG_PASSWORD = { 400: 'Şifre hatalı.' }

const THEMES: { value: ThemePreference; label: string; icon: LucideIcon }[] = [
  { value: 'light', label: 'Açık', icon: Sun },
  { value: 'dark', label: 'Koyu', icon: Moon },
  { value: 'system', label: 'Sistem', icon: Monitor },
]

function Section({ title, children }: { title: string; children: ReactNode }) {
  return (
    <Card>
      <h2 className="font-semibold text-fg">{title}</h2>
      <div className="mt-4">{children}</div>
    </Card>
  )
}

function ThemeSection() {
  const { preference, setPreference } = useTheme()
  return (
    <Section title="Görünüm">
      <div role="radiogroup" aria-label="Tema" className="grid grid-cols-3 gap-3">
        {THEMES.map(({ value, label, icon: Icon }) => (
          <button
            key={value}
            type="button"
            role="radio"
            aria-checked={preference === value}
            onClick={() => setPreference(value)}
            className={`flex flex-col items-center gap-2 rounded-xl px-3 py-4 text-sm font-medium ring-1 transition-colors ${
              preference === value
                ? 'bg-accent-soft text-accent-fg ring-emerald-500'
                : 'text-fg-muted ring-line-strong hover:bg-surface-muted'
            }`}
          >
            <Icon aria-hidden className="size-5" />
            {label}
          </button>
        ))}
      </div>
      <p className="mt-3 text-xs text-fg-subtle">
        "Sistem", bilgisayarının ya da telefonunun ayarını izler.
      </p>
    </Section>
  )
}

function PasswordSection() {
  const { changePassword } = useAuth()
  const [current, setCurrent] = useState('')
  const [next, setNext] = useState('')
  const [confirm, setConfirm] = useState('')
  const [fieldError, setFieldError] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [saving, setSaving] = useState(false)
  const [done, setDone] = useState(false)

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setError(null)
    setDone(false)
    if (next.length < MIN_PASSWORD_LENGTH) {
      setFieldError(`Yeni şifre en az ${MIN_PASSWORD_LENGTH} karakter olmalı.`)
      return
    }
    if (next !== confirm) {
      setFieldError('Şifreler eşleşmiyor.')
      return
    }
    setFieldError(null)
    setSaving(true)
    try {
      await changePassword(current, next)
      setCurrent('')
      setNext('')
      setConfirm('')
      setDone(true)
    } catch (err) {
      setError(errorMessage(err, { 400: 'Mevcut şifre hatalı.' }))
    } finally {
      setSaving(false)
    }
  }

  return (
    <Section title="Şifre değiştir">
      <form onSubmit={submit} className="space-y-4" noValidate>
        {done && (
          <SuccessNotice onDismiss={() => setDone(false)}>
            Şifren değiştirildi. Diğer cihazlardaki oturumların kapatıldı.
          </SuccessNotice>
        )}
        {error && <ErrorAlert>{error}</ErrorAlert>}
        <TextField
          label="Mevcut şifre"
          type="password"
          autoComplete="current-password"
          value={current}
          onChange={(event) => setCurrent(event.target.value)}
        />
        <TextField
          label="Yeni şifre"
          type="password"
          autoComplete="new-password"
          hint={`En az ${MIN_PASSWORD_LENGTH} karakter`}
          value={next}
          onChange={(event) => setNext(event.target.value)}
        />
        <TextField
          label="Yeni şifre (tekrar)"
          type="password"
          autoComplete="new-password"
          value={confirm}
          error={fieldError ?? undefined}
          onChange={(event) => setConfirm(event.target.value)}
        />
        <div className="flex justify-end">
          <Button type="submit" loading={saving} disabled={!current || !next}>
            Şifreyi değiştir
          </Button>
        </div>
      </form>
    </Section>
  )
}

function DeleteAccountSection() {
  const { deleteAccount, logout } = useAuth()
  const navigate = useNavigate()
  const [open, setOpen] = useState(false)
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [deleting, setDeleting] = useState(false)

  function close() {
    setOpen(false)
    setPassword('')
    setError(null)
  }

  async function confirmDelete(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setDeleting(true)
    try {
      await deleteAccount(password)
      navigate('/giris', { replace: true, state: { notice: 'Hesabın ve tüm verilerin silindi.' } })
      logout()
    } catch (err) {
      setError(errorMessage(err, WRONG_PASSWORD))
      setDeleting(false)
    }
  }

  return (
    <Card className="ring-danger-line">
      <h2 className="font-semibold text-danger-fg">Hesabı sil</h2>
      <p className="mt-2 text-sm text-fg-muted">
        Hesabın; yüklediğin ekstreler, işlemlerin, kategorilerin ve kuralların ile birlikte kalıcı
        olarak silinir. Bu işlem geri alınamaz.
      </p>
      <Button variant="danger" className="mt-4" onClick={() => setOpen(true)}>
        Hesabımı sil
      </Button>

      <Dialog open={open} title="Hesabını silmek istediğine emin misin?" onClose={close}>
        <form onSubmit={confirmDelete} className="space-y-4">
          <p>Onaylamak için şifreni gir. Silinen veriler geri getirilemez.</p>
          {error && <ErrorAlert>{error}</ErrorAlert>}
          <TextField
            label="Şifre"
            type="password"
            autoComplete="current-password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
          />
          <div className="flex justify-end gap-3">
            <Button variant="secondary" onClick={close} disabled={deleting}>
              Vazgeç
            </Button>
            <Button type="submit" variant="danger" loading={deleting} disabled={!password}>
              Hesabımı kalıcı olarak sil
            </Button>
          </div>
        </form>
      </Dialog>
    </Card>
  )
}

export function SettingsPage() {
  const { user } = useAuth()

  return (
    <div className="mx-auto max-w-2xl space-y-4">
      <Section title="Hesap">
        <dl className="grid grid-cols-[auto_1fr] gap-x-6 gap-y-2 text-sm">
          <dt className="text-fg-subtle">E-posta</dt>
          <dd className="font-medium text-fg">{user?.email}</dd>
          <dt className="text-fg-subtle">Üyelik tarihi</dt>
          <dd className="text-fg">{user && formatDate(user.created_at)}</dd>
        </dl>
      </Section>
      <ThemeSection />
      <PasswordSection />
      <DeleteAccountSection />
    </div>
  )
}
