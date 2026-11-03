import { ChevronLeft, ChevronRight } from 'lucide-react'
import { Button } from './Button.tsx'

interface PaginationProps {
  page: number
  pages: number
  pageSize: number
  total: number
  onPageChange(page: number): void
}

export function Pagination({ page, pages, pageSize, total, onPageChange }: PaginationProps) {
  if (total === 0) return null
  const first = (page - 1) * pageSize + 1
  const last = Math.min(page * pageSize, total)

  return (
    <nav aria-label="Sayfalar" className="flex items-center justify-between gap-3">
      <p className="text-sm text-fg-subtle">
        {total} işlemden {first}–{last} arası
      </p>
      <div className="flex items-center gap-2">
        <Button
          variant="secondary"
          onClick={() => onPageChange(page - 1)}
          disabled={page <= 1}
          aria-label="Önceki sayfa"
          className="px-2.5"
        >
          <ChevronLeft aria-hidden className="size-4" />
        </Button>
        <span className="text-sm text-fg-muted tabular-nums">
          {page} / {pages}
        </span>
        <Button
          variant="secondary"
          onClick={() => onPageChange(page + 1)}
          disabled={page >= pages}
          aria-label="Sonraki sayfa"
          className="px-2.5"
        >
          <ChevronRight aria-hidden className="size-4" />
        </Button>
      </div>
    </nav>
  )
}
