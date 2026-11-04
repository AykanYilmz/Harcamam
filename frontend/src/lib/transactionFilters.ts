import type { TransactionSort, TransactionType } from '../api/types.ts'
import { periodRange } from './periods.ts'

/** Filters for the transactions list, as kept in the page URL. */
export interface TransactionFilters {
  query: string
  dateFrom: string
  dateTo: string
  categoryIds: string[]
  type: TransactionType | ''
  sort: TransactionSort
  page: number
}

export const DEFAULT_SORT: TransactionSort = 'date_desc'
export const PAGE_SIZE = 25

// Turkish URL parameter names: /islemler?ara=migros&kategori=...&tur=gider
const PARAMS = {
  query: 'ara',
  dateFrom: 'baslangic',
  dateTo: 'bitis',
  category: 'kategori',
  type: 'tur',
  sort: 'sirala',
  page: 'sayfa',
} as const

const TYPE_IN_URL: Record<TransactionType, string> = { income: 'gelir', expense: 'gider' }
const SORTS: TransactionSort[] = ['date_desc', 'date_asc', 'amount_desc', 'amount_asc']
const ISO_DATE = /^\d{4}-\d{2}-\d{2}$/

export function filtersFromParams(params: URLSearchParams): TransactionFilters {
  const typeParam = params.get(PARAMS.type)
  const type = (Object.keys(TYPE_IN_URL) as TransactionType[]).find(
    (key) => TYPE_IN_URL[key] === typeParam,
  )
  const sort = params.get(PARAMS.sort) as TransactionSort | null
  const date = (value: string | null) => (value && ISO_DATE.test(value) ? value : '')
  const page = Number(params.get(PARAMS.page))

  return {
    query: params.get(PARAMS.query) ?? '',
    dateFrom: date(params.get(PARAMS.dateFrom)),
    dateTo: date(params.get(PARAMS.dateTo)),
    categoryIds: params.getAll(PARAMS.category),
    type: type ?? '',
    sort: sort && SORTS.includes(sort) ? sort : DEFAULT_SORT,
    page: Number.isInteger(page) && page > 1 ? page : 1,
  }
}

export function filtersToParams(filters: TransactionFilters): URLSearchParams {
  const params = new URLSearchParams()
  if (filters.query) params.set(PARAMS.query, filters.query)
  if (filters.dateFrom) params.set(PARAMS.dateFrom, filters.dateFrom)
  if (filters.dateTo) params.set(PARAMS.dateTo, filters.dateTo)
  for (const id of filters.categoryIds) params.append(PARAMS.category, id)
  if (filters.type) params.set(PARAMS.type, TYPE_IN_URL[filters.type])
  if (filters.sort !== DEFAULT_SORT) params.set(PARAMS.sort, filters.sort)
  if (filters.page > 1) params.set(PARAMS.page, String(filters.page))
  return params
}

/** The same filters in the API's query parameter names. */
export function filtersToApiQuery(filters: TransactionFilters) {
  return {
    q: filters.query.trim() || undefined,
    date_from: filters.dateFrom || undefined,
    date_to: filters.dateTo || undefined,
    category_id: filters.categoryIds,
    type: filters.type || undefined,
    sort: filters.sort,
    page: filters.page,
    page_size: PAGE_SIZE,
  }
}

export function hasActiveFilters(filters: TransactionFilters): boolean {
  return Boolean(
    filters.query ||
    filters.dateFrom ||
    filters.dateTo ||
    filters.categoryIds.length ||
    filters.type,
  )
}

/** A local date as "2026-10-05". */
export function isoDate(date: Date): string {
  const month = String(date.getMonth() + 1).padStart(2, '0')
  return `${date.getFullYear()}-${month}-${String(date.getDate()).padStart(2, '0')}`
}

/**
 * The transactions page filtered to one category in one month ("2026-10"), using the same
 * days the reports count for that month (`endDay` is the user's statement closing day).
 */
export function categoryMonthLink(
  categoryId: string,
  month: string,
  endDay: number | null,
): string {
  const { start, end } = periodRange(month, endDay)
  const params = filtersToParams({
    query: '',
    dateFrom: isoDate(start),
    dateTo: isoDate(end),
    categoryIds: [categoryId],
    type: '',
    sort: DEFAULT_SORT,
    page: 1,
  })
  return `/islemler?${params}`
}
