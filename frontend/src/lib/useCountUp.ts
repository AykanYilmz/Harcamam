import { useEffect, useRef, useState } from 'react'

/**
 * A number that counts up to `target` (from 0 on first render, then from wherever it is
 * when `target` changes), easing out over `durationMs`.
 */
export function useCountUp(target: number, durationMs = 800): number {
  const [value, setValue] = useState(0)
  // What is on screen right now, so a new target continues from it instead of jumping.
  const shown = useRef(0)

  useEffect(() => {
    if (typeof requestAnimationFrame === 'undefined') return
    const from = shown.current
    const start = performance.now()
    let frame = 0

    const tick = (now: number) => {
      const progress = Math.min((now - start) / durationMs, 1)
      const eased = 1 - (1 - progress) ** 3
      // Land exactly on the target: floating-point steps could stop a hair short.
      const next = progress === 1 ? target : from + (target - from) * eased
      shown.current = next
      setValue(next)
      if (progress < 1) frame = requestAnimationFrame(tick)
    }
    frame = requestAnimationFrame(tick)
    return () => cancelAnimationFrame(frame)
  }, [target, durationMs])

  return value
}
