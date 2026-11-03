# Harcamam — Kişisel Finans ve Harcama Analizi Uygulaması

Bu dosya projenin ana talimatıdır. Her oturumda önce bunu oku ve buradaki plana göre ilerle.

## Ben kimim, ne istiyorum
- Bilgisayar mühendisliği mezunuyum (junior). Python/FastAPI, Java, C#, PostgreSQL ve Docker biliyorum. Frontend tarafında daha az deneyimliyim.
- Bu proje GitHub portfolyomda ve CV'mde duracak. O yüzden kod kalitesi, test, dokümantasyon ve canlı demo önemli.
- Öğrenmek istiyorum. Önemli bir karar verdiğinde (kütüphane seçimi, mimari, veritabanı şeması) kısaca **neden** öyle yaptığını açıkla.

## Projenin amacı
Kullanıcı banka hesap ekstresini (PDF veya CSV) yükler. Uygulama işlemleri ayrıştırır, her harcamayı otomatik olarak kategorize eder (market, ulaşım, fatura, yemek, eğlence vb.) ve aylık özet ile grafikler gösterir. Kullanıcı yanlış kategorileri düzeltebilir. Sistem bu düzeltmelerden öğrenir.

## Teknoloji yığını
- **Backend:** Python 3.12, FastAPI, SQLAlchemy 2.0, Alembic, Pydantic v2
- **Veritabanı:** PostgreSQL
- **Kimlik doğrulama:** JWT (access + refresh token), şifreler bcrypt/argon2 ile hash'lenir
- **Ekstre ayrıştırma:** pdfplumber (PDF), Python `csv` modülü (CSV; pandas bu iş için gereksiz ağır bulundu)
- **Kategorizasyon:** önce kural tabanlı (anahtar kelime eşleşmesi + kullanıcı kuralları), sonra opsiyonel olarak scikit-learn (TF-IDF + Logistic Regression)
- **Frontend:** React + TypeScript + Vite, Tailwind CSS, Recharts (grafikler), TanStack Query (API istekleri)
- **Test:** pytest (backend), Vitest (frontend, temel düzeyde)
- **Altyapı:** Docker, docker-compose, GitHub Actions (CI)
- **Kod kalitesi:** ruff + black (Python), ESLint + Prettier (TS)

## Proje yapısı
```
harcamam/
├── backend/
│   ├── app/
│   │   ├── api/          # router'lar (auth, statements, transactions, categories, reports)
│   │   ├── core/         # config, security, dependencies
│   │   ├── models/       # SQLAlchemy modelleri
│   │   ├── schemas/      # Pydantic şemaları
│   │   ├── services/     # iş mantığı (parser, categorizer, report)
│   │   └── main.py
│   ├── alembic/
│   ├── tests/
│   └── Dockerfile
├── frontend/
│   ├── src/
│   └── Dockerfile
├── sample_data/          # SAHTE örnek ekstreler (gerçek veri asla yok)
├── docker-compose.yml
├── .github/workflows/ci.yml
└── README.md
```

## Veri modeli (başlangıç)
- **User:** id, email, password_hash, created_at
- **Statement:** id, user_id, file_name, bank_name, period_start, period_end, uploaded_at
- **Transaction:** id, user_id, statement_id, date, description, amount, type (gelir/gider), category_id, is_manually_categorized
- **Category:** id, user_id (null ise varsayılan kategori), name, color, icon
- **CategoryRule:** id, user_id, keyword, category_id (kullanıcının öğrettiği kurallar)

---

## Yol haritası — fazlar

**Kural:** Fazları sırayla yap. Her fazın sonunda testleri çalıştır, ne yaptığını özetle ve bir sonraki faza geçmeden önce bana sor. Her fazı mantıklı, küçük commit'lere böl ve Conventional Commits formatında commit mesajı öner (`feat:`, `fix:`, `test:`, `docs:`, `chore:`).

### Faz 0 — Kurulum
- [x] Repo yapısını oluştur, `.gitignore`, `.env.example`, `README.md` taslağı
- [x] docker-compose ile PostgreSQL + backend + frontend ayağa kalksın
- [x] FastAPI'de `/health` endpoint'i, React'te boş bir ana sayfa
- [x] ruff, black, ESLint, Prettier ayarları ve pre-commit hook'ları

### Faz 1 — Kimlik doğrulama
- [x] User modeli + Alembic migration
- [x] `/auth/register`, `/auth/login`, `/auth/refresh`, `/auth/me`
- [x] Şifre hash'leme, JWT üretimi/doğrulama, korumalı endpoint dependency'si
- [x] Testler: başarılı kayıt, tekrar eden email, hatalı şifre, süresi dolmuş token

