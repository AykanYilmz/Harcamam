import { errorMessage } from './errors.ts'

// Same limits as the backend; checked here first so the user hears back instantly.
export const MAX_UPLOAD_BYTES = 5 * 1024 * 1024
export const ACCEPTED_EXTENSIONS = ['.pdf', '.csv']

/** A Turkish reason the file can't be uploaded, or null if it looks fine. */
export function validateStatementFile(file: Pick<File, 'name' | 'size'>): string | null {
  const name = file.name.toLowerCase()
  if (!ACCEPTED_EXTENSIONS.some((extension) => name.endsWith(extension))) {
    return 'Yalnızca PDF ve CSV dosyaları yüklenebilir.'
  }
  if (file.size === 0) return 'Dosya boş.'
  if (file.size > MAX_UPLOAD_BYTES) return 'Dosya 5 MB sınırını aşıyor.'
  return null
}

export function uploadErrorMessage(error: unknown): string {
  return errorMessage(error, {
    409: 'Bu ekstre ya da içindeki tüm işlemler zaten yüklenmiş.',
    413: 'Dosya 5 MB sınırını aşıyor.',
    415: 'Dosyanın içeriği PDF ya da CSV değil.',
    422: 'Dosya okunamadı. Bir banka ekstresi olduğundan ve bozuk olmadığından emin olun.',
  })
}
