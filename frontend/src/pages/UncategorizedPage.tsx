import { ChevronDown, CircleCheck, PartyPopper } from 'lucide-react'
import { useState } from 'react'
import { Link } from 'react-router'
import { useCategories, useCreateRule } from '../api/categories.ts'
import { useUncategorized } from '../api/transactions.ts'
import type { Category, UncategorizedMerchant } from '../api/types.ts'
import { CategoryIcon } from '../components/CategoryIcon.tsx'
import { ErrorAlert } from '../components/ui/Alert.tsx'
import { Card } from '../components/ui/Card.tsx'
import { selectClass } from '../components/ui/SelectField.tsx'
import { PageLoader } from '../components/ui/Spinner.tsx'
import { isOtherCategory, KIND_LABELS, KIND_ORDER } from '../lib/categories.ts'
import { errorMessage } from '../lib/errors.ts'
import { formatCurrency, formatDate } from '../lib/format.ts'

function CategoryOptions({ categories }: { categories: Category[] }) {
  return KIND_ORDER.map((kind) => {
    const options = categories.filter((c) => c.kind === kind && !isOtherCategory(c))
    if (options.length === 0) return null
    return (
      <optgroup key={kind} label={KIND_LABELS[kind]}>
        {options.map((category) => (
          <option key={category.id} value={category.id}>
            {category.name}
          </option>
        ))}
      </optgroup>
    )
  })
}

function MerchantRow({
  merchant,
  categories,
}: {
  merchant: UncategorizedMerchant
  categories: Category[]
}) {
  const saveRule = useCreateRule()
  const [open, setOpen] = useState(false)
  const chosen = categories.find((c) => c.id === saveRule.variables?.category_id)
  const count = merchant.transactions.length
  const detailsId = `merchant-${merchant.keyword}`

  return (
    <li className="py-3">
      <div className="flex flex-wrap items-center gap-x-4 gap-y-2">
        <button
          type="button"
          onClick={() => setOpen(!open)}
          aria-expanded={open}
          aria-controls={detailsId}
          className="flex min-w-0 flex-1 items-center gap-2 rounded text-left focus-visible:ring-2 focus-visible:ring-emerald-500 focus-visible:outline-none"
        >
          <ChevronDown
            aria-hidden
            className={`size-4 shrink-0 text-fg-subtle transition-transform ${open ? '' : '-rotate-90'}`}
          />
          <span className="min-w-0">
            <span className="block truncate font-medium text-fg">{merchant.name}</span>
            <span className="text-xs text-fg-subtle">
              {count} işlem · {formatCurrency(merchant.amount)}
            </span>
          </span>
        </button>

        {saveRule.isSuccess && chosen ? (
          <span className="flex items-center gap-2 text-sm font-medium text-accent-fg">
            <CircleCheck aria-hidden className="size-4" />
            <CategoryIcon icon={chosen.icon} color={chosen.color} className="size-6" />
            {chosen.name}
          </span>
        ) : (
          <select
            aria-label={`${merchant.name} için kategori`}
            value=""
            disabled={saveRule.isPending}
            onChange={(event) =>
              saveRule.mutate({
                keyword: merchant.keyword,
                category_id: event.target.value,
                apply_to_existing: true,
              })
            }
            className={`${selectClass} w-full sm:w-52`}
          >
            <option value="" disabled>
              {saveRule.isPending ? 'Kaydediliyor…' : 'Kategori seç'}
            </option>
            <CategoryOptions categories={categories} />
          </select>
        )}
      </div>

      {saveRule.isError && (
        <div className="mt-2">
          <ErrorAlert>{errorMessage(saveRule.error)}</ErrorAlert>
        </div>
      )}

      {open && (
        <ul id={detailsId} className="mt-2 space-y-1 pl-6 text-sm">
          {merchant.transactions.map((transaction) => (
            <li key={transaction.id} className="flex gap-3 text-fg-muted">
              <span className="w-24 shrink-0 text-fg-subtle">{formatDate(transaction.date)}</span>
              <span className="min-w-0 flex-1 truncate">{transaction.description}</span>
              <span className="shrink-0 tabular-nums">
                {transaction.type === 'income' ? '+' : '−'}
                {formatCurrency(transaction.amount)}
              </span>
            </li>
          ))}
        </ul>
      )}
    </li>
  )
}

export function UncategorizedPage() {
  const report = useUncategorized()
  const categories = useCategories()

  if (report.isPending || categories.isPending) return <PageLoader />
  if (report.isError) return <ErrorAlert>{errorMessage(report.error)}</ErrorAlert>
  if (categories.isError) return <ErrorAlert>{errorMessage(categories.error)}</ErrorAlert>

  const { merchants, transaction_count: count } = report.data
  if (merchants.length === 0) {
    return (
      <Card className="mx-auto flex max-w-xl flex-col items-center py-12 text-center">
        <PartyPopper aria-hidden className="size-10 text-accent-fg" />
        <p className="mt-3 font-medium text-fg">Tanınmayan işlem kalmadı</p>
        <p className="mt-1 text-sm text-fg-subtle">
          Bütün işlemlerin bir kategoride. Yeni ekstre yüklediğinde tanınmayanlar burada görünür.
        </p>
        <Link to="/" className="mt-5 text-sm font-medium text-accent-fg hover:underline">
          Özete dön
        </Link>
      </Card>
    )
  }

  return (
    <div className="mx-auto max-w-3xl">
      <Card>
        <h2 className="font-semibold text-fg">
          {merchants.length} yerden {count} işlem tanınmadı
        </h2>
        <p className="mt-1 text-sm text-fg-subtle">
          Bir yer için seçtiğin kategori o yerin bütün işlemlerine uygulanır ve kural olarak
          kaydedilir; sonraki ekstrelerde kendiliğinden tanınır. En çok harcama yapılan yerler
          üstte. Kuralları Kategoriler sayfasından değiştirebilirsin.
        </p>
        <ul className="mt-2 divide-y divide-line">
          {merchants.map((merchant) => (
            <MerchantRow key={merchant.keyword} merchant={merchant} categories={categories.data} />
          ))}
        </ul>
      </Card>
    </div>
  )
}
