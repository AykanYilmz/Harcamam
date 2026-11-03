import { useId, type SelectHTMLAttributes } from 'react'

export const selectClass =
  'block w-full rounded-lg border border-line-strong bg-surface px-3 py-2 text-sm text-fg shadow-sm focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/30 focus:outline-none'

interface SelectFieldProps extends SelectHTMLAttributes<HTMLSelectElement> {
  label: string
}

export function SelectField({ label, className = '', children, ...props }: SelectFieldProps) {
  const id = useId()
  return (
    <div className={className}>
      <label htmlFor={id} className="mb-1 block text-sm font-medium text-fg-secondary">
        {label}
      </label>
      <select id={id} className={selectClass} {...props}>
        {children}
      </select>
    </div>
  )
}