### Faz 2 — Ekstre yükleme ve ayrıştırma
- [x] Statement ve Transaction modelleri
- [x] `/statements/upload`: PDF ve CSV kabul etsin, dosya boyutu ve türü doğrulansın
- [x] Parser'ı **strateji deseni** ile yaz: `BaseParser` arayüzü + `CsvParser`, `GenericPdfParser`. İleride banka bazlı parser eklemek kolay olsun.
- [x] Türkçe formatları doğru işle: tarih `GG.AA.YYYY`, tutar `1.234,56 TL`, negatif/pozitif ayrımı
- [x] Aynı ekstre iki kez yüklenirse mükerrer işlem oluşmasın
- [x] `sample_data/` içine 2–3 **sahte** örnek ekstre (CSV + PDF) oluştur
- [x] Testler: her parser için örnek dosyalarla birim testleri, bozuk dosya senaryosu

### Faz 3 — Kategorizasyon
- [x] Varsayılan kategoriler (seed): Market, Yemek, Ulaşım, Faturalar, Kira, Eğlence, Sağlık, Giyim, Abonelikler, Nakit Çekim, Gelir, Diğer (+ sonradan eklenen: Alışveriş, Transfer)
- [x] Kural tabanlı kategorizer: Türkiye'ye özgü anahtar kelimeler (ör. MIGROS, A101, BIM, SOK → Market; SHELL, OPET → Ulaşım; NETFLIX, SPOTIFY → Abonelikler)
- [x] Kullanıcı bir işlemin kategorisini değiştirince "bunu kural olarak kaydet" seçeneği sunulsun. Sonraki yüklemelerde bu kural öncelikli uygulansın.
- [x] `PATCH /transactions/{id}` (kategori düzeltme), toplu düzeltme endpoint'i
- [x] Testler: kural önceliği (kullanıcı kuralı > varsayılan kural), eşleşme olmayınca "Diğer"

### Faz 4 — Raporlar ve API'nin tamamlanması
- [x] `/reports/monthly`: kategori bazlı toplam, gelir-gider, önceki aya göre değişim
- [x] `/reports/trend`: son 6–12 ayın aylık harcama trendi
- [x] `/reports/top-merchants`: en çok harcama yapılan yerler
- [x] İşlem listesi: sayfalama, tarih aralığı, kategori ve metin filtresi
- [x] Testler: rapor hesaplamalarının doğruluğu

### Faz 5 — Frontend
- [ ] Giriş/kayıt sayfaları, token yönetimi, korumalı route'lar
- [ ] Dashboard: bu ayın özeti (kartlar), kategori pasta grafiği, aylık trend çizgi grafiği
- [ ] Ekstre yükleme sayfası (sürükle-bırak, yükleme durumu, hata mesajları)
- [ ] İşlemler tablosu: filtreleme, kategori düzeltme (satır içi dropdown)
- [ ] Kategoriler ve kurallar yönetim sayfası
- [ ] Mobil uyumlu, temiz ve sade tasarım. Arayüz dili Türkçe.

### Faz 6 — Kalite ve altyapı
- [ ] GitHub Actions: lint + backend testleri + frontend build. Her push ve PR'da çalışsın.
- [ ] Backend test coverage en az %80, README'ye coverage rozeti
- [ ] Production için Dockerfile'lar (multi-stage build), docker-compose.prod.yml
- [ ] Ortam değişkenleri ile config, gizli bilgiler asla kodda değil
- [ ] Ücretsiz bir platforma deploy ve canlı demo linki. Demo kullanıcısı + sahte veriyle dolu hesap.

### Faz 7 — Opsiyonel geliştirmeler (vakit kalırsa)
- [ ] ML tabanlı kategorizer: kullanıcının düzelttiği işlemlerle eğitilen TF-IDF + Logistic Regression. Kural eşleşmeyince devreye girsin, güven skoru düşükse "Diğer".
- [ ] Bütçe hedefleri: kategori bazlı aylık limit, aşılınca uyarı
- [ ] Abonelik tespiti: her ay tekrar eden ödemeleri otomatik bul
- [ ] Rapor dışa aktarma (Excel/PDF)

### Faz 8 — Portfolyo cilası
- [ ] README: proje tanıtımı, ekran görüntüleri/GIF, mimari diyagram (Mermaid), kurulum adımları, API dokümantasyonu linki (FastAPI /docs), kullanılan teknolojiler, öğrendiklerim
- [ ] Kod içinde gereksiz yorum yok, anlamlı isimlendirme, tutarlı yapı

---

## Çalışma kuralları
- Kod (değişken, fonksiyon, sınıf isimleri, commit mesajları) **İngilizce**. Arayüz metinleri ve bana yaptığın açıklamalar **Türkçe**.
- Büyük bir değişiklikten önce kısa bir plan sun, onayımı al.
- Her yeni özellik için test yaz. Testler geçmeden "bitti" deme.
- Gereksiz bağımlılık ekleme. Eklediğin her paketi neden eklediğini söyle.
- Güvenlik: SQL injection, dosya yükleme doğrulaması, şifre ve token güvenliği, CORS ayarları. Gerçek banka verisi asla repoya girmesin.
- Bir şeyden emin değilsen tahmin etme, bana sor.
- Faz bittiğinde bu dosyadaki ilgili checkbox'ları `[x]` olarak işaretle.

## Başlangıç
Faz 0 ile başla. Önce kurulum planını kısaca anlat, sonra uygula.
