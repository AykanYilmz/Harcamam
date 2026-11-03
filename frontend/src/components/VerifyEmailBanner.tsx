import { MailWarning, X } from 'lucide-react'
import { useResendVerification } from '../api/account.ts'
import { errorMessage, RESEND_ERRORS } from '../lib/errors.ts'

/** Reminds an unverified user to open the link; using the app is not blocked. */
export function VerifyEmailBanner({ email, onDismiss }: { email: string; onDismiss(): void }) {
  const resend = useResendVerification()

  return (
    <div
      role="status"
      className="flex items-start gap-3 border-b border-warning-line bg-warning-soft px-4 py-3 text-sm text-warning-fg md:px-8"
    >
      <MailWarning aria-hidden className="mt-0.5 size-5 shrink-0" />
      <div className="flex-1">
        <p>
          <strong>E-posta adresini doğrula.</strong> {email} adresine gönderdiğimiz bağlantıya
          tıkla.{' '}
          {resend.isSuccess ? (
            <span>Yeni bağlantı gönderildi, gelen kutunu kontrol et.</span>
          ) : (
            <button
              type="button"
              onClick={() => resend.mutate()}
              disabled={resend.isPending}
              className="font-semibold underline underline-offset-2 hover:no-underline disabled:opacity-60"
            >
              {resend.isPending ? 'Gönderiliyor…' : 'Bağlantıyı tekrar gönder'}
            </button>
          )}
        </p>
        {resend.isError && <p className="mt-1">{errorMessage(resend.error, RESEND_ERRORS)}</p>}
      </div>
      <button
        type="button"
        onClick={onDismiss}
        aria-label="Uyarıyı kapat"
        className="rounded p-0.5 hover:bg-amber-500/15"
      >
        <X aria-hidden className="size-4" />
      </button>
    </div>
  )
}
