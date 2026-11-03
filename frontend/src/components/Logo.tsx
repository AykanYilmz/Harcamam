import { Wallet } from 'lucide-react'

export function LogoMark() {
  return (
    <span className="flex size-8 shrink-0 items-center justify-center rounded-lg bg-emerald-600 text-white">
      <Wallet aria-hidden className="size-5" />
    </span>
  )
}

export function Logo({ className = '' }: { className?: string }) {
  return (
    <span className={`inline-flex items-center gap-2 font-bold text-fg ${className}`}>
      <LogoMark />
      Harcamam
    </span>
  )
}
