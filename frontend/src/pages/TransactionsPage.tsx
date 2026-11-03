import { Upload } from 'lucide-react'
import { useState } from 'react'
import { Link, useSearchParams } from 'react-router'
import { useCategories } from '../api/categories.ts'
import { useBulkCategory, useCorrectCategory, useTransactions } from '../api/transactions.ts'
import type { Transaction } from '../api/types.ts'
import { BulkBar } from '../components/transactions/BulkBar.tsx'
import {
  CorrectionDialog,
  type PendingCorrection,
} from '../components/transactions/CorrectionDialog.tsx'
import { TransactionFiltersBar } from '../components/transactions/TransactionFiltersBar.tsx'
import { TransactionList } from '../components/transactions/TransactionList.tsx'
import { ErrorAlert } from '../components/ui/Alert.tsx'
import { Card } from '../components/ui/Card.tsx'
import { SuccessNotice } from '../components/ui/Notice.tsx'
import { Pagination } from '../components/ui/Pagination.tsx'
import { PageLoader, Spinner } from '../components/ui/Spinner.tsx'
import { errorMessage } from '../lib/errors.ts'
import {
  filtersFromParams,
  filtersToParams,
  hasActiveFilters,
  PAGE_SIZE,
  type TransactionFilters,
} from '../lib/transactionFilters.ts'
import { useDebouncedValue } from '../lib/useDebouncedValue.ts'

function correctionMessage(ruleKeyword: string | null, updated: number): string {
  if (!ruleKeyword) return 'Kategori güncellendi.'
  const others = updated > 0 ? ` ve ${updated} benzer işleme uygulandı` : ''
  return `Kategori güncellendi. "${ruleKeyword}" kuralı kaydedildi${others}.`
}

export function TransactionsPage() {
  const [searchParams, setSearchParams] = useSearchParams()
  const filters = filtersFromParams(searchParams)
  // The URL follows every keystroke; the request waits until typing pauses.
  const debouncedQuery = useDebouncedValue(filters.query)
  const transactions = useTransactions({ ...filters, query: debouncedQuery })
  const categories = useCategories()
  const correct = useCorrectCategory()
  const bulk = useBulkCategory()

  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set())
  const [pending, setPending] = useState<PendingCorrection | null>(null)
  const [notice, setNotice] = useState<string | null>(null)

  function updateFilters(changes: Partial<TransactionFilters>) {
    // Any filter change starts again from the first page with nothing selected.
    const next = { ...filters, page: 1, ...changes }
    setSearchParams(filtersToParams(next), { replace: 'query' in changes })
    setSelectedIds(new Set())
  }

  function clearFilters() {
    setSearchParams(new URLSearchParams())
    setSelectedIds(new Set())
  }

  if (categories.isPending || (transactions.isPending && !transactions.data)) {
    return <PageLoader />
  }
  if (categories.isError) return <ErrorAlert>{errorMessage(categories.error)}</ErrorAlert>

  const page = transactions.data
  const items = page?.items ?? []
  const categoryList = categories.data

  function toggle(id: string) {
    const next = new Set(selectedIds)
    if (next.has(id)) next.delete(id)
    else next.add(id)
    setSelectedIds(next)
  }

  function toggleAll() {
    const allSelected = items.every((item) => selectedIds.has(item.id))
    setSelectedIds(allSelected ? new Set() : new Set(items.map((item) => item.id)))
  }

  function startCorrection(transaction: Transaction, categoryId: string) {
    const category = categoryList.find((item) => item.id === categoryId)
    if (!category) return
    correct.reset()
    setPending({ transaction, category })
  }

  function saveCorrection(ruleKeyword: string | null) {
    if (!pending) return
    correct.mutate(
      {
        transactionId: pending.transaction.id,
        categoryId: pending.category.id,
        ruleKeyword: ruleKeyword ?? undefined,
      },
      {
        onSuccess: (result) => {
          setPending(null)
          setNotice(correctionMessage(ruleKeyword, result.updated_transactions))
        },
      },
    )
  }

  function applyBulk(categoryId: string) {
    bulk.mutate(
      { transactionIds: [...selectedIds], categoryId },
      {
        onSuccess: (result) => {
          setSelectedIds(new Set())
          const name = categoryList.find((item) => item.id === categoryId)?.name
          setNotice(`${result.updated} işlem ${name} kategorisine taşındı.`)
        },
      },
    )
  }

  return (
    <div className="space-y-4">
      <TransactionFiltersBar
        filters={filters}
        categories={categoryList}
        onChange={updateFilters}
        onClear={clearFilters}
      />

      {notice && <SuccessNotice onDismiss={() => setNotice(null)}>{notice}</SuccessNotice>}
      {bulk.isError && <ErrorAlert>{errorMessage(bulk.error)}</ErrorAlert>}
      {transactions.isError && <ErrorAlert>{errorMessage(transactions.error)}</ErrorAlert>}

      {selectedIds.size > 0 && (
        <BulkBar
          count={selectedIds.size}
          categories={categoryList}
          saving={bulk.isPending}
          onApply={applyBulk}
          onClear={() => setSelectedIds(new Set())}
        />
      )}

      <Card className="relative overflow-hidden p-0">
        {transactions.isFetching && (
          <Spinner className="absolute top-3 right-3 size-4 text-fg-faint" />
        )}
        {items.length > 0 ? (
          <TransactionList
            transactions={items}
            categories={categoryList}
            selectedIds={selectedIds}
            onToggle={toggle}
            onToggleAll={toggleAll}
            onCategoryChange={startCorrection}
          />
        ) : hasActiveFilters(filters) ? (
          <p className="px-4 py-12 text-center text-sm text-fg-subtle">
            Filtrelere uyan işlem yok.
          </p>
        ) : (
          <div className="flex flex-col items-center px-4 py-12 text-center">
            <Upload aria-hidden className="size-10 text-fg-faint" />
            <p className="mt-3 font-medium text-fg-secondary">Henüz işlem yok</p>
            <Link to="/yukle" className="mt-2 text-sm font-medium text-accent-fg hover:underline">
              İlk ekstreni yükle
            </Link>
          </div>
        )}
      </Card>

      {page && (
        <Pagination
          page={page.page}
          pages={page.pages}
          pageSize={PAGE_SIZE}
          total={page.total}
          onPageChange={(next) => {
            setSearchParams(filtersToParams({ ...filters, page: next }))
            setSelectedIds(new Set())
          }}
        />
      )}

      <CorrectionDialog
        correction={pending}
        saving={correct.isPending}
        error={correct.isError ? errorMessage(correct.error) : null}
        onSave={saveCorrection}
        onCancel={() => setPending(null)}
      />
    </div>
  )
}
