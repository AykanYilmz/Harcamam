import { ArrowRight, Trash2 } from 'lucide-react'
import { useState, type FormEvent } from 'react'
import { useCreateRule, useDeleteRule, useRules } from '../../api/categories.ts'
import type { Category } from '../../api/types.ts'
import { errorMessage } from '../../lib/errors.ts'
import { CategoryOptions } from '../CategoryOptions.tsx'
import { ErrorAlert } from '../ui/Alert.tsx'
import { Button } from '../ui/Button.tsx'
import { Card } from '../ui/Card.tsx'
import { SuccessNotice } from '../ui/Notice.tsx'
import { selectClass } from '../ui/SelectField.tsx'
import { Spinner } from '../ui/Spinner.tsx'

const inputClass =
  'w-full rounded-lg border border-line-strong bg-surface px-3 py-2 text-sm text-fg shadow-sm focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/30 focus:outline-none'

export function RulesSection({ categories }: { categories: Category[] }) {
  const rules = useRules()
  const create = useCreateRule()
  const remove = useDeleteRule()
  const [keyword, setKeyword] = useState('')
  const [categoryId, setCategoryId] = useState('')
  const [applyToExisting, setApplyToExisting] = useState(true)
  const [notice, setNotice] = useState<string | null>(null)

  const byId = new Map(categories.map((category) => [category.id, category]))

  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    create.mutate(
      { keyword: keyword.trim(), category_id: categoryId, apply_to_existing: applyToExisting },
      {
        onSuccess: (result) => {
          setKeyword('')
          const updated = result.updated_transactions
          setNotice(
            `"${result.rule.keyword}" kuralı kaydedildi.` +
              (updated > 0 ? ` ${updated} işlem güncellendi.` : ''),
          )
        },
      },
    )
  }

  return (
    <Card>
      <h2 className="font-semibold text-fg">Kurallar</h2>
      <p className="mt-1 text-sm text-fg-subtle">
        Açıklamasında anahtar kelime geçen işlemler seçtiğin kategoriye düşer. Kuralların varsayılan
        eşleştirmelerden önce uygulanır.
      </p>

      <form onSubmit={submit} className="mt-4 space-y-3">
        <div className="grid gap-2 sm:grid-cols-[1fr_auto_1fr]">
          <input
            value={keyword}
            onChange={(event) => setKeyword(event.target.value)}
            placeholder="Anahtar kelime (ör. STARBUCKS)"
            aria-label="Anahtar kelime"
            maxLength={100}
            className={inputClass}
          />
          <ArrowRight aria-hidden className="hidden size-4 self-center text-fg-faint sm:block" />
          <select
            value={categoryId}
            onChange={(event) => setCategoryId(event.target.value)}
            aria-label="Kategori"
            className={selectClass}
          >
            <option value="" disabled>
              Kategori seç…
            </option>
            <CategoryOptions categories={categories} />
          </select>
        </div>
        <div className="flex flex-wrap items-center justify-between gap-3">
          <label className="flex items-center gap-2 text-sm text-fg-muted">
            <input
              type="checkbox"
              checked={applyToExisting}
              onChange={(event) => setApplyToExisting(event.target.checked)}
              className="accent-emerald-600"
            />
            Mevcut işlemlere de uygula
          </label>
          <Button
            type="submit"
            loading={create.isPending}
            disabled={!keyword.trim() || !categoryId}
          >
            Kural ekle
          </Button>
        </div>
      </form>

      <div className="mt-4 space-y-3">
        {notice && <SuccessNotice onDismiss={() => setNotice(null)}>{notice}</SuccessNotice>}
        {create.isError && (
          <ErrorAlert>
            {errorMessage(create.error, {
              422: 'Anahtar kelime en az bir harf ya da rakam içermeli.',
            })}
          </ErrorAlert>
        )}
        {remove.isError && <ErrorAlert>{errorMessage(remove.error)}</ErrorAlert>}
      </div>

      {rules.isPending && <Spinner className="mt-4 size-5 text-fg-subtle" />}
      {rules.data?.length === 0 && (
        <p className="mt-4 text-sm text-fg-subtle">
          Henüz kural yok. İşlemler sayfasında bir kategoriyi düzeltirken de kural kaydedebilirsin.
        </p>
      )}
      {rules.data && rules.data.length > 0 && (
        <ul className="mt-4 divide-y divide-line">
          {rules.data.map((rule) => {
            const category = byId.get(rule.category_id)
            return (
              <li key={rule.id} className="flex items-center gap-3 py-2.5">
                <code className="rounded bg-surface-muted px-2 py-0.5 text-sm text-fg">
                  {rule.keyword}
                </code>
                <ArrowRight aria-hidden className="size-4 shrink-0 text-fg-faint" />
                <span className="flex flex-1 items-center gap-2 truncate text-sm text-fg">
                  <span
                    aria-hidden
                    className="size-2.5 shrink-0 rounded-full"
                    style={{ backgroundColor: category?.color }}
                  />
                  {category?.name}
                </span>
                <button
                  type="button"
                  onClick={() => remove.mutate(rule.id)}
                  disabled={remove.isPending}
                  aria-label={`${rule.keyword} kuralını sil`}
                  title="Sil"
                  className="rounded-lg p-2 text-fg-subtle hover:bg-danger-soft hover:text-danger-fg"
                >
                  <Trash2 aria-hidden className="size-4" />
                </button>
              </li>
            )
          })}
        </ul>
      )}
    </Card>
  )
}
