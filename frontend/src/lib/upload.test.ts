import { describe, expect, it } from 'vitest'
import { ApiError } from '../api/client.ts'
import { MAX_UPLOAD_BYTES, uploadErrorMessage, validateStatementFile } from './upload.ts'

describe('validateStatementFile', () => {
  it.each(['ekstre.pdf', 'EKSTRE.CSV', 'hesap.hareketleri.csv'])('accepts %s', (name) => {
    expect(validateStatementFile({ name, size: 1000 })).toBeNull()
  })

  it.each(['ekstre.xlsx', 'ekstre.txt', 'pdf', 'ekstre.pdf.exe'])('rejects %s', (name) => {
    expect(validateStatementFile({ name, size: 1000 })).toBe(
      'Yalnızca PDF ve CSV dosyaları yüklenebilir.',
    )
  })

  it('rejects empty and oversized files', () => {
    expect(validateStatementFile({ name: 'a.csv', size: 0 })).toBe('Dosya boş.')
    expect(validateStatementFile({ name: 'a.csv', size: MAX_UPLOAD_BYTES + 1 })).toBe(
      'Dosya 5 MB sınırını aşıyor.',
    )
    expect(validateStatementFile({ name: 'a.csv', size: MAX_UPLOAD_BYTES })).toBeNull()
  })
})

describe('uploadErrorMessage', () => {
  it('explains a duplicate upload', () => {
    expect(uploadErrorMessage(new ApiError(409, 'This statement has already been uploaded'))).toBe(
      'Bu ekstre ya da içindeki tüm işlemler zaten yüklenmiş.',
    )
  })

  it('explains an unreadable file', () => {
    expect(uploadErrorMessage(new ApiError(422, 'Row 3: could not read the amount'))).toContain(
      'Dosya okunamadı',
    )
  })
})
