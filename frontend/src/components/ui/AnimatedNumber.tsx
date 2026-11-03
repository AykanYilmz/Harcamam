import { useCountUp } from '../../lib/useCountUp.ts'

interface AnimatedNumberProps {
  value: number
  format(value: number): string
}

/**
 * Counts up to `value`. Screen readers get only the final value: the counting copy is
 * hidden from them, so they don't read out every intermediate number.
 */
export function AnimatedNumber({ value, format }: AnimatedNumberProps) {
  const shown = useCountUp(value)
  return (
    <>
      <span aria-hidden>{format(shown)}</span>
      <span className="sr-only">{format(value)}</span>
    </>
  )
}
