import { Pencil, Plus, Trash2 } from 'lucide-react'
import { useState, type ReactNode } from 'react'
import { useCreateCategory, useDeleteCategory, useUpdateCategory } from '../../api/categories.ts'
import type { Category, CategoryCreate } from '../../api/types.ts'
import { KIND_LABELS } from '../../lib/categories.ts'
import { errorMessage } from '../../lib/errors.ts'
import { CategoryIcon } from '../CategoryIcon.tsx'
import { ErrorAlert } from '../ui/Alert.tsx'
import { Button } from '../ui/Button.tsx'
import { Card } from '../ui/Card.tsx'
import { ConfirmDialog } from '../ui/ConfirmDialog.tsx'
import { CategoryFormDialog } from './CategoryFormDialog.tsx'

const CATEGORY_ERRORS = { 409: 'Bu adla bir kategori zaten var.' }

function KindBadge({ category }: { category: Category }) {
  if (category.kind === 'expense') return null
  return (
    <span className="rounded-full bg-surface-muted px-2 py-0.5 text-xs text-fg-subtle">
      {KIND_LABELS[category.kind]}
    </span>
  )
}

function CategoryRow({ category, actions }: { category: Category; actions?: ReactNode }) {
  return (
    <li className="flex items-center gap-3 py-2.5">
      <CategoryIcon icon={category.icon} color={category.color} />
      <span className="flex-1 truncate text-sm font-medium text-fg">{category.name}</span>
      <KindBadge category={category} />
      {actions}
    </li>
  )
}

export function CategoriesSection({ categories }: { categories: Category[] }) {
  const create = useCreateCategory()
  const update = useUpdateCategory()
  const remove = useDeleteCategory()
  const [editing, setEditing] = useState<Category | null>(null)
  const [formOpen, setFormOpen] = useState(false)
  const [toDelete, setToDelete] = useState<Category | null>(null)

  const own = categories.filter((category) => !category.is_default)
  const defaults = categories.filter((category) => category.is_default)
  const saving = create.isPending || update.isPending
  const saveError = create.error ?? update.error

  function openForm(category: Category | null) {
    create.reset()
    update.reset()
    setEditing(category)
    setFormOpen(true)
  }

  function save(values: CategoryCreate) {
    const done = { onSuccess: () => setFormOpen(false) }
    if (editing) update.mutate({ id: editing.id, changes: values }, done)
    else create.mutate(values, done)
  }

  return (
    <Card>
      <div className="flex items-center justify-between gap-3">
        <h2 className="font-semibold text-fg">Kategoriler</h2>
        <Button onClick={() => openForm(null)} className="px-3">
          <Plus aria-hidden className="size-4" />
          Yeni kategori
        </Button>
      </div>

      <h3 className="mt-5 text-xs font-medium text-fg-subtle uppercase">Kendi kategorilerin</h3>
      {own.length === 0 ? (
        <p className="mt-2 text-sm text-fg-subtle">
          Henüz kendi kategorin yok. Örneğin "Hobi" ya da "Freelance" ekleyebilirsin.
        </p>
      ) : (
        <ul className="divide-y divide-line">
          {own.map((category) => (
            <CategoryRow
              key={category.id}
              category={category}
              actions={
                <div className="flex">
                  <button
                    type="button"
                    onClick={() => openForm(category)}
                    aria-label={`${category.name} kategorisini düzenle`}
                    title="Düzenle"
                    className="rounded-lg p-2 text-fg-subtle hover:bg-surface-muted hover:text-fg"
                  >
                    <Pencil aria-hidden className="size-4" />
                  </button>
                  <button
                    type="button"
                    onClick={() => {
                      remove.reset()
                      setToDelete(category)
                    }}
                    aria-label={`${category.name} kategorisini sil`}
                    title="Sil"
                    className="rounded-lg p-2 text-fg-subtle hover:bg-danger-soft hover:text-danger-fg"
                  >
                    <Trash2 aria-hidden className="size-4" />
                  </button>
                </div>
              }
            />
          ))}
        </ul>
      )}

      <h3 className="mt-6 text-xs font-medium text-fg-subtle uppercase">Varsayılan kategoriler</h3>
      <ul className="divide-y divide-line">
        {defaults.map((category) => (
          <CategoryRow key={category.id} category={category} />
        ))}
      </ul>

      <CategoryFormDialog
        open={formOpen}
        category={editing}
        saving={saving}
        error={saveError ? errorMessage(saveError, CATEGORY_ERRORS) : null}
        onSave={save}
        onClose={() => setFormOpen(false)}
      />

      <ConfirmDialog
        open={toDelete !== null}
        title="Kategoriyi sil"
        confirmLabel="Sil"
        loading={remove.isPending}
        onConfirm={() =>
          toDelete && remove.mutate(toDelete.id, { onSuccess: () => setToDelete(null) })
        }
        onCancel={() => setToDelete(null)}
      >
        <p>
          <strong className="text-fg">{toDelete?.name}</strong> silinecek. Bu kategorideki işlemler
          "Diğer"e taşınır ve kategoriye bağlı kurallar silinir.
        </p>
        {remove.isError && (
          <div className="mt-3">
            <ErrorAlert>{errorMessage(remove.error)}</ErrorAlert>
          </div>
        )}
      </ConfirmDialog>
    </Card>
  )
}
