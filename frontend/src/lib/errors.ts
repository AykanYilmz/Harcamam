import { ApiError, NetworkError } from '../api/client.ts'

// The API answers in English; every message the user sees is chosen here, in Turkish.
const NETWORK_MESSAGE = 'Sunucuya ulaşılamadı. Bağlantını kontrol edip tekrar dene.'
const GENERIC_MESSAGE = 'Beklenmeyen bir hata oluştu. Lütfen tekrar dene.'

const STATUS_MESSAGES: Record<number, string> = {
  401: 'Oturumunun süresi doldu. Lütfen tekrar giriş yap.',
  403: 'Bu işlem için yetkin yok.',
  404: 'Aradığın kayıt bulunamadı.',
  413: 'Dosya çok büyük.',
  422: 'Girdiğin bilgiler geçersiz.',
  429: 'Çok sık denedin. Biraz bekleyip tekrar dene.',
  500: 'Sunucuda bir hata oluştu. Lütfen daha sonra tekrar dene.',
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

/** Resending a verification link. */
export const RESEND_ERRORS = {
  409: 'E-posta adresin zaten doğrulanmış.',
  429: 'Az önce bir bağlantı gönderdik. Bir dakika sonra tekrar deneyebilirsin.',
}
