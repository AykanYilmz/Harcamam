import type { ReactNode } from 'react'

/** On/off toggle whose knob slides across the track. `knob` is drawn inside the knob. */
export function Switch({
  checked,
  onChange,
  label,
  knob,
  className = '',
}: {
  checked: boolean
  onChange(checked: boolean): void
  label: string
  knob?: ReactNode
  className?: string
}) {
  return (
    <button
      type="button"
      role="switch"
      aria-checked={checked}
      aria-label={label}
      title={label}
      onClick={() => onChange(!checked)}
      className={`relative inline-flex h-7 w-12 shrink-0 items-center rounded-full p-1 transition-colors duration-300 outline-none focus-visible:ring-2 focus-visible:ring-emerald-500 focus-visible:ring-offset-2 focus-visible:ring-offset-surface ${
        checked ? 'bg-emerald-600' : 'bg-line-strong'
      } ${className}`}
    >
      <span
        aria-hidden
        className={`flex size-5 items-center justify-center rounded-full bg-white text-slate-600 shadow-sm transition-transform duration-300 ease-drawer ${
          checked ? 'translate-x-5' : 'translate-x-0'
        }`}
      >
        {knob}
      </span>
    </button>
  )
}
