// Friendly names for the types generated from the backend's OpenAPI schema (`npm run gen:api`).
import type { components } from './schema'

type Schemas = components['schemas']

export type User = Schemas['UserRead']
export type TokenPair = Schemas['TokenPair']

export type MonthlyReport = Schemas['MonthlyReportRead']
export type CategorySpending = Schemas['CategorySpendingRead']
export type TrendReport = Schemas['TrendReportRead']
export type MonthTotals = Schemas['MonthTotalsRead']
export type TopMerchants = Schemas['TopMerchantsRead']
export type MerchantSpending = Schemas['MerchantSpendingRead']
export type DailySpending = Schemas['DailySpendingRead']
export type DaySpending = Schemas['DaySpendingRead']

export type Statement = Schemas['StatementRead']
export type StatementImportResult = Schemas['StatementImportResult']
