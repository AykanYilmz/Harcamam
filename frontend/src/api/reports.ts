import { useQuery } from '@tanstack/react-query'
import { api } from './index.ts'
import type {
  CategoryTrendReport,
  DailySpending,
  MonthlyReport,
  TopMerchants,
  TrendReport,
} from './types.ts'

/** Every report query starts with this key, so one invalidation refreshes them all. */
export const REPORTS_KEY = ['reports'] as const

const TREND_MONTHS = 6

/** `month` undefined lets the API pick the latest month that has data. */
export function useMonthlyReport(month: string | undefined) {
  return useQuery({
    queryKey: [...REPORTS_KEY, 'monthly', month ?? 'latest'],
    queryFn: () => api.get<MonthlyReport>('/reports/monthly', { month }),
  })
}

export function useTrend(endMonth: string | undefined) {
  return useQuery({
    queryKey: [...REPORTS_KEY, 'trend', endMonth],
    queryFn: () => api.get<TrendReport>('/reports/trend', { end: endMonth, months: TREND_MONTHS }),
    enabled: endMonth !== undefined,
  })
}

export function useTopMerchants(month: string | undefined, limit = 5) {
  return useQuery({
    queryKey: [...REPORTS_KEY, 'top-merchants', month, limit],
    queryFn: () => api.get<TopMerchants>('/reports/top-merchants', { month, limit }),
    enabled: month !== undefined,
  })
}

/** `calendarMonth`: the 1st to the last day, even when the user's months end on another day. */
export function useDailySpending(month: string | undefined, calendarMonth = false) {
  return useQuery({
    queryKey: [...REPORTS_KEY, 'daily', month, calendarMonth],
    queryFn: () =>
      api.get<DailySpending>('/reports/daily', { month, calendar_month: calendarMonth }),
    enabled: month !== undefined,
  })
}

export function useLongTrend(endMonth: string | undefined, months: number) {
  return useQuery({
    queryKey: [...REPORTS_KEY, 'trend', endMonth, months],
    queryFn: () => api.get<TrendReport>('/reports/trend', { end: endMonth, months }),
    enabled: endMonth !== undefined,
  })
}

export function useCategoryTrend(endMonth: string | undefined, months: number) {
  return useQuery({
    queryKey: [...REPORTS_KEY, 'category-trend', endMonth, months],
    queryFn: () =>
      api.get<CategoryTrendReport>('/reports/category-trend', { end: endMonth, months }),
    enabled: endMonth !== undefined,
  })
}
