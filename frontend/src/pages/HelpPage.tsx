import { ChevronDown } from 'lucide-react'
import type { ReactNode } from 'react'
import { Link } from 'react-router'
import { Card } from '../components/ui/Card.tsx'

interface Question {
  question: string
  answer: ReactNode
}

const linkClass = 'font-medium text-accent-fg hover:underline'

const QUESTIONS: Question[] = [
  {
    question: 'Hangi dosyaları yükleyebilirim?',
    answer: (
      <>
        Bankandan indirdiğin hesap ya da kredi kartı ekstresini <strong>PDF</strong> veya{' '}
        <strong>CSV</strong> olarak yükleyebilirsin (en fazla 5 MB). Dosyada tarih, açıklama ve
        tutar sütunları olmalı; tutar tek sütunda ya da ayrı "Borç / Alacak" sütunlarında olabilir.
        Taranmış (fotoğraf) PDF'ler okunamaz.
      </>
    ),
  },
  {
    question: 'Ekstremi bankadan nasıl indiririm?',
    answer: (
      <>
        Çoğu bankada internet şubesinde ya da mobil uygulamada "Hesap hareketleri" veya "Kart
        ekstresi" ekranında PDF, Excel veya CSV olarak indirme seçeneği bulunur. Excel dosyasını
        "Farklı kaydet → CSV" ile CSV'ye çevirebilirsin.
      </>
    ),
  },
  {
    question: 'Aynı ekstreyi ya da tarihleri çakışan ekstreleri yüklersem ne olur?',
    answer: (
      <>
        Aynı dosya ikinci kez yüklenmez. Tarihleri çakışan farklı bir ekstrede ise daha önce
        kaydedilmiş işlemler atlanır, yalnızca yeniler eklenir. Aynı gün aynı tutarda iki gerçek
        harcama (ör. iki kahve) ise ikisi de korunur.
      </>
    ),
  },
  {
    question: 'İşlemler nasıl kategorilere ayrılıyor?',
    answer: (
      <>
        Açıklamadaki anahtar kelimelere bakılır: MIGROS → Market, SHELL → Ulaşım, NETFLIX →
        Abonelikler gibi. Yanlış bir kategoriyi{' '}
        <Link to="/islemler" className={linkClass}>
          İşlemler
        </Link>{' '}
        sayfasında düzeltip "kural olarak kaydet" dersen, o kelime sonraki yüklemelerde de senin
        seçtiğin kategoriye gider. Kurallarını{' '}
        <Link to="/kategoriler" className={linkClass}>
          Kategoriler
        </Link>{' '}
        sayfasından yönetebilirsin.
      </>
    ),
  },
  {
    question: 'Transfer kategorisi neden raporlarda görünmüyor?',
    answer: (
      <>
        Kendi hesapların arasındaki para aktarımları ve kredi kartı borç ödemeleri ne gelirdir ne
        harcama. Bunları saymak harcamayı iki kez hesaplamak olurdu (bir kez alışverişte, bir kez
        kart ödemesinde). Bu yüzden "Transfer" türündeki kategoriler raporlara girmez.
      </>
    ),
  },
  {
    question: 'İadeler nasıl hesaplanıyor?',
    answer: (
      <>
        Bir iade gelir sayılmaz; ait olduğu kategorinin harcamasından düşülür. Örneğin 1.129 TL'lik
        bir alışverişin 349 TL'si iade edildiyse o ayın Alışveriş harcaması 780 TL görünür.
      </>
    ),
  },
  {
    question: 'Verilerim güvende mi?',
    answer: (
      <>
        Yüklediğin dosyanın kendisi saklanmaz: içindeki işlemler okunur, dosya atılır. Şifren geri
        çevrilemez şekilde (Argon2) saklanır. Verilerini yalnızca sen görebilirsin.
      </>
    ),
  },
  {
    question: 'Hesabımı nasıl silerim?',
    answer: (
      <>
        <Link to="/ayarlar" className={linkClass}>
          Ayarlar
        </Link>{' '}
        sayfasının en altındaki "Hesabı sil" bölümünden. Hesabın tüm verilerinle birlikte kalıcı
        olarak silinir.
      </>
    ),
  },
]

export function HelpPage() {
  return (
    <div className="mx-auto max-w-3xl">
      <h2 className="text-lg font-semibold text-fg">Sık sorulan sorular</h2>
      <Card className="mt-4 divide-y divide-line p-0">
        {QUESTIONS.map(({ question, answer }) => (
          <details key={question} className="group">
            <summary className="flex cursor-pointer list-none items-center justify-between gap-4 px-5 py-4 font-medium text-fg hover:bg-surface-muted/50">
              {question}
              <ChevronDown
                aria-hidden
                className="size-5 shrink-0 text-fg-faint transition-transform group-open:rotate-180"
              />
            </summary>
            <div className="px-5 pb-4 text-sm leading-relaxed text-fg-muted">{answer}</div>
          </details>
        ))}
      </Card>
    </div>
  )
}
