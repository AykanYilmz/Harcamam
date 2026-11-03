import { UserPen } from 'lucide-react'
import type { Category, Transaction } from '../../api/types.ts'
import { formatCurrency, formatDate } from '../../lib/format.ts'
import { CategoryOptions } from '../CategoryOptions.tsx'

interface TransactionListProps {
  transactions: Transaction[]
  categories: Category[]
  selectedIds: Set<string>
  onToggle(id: string): void
  onToggleAll(): void
  /** The user picked another category in a row; nothing is saved until confirmed. */
  onCategoryChange(transaction: Transaction, categoryId: string): void
}

function SignedAmount({ transaction }: { transaction: Transaction }) {
  const income = transaction.type === 'income'
  return (
    <span
      className={`font-semibold whitespace-nowrap tabular-nums ${income ? 'text-accent-fg' : 'text-fg'}`}
    >
      {income ? '+' : '−'}
      {formatCurrency(transaction.amount)}
    </span>
  )
}

function CategoryPicker({
  transaction,
  categories,
  onChange,
}: {
  transaction: Transaction
  categories: Category[]
  onChange(categoryId: string): void
}) {
  const current = categories.find((category) => category.id === transaction.category_id)
  return (
    <div className="flex items-center gap-2">
      <span
        aria-hidden
        className="size-2.5 shrink-0 rounded-full"
        style={{ backgroundColor: current?.color }}
      />
      {/* The select shows the saved category until a change is confirmed in the dialog. */}
      <select
        value={transaction.category_id}
        onChange={(event) => onChange(event.target.value)}
        aria-label={`${transaction.description} işleminin kategorisi`}
        className="w-full min-w-32 cursor-pointer rounded-md border border-transparent bg-transparent py-1 pr-7 pl-1 text-sm text-fg hover:border-line-strong focus:border-emerald-500 focus:outline-none"
      >
        <CategoryOptions categories={categories} />
      </select>
      {transaction.is_manually_categorized && (
        <span title="Elle kategorilendi" className="shrink-0 text-fg-faint">
          <UserPen aria-hidden className="size-4" />
          <span className="sr-only">Elle kategorilendi</span>
        </span>
      )}
    </div>
  )
}

export function TransactionList({
  transactions,
  categories,
  selectedIds,
  onToggle,
  onToggleAll,
  onCategoryChange,
}: TransactionListProps) {
  const allSelected = transactions.length > 0 && transactions.every((t) => selectedIds.has(t.id))

  return (
    <>
      {/* Wide screens: table */}
      <table className="hidden w-full text-sm md:table">
        <thead>
          <tr className="border-b border-line text-left text-xs font-medium text-fg-subtle uppercase">
            <th className="w-10 py-3 pl-4">
              <input
                type="checkbox"
                checked={allSelected}
                onChange={onToggleAll}
                aria-label="Bu sayfadaki tüm işlemleri seç"
                className="accent-emerald-600"
              />
            </th>
            <th className="py-3 pr-4">Tarih</th>
            <th className="py-3 pr-4">Açıklama</th>
            <th className="w-56 py-3 pr-4">Kategori</th>
            <th className="py-3 pr-4 text-right">Tutar</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-line">
          {transactions.map((transaction) => (
            <tr
              key={transaction.id}
              className={
                selectedIds.has(transaction.id) ? 'bg-accent-soft' : 'hover:bg-surface-muted/50'
              }
            >
              <td className="py-2 pl-4">
                <input
                  type="checkbox"
                  checked={selectedIds.has(transaction.id)}
                  onChange={() => onToggle(transaction.id)}
                  aria-label={`${transaction.description} işlemini seç`}
                  className="accent-emerald-600"
                />
              </td>
              <td className="py-2 pr-4 whitespace-nowrap text-fg-subtle">
                {formatDate(transaction.date)}
              </td>
              <td className="py-2 pr-4 font-medium text-fg">{transaction.description}</td>
              <td className="py-2 pr-4">
                <CategoryPicker
                  transaction={transaction}
                  categories={categories}
                  onChange={(categoryId) => onCategoryChange(transaction, categoryId)}
                />
              </td>
              <td className="py-2 pr-4 text-right">
                <SignedAmount transaction={transaction} />
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      {/* Phones: cards */}
      <ul className="divide-y divide-line md:hidden">
        {transactions.map((transaction) => (
          <li key={transaction.id} className="flex gap-3 px-4 py-3">
            <input
              type="checkbox"
              checked={selectedIds.has(transaction.id)}
              onChange={() => onToggle(transaction.id)}
              aria-label={`${transaction.description} işlemini seç`}
              className="mt-1 accent-emerald-600"
            />
            <div className="min-w-0 flex-1">
              <div className="flex items-start justify-between gap-2">
                <p className="font-medium text-fg">{transaction.description}</p>
                <SignedAmount transaction={transaction} />
              </div>
              <p className="text-xs text-fg-subtle">{formatDate(transaction.date)}</p>
              <div className="mt-1">
                <CategoryPicker
                  transaction={transaction}
                  categories={categories}
                  onChange={(categoryId) => onCategoryChange(transaction, categoryId)}
                />
              </div>
            </div>
          </li>
        ))}
      </ul>
    </>
  )
}
