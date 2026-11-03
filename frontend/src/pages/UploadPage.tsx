import { useRef, useState } from 'react'
import { useUploadStatement } from '../api/statements.ts'
import { Dropzone } from '../components/upload/Dropzone.tsx'
import { StatementList } from '../components/upload/StatementList.tsx'
import { UploadQueue, type UploadItem } from '../components/upload/UploadQueue.tsx'
import { uploadErrorMessage, validateStatementFile } from '../lib/upload.ts'

export function UploadPage() {
  const upload = useUploadStatement()
  const [items, setItems] = useState<UploadItem[]>([])
  const nextId = useRef(0)

  function update(id: number, item: UploadItem) {
    setItems((current) => current.map((existing) => (existing.id === id ? item : existing)))
  }

  async function handleFiles(files: File[]) {
    const queued = files.map((file) => {
      const id = nextId.current++
      const problem = validateStatementFile(file)
      const item: UploadItem = problem
        ? { id, fileName: file.name, status: 'failed', message: problem }
        : { id, fileName: file.name, status: 'waiting' }
      return { file, item }
    })
    setItems((current) => [...queued.map(({ item }) => item), ...current])

    // One at a time: later files may overlap earlier ones, and each must see what the
    // previous one imported for duplicates to be skipped.
    for (const { file, item } of queued) {
      if (item.status === 'failed') continue
      update(item.id, { ...item, status: 'uploading' })
      try {
        const result = await upload.mutateAsync(file)
        update(item.id, { id: item.id, fileName: file.name, status: 'done', result })
      } catch (error) {
        update(item.id, {
          id: item.id,
          fileName: file.name,
          status: 'failed',
          message: uploadErrorMessage(error),
        })
      }
    }
  }

  return (
    <>
      <h1 className="text-2xl font-semibold text-fg">Ekstre Yükle</h1>
      <p className="mt-1 text-sm text-fg-subtle">
        Bankandan indirdiğin hesap veya kredi kartı ekstresini yükle. İşlemler otomatik olarak
        kategorilere ayrılır; aynı işlem iki kez kaydedilmez.
      </p>

      <div className="mt-6">
        <Dropzone onFiles={handleFiles} />
        <UploadQueue items={items} />
      </div>

      <StatementList />
    </>
  )
}
