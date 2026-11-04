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

export type Category = Schemas['CategoryRead']
export type CategoryKind = Schemas['CategoryKind']
export type CategoryCreate = Schemas['CategoryCreate']
export type CategoryUpdate = Schemas['CategoryUpdate']
export type Rule = Schemas['RuleRead']
export type RuleSaveResult = Schemas['RuleSaveResult']

export type Transaction = Schemas['TransactionRead']
export type TransactionPage = Schemas['TransactionPage']
export type TransactionType = Schemas['TransactionType']
export type TransactionSort = Schemas['TransactionSort']
export type TransactionCorrectionResult = Schemas['TransactionCorrectionResult']
export type BulkCategoryResult = Schemas['BulkCategoryResult']
export type UncategorizedReport = Schemas['UncategorizedReport']
export type UncategorizedMerchant = Schemas['UncategorizedMerchantRead']

export type CategoryTrendReport = Schemas['CategoryTrendReportRead']
export type CategoryTrend = Schemas['CategoryTrendRead']

export type BudgetReport = Schemas['BudgetReportRead']
export type Budget = Schemas['BudgetRead']
export type BudgetStatus = Schemas['BudgetStatus']
