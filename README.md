# HesapKitap

Banka hesap ekstrelerini (PDF / CSV) yükleyip harcamaları otomatik olarak kategorize eden, aylık özet ve grafikler sunan kişisel finans uygulaması.

> 🚧 Proje geliştirme aşamasında. Yol haritası için aşağıya bakın.

## Özellikler (planlanan)

- Ekstre yükleme ve ayrıştırma (Türkçe tarih ve tutar formatları)
- Kural tabanlı otomatik kategorizasyon; kullanıcının düzeltmelerinden öğrenen kurallar
- Aylık özet, kategori dağılımı, harcama trendi ve en çok harcama yapılan yerler
- JWT ile kimlik doğrulama

## Teknolojiler

| Katman | Teknolojiler |
|---|---|
| Backend | Python 3.12, FastAPI, SQLAlchemy 2.0, Alembic, Pydantic v2 |
| Veritabanı | PostgreSQL 17 |
| Frontend | React, TypeScript, Vite, Tailwind CSS |
| Altyapı | Docker, docker-compose, GitHub Actions |
| Kod kalitesi | ruff, black, ESLint, Prettier, pre-commit |

## Hızlı başlangıç (Docker)

Gereksinim: [Docker Desktop](https://www.docker.com/products/docker-desktop/)

```bash
git clone https://github.com/AykanYilmz/Harcamam.git
cd Harcamam
cp .env.example .env
# .env içindeki JWT_SECRET'ı doldurun:
# python -c "import secrets; print(secrets.token_hex(32))"
docker compose up --build
```

| Servis | Adres |
|---|---|
| Frontend | http://localhost:5173 |
| Backend API | http://localhost:8000 |
| API dokümantasyonu (Swagger) | http://localhost:8000/docs |
| PostgreSQL | `localhost:5432` |
| Mailpit (geliştirmede gönderilen e-postalar) | http://localhost:8025 |

## Yerel geliştirme

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -e ".[dev]"

uvicorn app.main:app --reload    # sunucuyu başlat
pytest                           # testler (önce: docker compose up -d db)
ruff check . && black --check .  # lint
```

### Frontend

```bash
cd frontend
npm install

npm run dev           # geliştirme sunucusu
npm run lint          # ESLint
npm run format:check  # Prettier
npm run build         # production build
```

### Pre-commit hook'ları

Her commit öncesinde lint ve format kontrolleri otomatik çalışır. Backend sanal ortamı aktifken ve frontend bağımlılıkları kuruluyken:

```bash
pre-commit install
pre-commit run --all-files   # tüm dosyalarda elle çalıştırmak için
```

## Proje yapısı

```
├── backend/          # FastAPI uygulaması
│   ├── app/
│   │   ├── api/      # router'lar
│   │   ├── core/     # config, güvenlik, bağımlılıklar
│   │   ├── models/   # SQLAlchemy modelleri
│   │   ├── schemas/  # Pydantic şemaları
│   │   └── services/ # iş mantığı
│   └── tests/
├── frontend/         # React + Vite uygulaması
├── sample_data/      # sahte örnek ekstreler (gerçek veri yok)
└── docker-compose.yml
```

## Yol haritası

- [x] Faz 0 — Kurulum (Docker, FastAPI, React, lint ve pre-commit)
- [x] Faz 1 — Kimlik doğrulama (JWT access + refresh token)
- [x] Faz 2 — Ekstre yükleme ve ayrıştırma (CSV + PDF, mükerrer kontrolü)
- [x] Faz 3 — Kategorizasyon (anahtar kelime + kullanıcı kuralları)
- [x] Faz 4 — Raporlar (aylık özet, trend, en çok harcama yapılan yerler, işlem listesi)
- [x] Faz 5 — Frontend arayüzü (dashboard, işlemler, takvim, raporlar, kategoriler, ayarlar; açık/koyu tema)
- [ ] Faz 6 — CI, test kapsamı ve deploy
- [ ] Faz 7 — Opsiyonel geliştirmeler (ML kategorizer, bütçe, abonelik tespiti)
- [ ] Faz 8 — Dokümantasyon ve portfolyo cilası

## Güvenlik notu

Repoda **gerçek banka verisi bulunmaz**. `sample_data/` altındaki tüm dosyalar sahtedir; `.gitignore` bu klasör dışındaki PDF, CSV ve Excel dosyalarını engeller.
