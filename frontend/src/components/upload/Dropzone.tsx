import { FileUp } from 'lucide-react'
import { useState, type DragEvent } from 'react'
import { ACCEPTED_EXTENSIONS } from '../../lib/upload.ts'

/**
 * A file input styled as a drop area. Being a real <input type="file"> inside a <label>,
 * it opens the file picker on click and works with the keyboard and screen readers.
 */
export function Dropzone({ onFiles }: { onFiles(files: File[]): void }) {
  const [dragging, setDragging] = useState(false)

  function handleDrop(event: DragEvent<HTMLLabelElement>) {
    event.preventDefault()
    setDragging(false)
    onFiles(Array.from(event.dataTransfer.files))
  }

  return (
    <label
      onDragOver={(event) => {
        event.preventDefault()
        setDragging(true)
      }}
      onDragLeave={() => setDragging(false)}
      onDrop={handleDrop}
      className={`flex cursor-pointer flex-col items-center justify-center rounded-2xl border-2 border-dashed px-6 py-12 text-center transition-colors has-[:focus-visible]:outline-2 has-[:focus-visible]:outline-offset-2 has-[:focus-visible]:outline-emerald-600 ${
        dragging
          ? 'border-emerald-500 bg-accent-soft'
          : 'border-line-strong bg-surface hover:border-emerald-500'
      }`}
    >
      <FileUp aria-hidden className="size-10 text-fg-faint" />
      <span className="mt-3 font-medium text-fg">
        Ekstreni buraya sürükle ya da <span className="text-accent-fg">dosya seç</span>
      </span>
      <span className="mt-1 text-sm text-fg-subtle">PDF veya CSV · en fazla 5 MB</span>
      <input
        type="file"
        multiple
        accept={ACCEPTED_EXTENSIONS.join(',')}
        className="sr-only"
        onChange={(event) => {
          onFiles(Array.from(event.target.files ?? []))
          // Reset so choosing the same file again still triggers a change.
          event.target.value = ''
        }}
      />
    </label>
  )
}
