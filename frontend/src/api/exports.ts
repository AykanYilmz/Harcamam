import { useMutation } from '@tanstack/react-query'
import { api } from './index.ts'

export type ExportFormat = 'xlsx' | 'csv'

function save(blob: Blob, fileName: string) {
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = fileName
  link.click()
  URL.revokeObjectURL(url)
}

/** Downloads the transactions from `start` to `end` (ISO dates, inclusive). */
export function useExportTransactions() {
  return useMutation({
    mutationFn: async ({
      format,
      start,
      end,
    }: {
      format: ExportFormat
      start: string
      end: string
    }) => {
      const { blob, fileName } = await api.download('/exports/transactions', { format, start, end })
      save(blob, fileName ?? `hesapkitap_${start}_${end}.${format}`)
    },
  })
}
