import { BadgeCheck, MailWarning } from 'lucide-react'
import { useState, type FormEvent } from 'react'
import { useCancelEmailChange, useChangeEmail, useResendVerification } from '../../api/account.ts'
import type { User } from '../../api/types.ts'
import { errorMessage, RESEND_ERRORS } from '../../lib/errors.ts'
import { formatDate } from '../../lib/format.ts'
import { ErrorAlert } from '../ui/Alert.tsx'
import { Button } from '../ui/Button.tsx'
import { Card } from '../ui/Card.tsx'
import { TextField } from '../ui/TextField.tsx'

const CHANGE_ERRORS = {
  400: 'Şifre hatalı.',
  409: 'Bu e-posta adresiyle kayıtlı başka bir hesap var.',
  422: 'Geçerli ve mevcut adresinden farklı bir e-posta adresi gir.',
}

function VerificationBadge({ verified }: { verified: boolean }) {
  return verified ? (
    <span className="inline-flex items-center gap-1 rounded-full bg-accent-soft px-2.5 py-0.5 text-xs font-medium text-accent-fg">
      <BadgeCheck aria-hidden className="size-4" />
      Doğrulanmış hesap
    </span>
  ) : (
    <span className="inline-flex items-center gap-1 rounded-full bg-warning-soft px-2.5 py-0.5 text-xs font-medium text-warning-fg">
      <MailWarning aria-hidden className="size-4" />
      Doğrulanmadı
    </span>
  )
}

function ResendLink() {
  const resend = useResendVerification()
  if (resend.isSuccess) {
    return <span className="text-sm text-fg-subtle">Bağlantı gönderildi.</span>
  }
  return (
    <>
      <button
        type="button"
        onClick={() => resend.mutate()}
        disabled={resend.isPending}
        className="text-sm font-medium text-accent-fg hover:underline disabled:opacity-60"
      >
        Doğrulama bağlantısını tekrar gönder
      </button>
      {resend.isError && (
        <p className="mt-1 text-sm text-danger-fg">{errorMessage(resend.error, RESEND_ERRORS)}</p>
      )}
    </>
  )
}

function PendingChange({ pendingEmail }: { pendingEmail: string }) {
  const cancel = useCancelEmailChange()
  return (
    <div className="mt-4 rounded-lg bg-warning-soft px-4 py-3 text-sm text-warning-fg ring-1 ring-warning-line">
      <p>
        <strong>{pendingEmail}</strong> adresine doğrulama bağlantısı gönderildi. Bağlantıya
        tıkladığında e-posta adresin değişecek; o zamana kadar mevcut adresinle giriş yaparsın.
      </p>
      <div className="mt-2 flex flex-wrap items-center gap-4">
        <ResendLink />
        <button
          type="button"
          onClick={() => cancel.mutate()}
          disabled={cancel.isPending}
          className="text-sm font-medium underline underline-offset-2 hover:no-underline"
        >
          Değişikliği iptal et
        </button>
      </div>
      {cancel.isError && <p className="mt-1 text-danger-fg">{errorMessage(cancel.error)}</p>}
    </div>
  )
}

/** On success the pending-change box above takes over, so the form just closes. */
function ChangeEmailForm({ onClose }: { onClose(): void }) {
  const change = useChangeEmail()
  const [newEmail, setNewEmail] = useState('')
  const [password, setPassword] = useState('')

  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    change.mutate({ newEmail: newEmail.trim(), password }, { onSuccess: onClose })
  }

  return (
    <form onSubmit={submit} className="mt-4 space-y-4 border-t border-line pt-4" noValidate>
      {change.isError && <ErrorAlert>{errorMessage(change.error, CHANGE_ERRORS)}</ErrorAlert>}
      <TextField
        label="Yeni e-posta adresi"
        type="email"
        autoComplete="email"
        value={newEmail}
        onChange={(event) => setNewEmail(event.target.value)}
      />
      <TextField
        label="Şifren"
        type="password"
        autoComplete="current-password"
        hint="Hesabının güvenliği için şifreni tekrar gir."
        value={password}
        onChange={(event) => setPassword(event.target.value)}
      />
      <div className="flex justify-end gap-3">
        <Button variant="secondary" onClick={onClose} disabled={change.isPending}>
          Vazgeç
        </Button>
        <Button type="submit" loading={change.isPending} disabled={!newEmail.trim() || !password}>
          Doğrulama bağlantısı gönder
        </Button>
      </div>
    </form>
  )
}

export function AccountSection({ user }: { user: User }) {
  const [changing, setChanging] = useState(false)

  return (
    <Card>
      <h2 className="font-semibold text-fg">Hesap</h2>

      <dl className="mt-4 grid grid-cols-[auto_1fr] items-center gap-x-6 gap-y-3 text-sm">
        <dt className="text-fg-subtle">E-posta</dt>
        <dd className="flex flex-wrap items-center gap-2">
          <span className="font-medium text-fg">{user.email}</span>
          <VerificationBadge verified={user.email_verified} />
        </dd>
        <dt className="text-fg-subtle">Üyelik tarihi</dt>
        <dd className="text-fg">{formatDate(user.created_at)}</dd>
      </dl>

      {!user.email_verified && !user.pending_email && (
        <div className="mt-3">
          <ResendLink />
        </div>
      )}
      {user.pending_email && <PendingChange pendingEmail={user.pending_email} />}

      {changing ? (
        <ChangeEmailForm onClose={() => setChanging(false)} />
      ) : (
        <Button variant="secondary" className="mt-4" onClick={() => setChanging(true)}>
          E-posta adresini değiştir
        </Button>
      )}
    </Card>
  )
}
