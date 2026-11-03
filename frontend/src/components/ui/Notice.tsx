import { CircleCheck, X } from 'lucide-react'
import type { ReactNode } from 'react'

/** A dismissible success message, announced to screen readers. */
export function SuccessNotice({ children, onDismiss }: { children: ReactNode; onDismiss(): void }) {
  return (
    <div
      role="status"
      className="flex items-start gap-2 rounded-lg bg-accent-soft px-3 py-2 text-sm text-accent-fg ring-1 ring-emerald-500/30"
    >
      <CircleCheck aria-hidden className="mt-0.5 size-4 shrink-0" />
      <span className="flex-1">{children}</span>
      <button
        type="button"
        onClick={onDismiss}
        aria-label="Kapat"
        className="rounded p-0.5 hover:bg-emerald-500/15"
      >
        <X aria-hidden className="size-4" />
      </button>
    </div>
  )
}
