import { describe, expect, it } from 'vitest'
import { suggestKeyword } from './text.ts'
import {
  categoryMonthLink,
  DEFAULT_SORT,
  filtersFromParams,
  filtersToApiQuery,
  filtersToParams,
  type TransactionFilters,
} from './transactionFilters.ts'

const FILTERS: TransactionFilters = {
  query: 'migros',
  dateFrom: '2026-10-01',
  dateTo: '2026-10-31',
  categoryIds: ['a', 'b'],
  type: 'expense',
  sort: 'amount_desc',
  page: 3,
}

describe('transaction filters in the URL', () => {
  it('round-trips through URL parameters', () => {
    expect(filtersFromParams(filtersToParams(FILTERS))).toEqual(FILTERS)
  })

  it('uses Turkish parameter names', () => {
    expect(filtersToParams(FILTERS).toString()).toBe(
      'ara=migros&baslangic=2026-10-01&bitis=2026-10-31&kategori=a&kategori=b&tur=gider&sirala=amount_desc&sayfa=3',
    )
  })

  it('leaves defaults out of the URL', () => {
    const params = filtersToParams({
      ...FILTERS,
      query: '',
      categoryIds: [],
      type: '',
      sort: DEFAULT_SORT,
      page: 1,
      dateFrom: '',
      dateTo: '',
    })

    expect(params.toString()).toBe('')
  })

  it('ignores invalid values from a hand-edited URL', () => {
    const filters = filtersFromParams(
      new URLSearchParams('tur=hepsi&sirala=random&sayfa=-2&baslangic=dun'),
    )

    expect(filters).toMatchObject({ type: '', sort: DEFAULT_SORT, page: 1, dateFrom: '' })
  })

  it('maps to the API query', () => {
    expect(filtersToApiQuery({ ...FILTERS, query: '  ' })).toMatchObject({
      q: undefined,
      category_id: ['a', 'b'],
      type: 'expense',
      page: 3,
      page_size: 25,
    })
  })

  it('links a category to its month', () => {
    expect(categoryMonthLink('a', '2026-02', null)).toBe(
      '/islemler?baslangic=2026-02-01&bitis=2026-02-28&kategori=a',
    )
  })

  it('links to the same days the reports count with a closing day', () => {
    expect(categoryMonthLink('a', '2026-10', 6)).toBe(
      '/islemler?baslangic=2026-09-07&bitis=2026-10-06&kategori=a',
    )
  })
})

describe('suggestKeyword', () => {
  it.each([
    ['MIGROS KADIKÖY İSTANBUL', 'MIGROS'],
    ['NETFLIX.COM', 'NETFLIX'],
    ['A101 MODA', 'A101'],
    ['ŞOK MARKET', 'ŞOK'],
    ['123 456 STARBUCKS', 'STARBUCKS'],
    ['APPLE.COM/BILL', 'APPLE'],
  ])('suggests a keyword for %s', (description, expected) => {
    expect(suggestKeyword(description)).toBe(expected)
  })
})
