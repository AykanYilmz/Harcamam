import { useEffect, useRef, type ReactNode } from 'react'

interface DialogProps {
  open: boolean
  title: string
  onClose(): void
  children: ReactNode
  /** Buttons, right-aligned under the content. */
  footer?: ReactNode
}

/**
 * Built on the native <dialog>: the browser handles focus trapping, Escape to close and
 * hiding the rest of the page from screen readers.
 */
export function Dialog({ open, title, onClose, children, footer }: DialogProps) {
  const dialogRef = useRef<HTMLDialogElement>(null)

  useEffect(() => {
    const dialog = dialogRef.current
    if (!dialog) return
    if (open && !dialog.open) dialog.showModal()
    if (!open && dialog.open) dialog.close()
  }, [open])

  return (
    <dialog
      ref={dialogRef}
      aria-label={title}
      onCancel={(event) => {
        event.preventDefault()
        onClose()
      }}
      className="m-auto w-[calc(100%-2rem)] max-w-md rounded-2xl bg-surface p-6 text-fg shadow-xl ring-1 ring-line open:animate-dialog-in backdrop:animate-fade-in backdrop:bg-slate-950/50"
    >
      {open && (
        <>
          <h2 className="text-lg font-semibold">{title}</h2>
          <div className="mt-3 text-sm text-fg-muted">{children}</div>
          {footer && <div className="mt-6 flex justify-end gap-3">{footer}</div>}
        </>
      )}
    </dialog>
  )
}
