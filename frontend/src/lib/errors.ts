import { ApiError, NetworkError } from '../api/client.ts'

// The API answers in English; every message the user sees is chosen here, in Turkish.
const NETWORK_MESSAGE = 'Sunucuya ulaşılamadı. Bağlantınızı kontrol edip tekrar deneyin.'
const GENERIC_MESSAGE = 'Beklenmeyen bir hata oluştu. Lütfen tekrar deneyin.'

const STATUS_MESSAGES: Record<number, string> = {
  401: 'Oturumunuzun süresi doldu. Lütfen tekrar giriş yapın.',
  403: 'Bu işlem için yetkiniz yok.',
  404: 'Aradığınız kayıt bulunamadı.',
  413: 'Dosya çok büyük.',
  422: 'Girdiğiniz bilgiler geçersiz.',
  500: 'Sunucuda bir hata oluştu. Lütfen daha sonra tekrar deneyin.',
}

/**
 * A Turkish message for an error. `byStatus` overrides the defaults for one screen,
 * e.g. a 401 on the login form means a wrong password, not an expired session.
 */
export function errorMessage(error: unknown, byStatus: Record<number, string> = {}): string {
  if (error instanceof NetworkError) return NETWORK_MESSAGE
  if (error instanceof ApiError) {
    return byStatus[error.status] ?? STATUS_MESSAGES[error.status] ?? GENERIC_MESSAGE
  }
  return GENERIC_MESSAGE
}
