import { useId, type InputHTMLAttributes } from 'react'

interface TextFieldProps extends InputHTMLAttributes<HTMLInputElement> {
  label: string
  error?: string
  hint?: string
}

export function TextField({ label, error, hint, className = '', ...props }: TextFieldProps) {
  const id = useId()
  const describedBy = error ? `${id}-error` : hint ? `${id}-hint` : undefined

  return (
    <div className={className}>
      <label htmlFor={id} className="mb-1 block text-sm font-medium text-fg-secondary">
        {label}
      </label>
      <input
        id={id}
        aria-invalid={error ? true : undefined}
        aria-describedby={describedBy}
        className="block w-full rounded-lg border border-line-strong bg-surface px-3 py-2 text-fg shadow-sm placeholder:text-fg-faint focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/30 focus:outline-none aria-invalid:border-rose-500"
        {...props}
      />
      {error ? (
        <p id={`${id}-error`} className="mt-1 text-sm text-danger-fg">
          {error}
        </p>
      ) : hint ? (
        <p id={`${id}-hint`} className="mt-1 text-sm text-fg-subtle">
          {hint}
        </p>
      ) : null}
    </div>
  )
}
