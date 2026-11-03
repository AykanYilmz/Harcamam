import { useCategories } from '../api/categories.ts'
import { CategoriesSection } from '../components/categories/CategoriesSection.tsx'
import { RulesSection } from '../components/categories/RulesSection.tsx'
import { ErrorAlert } from '../components/ui/Alert.tsx'
import { PageLoader } from '../components/ui/Spinner.tsx'
import { errorMessage } from '../lib/errors.ts'

export function CategoriesPage() {
  const categories = useCategories()

  if (categories.isPending) return <PageLoader />
  if (categories.isError) return <ErrorAlert>{errorMessage(categories.error)}</ErrorAlert>

  return (
    <div className="grid items-start gap-4 lg:grid-cols-2">
      <CategoriesSection categories={categories.data} />
      <RulesSection categories={categories.data} />
    </div>
  )
}
