import { useMutation, useQuery, useQueryClient, type QueryClient } from '@tanstack/react-query'
import { api } from './index.ts'
import { REPORTS_KEY } from './reports.ts'
import type { Statement, StatementImportResult } from './types.ts'

const STATEMENTS_KEY = ['statements'] as const
export const TRANSACTIONS_KEY = ['transactions'] as const

/** Uploading or deleting a statement changes everything built from transactions. */
function invalidateStatementData(queryClient: QueryClient) {
  return Promise.all([
    queryClient.invalidateQueries({ queryKey: STATEMENTS_KEY }),
    queryClient.invalidateQueries({ queryKey: TRANSACTIONS_KEY }),
    queryClient.invalidateQueries({ queryKey: REPORTS_KEY }),
  ])
}

export function useStatements() {
  return useQuery({
    queryKey: STATEMENTS_KEY,
    queryFn: () => api.get<Statement[]>('/statements'),
  })
}

export function useUploadStatement() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (file: File) => {
      const body = new FormData()
      body.append('file', file)
      return api.request<StatementImportResult>('/statements/upload', { method: 'POST', body })
    },
    onSuccess: () => invalidateStatementData(queryClient),
  })
}

export function useDeleteStatement() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (statementId: string) => api.delete(`/statements/${statementId}`),
    onSuccess: () => invalidateStatementData(queryClient),
  })
}
