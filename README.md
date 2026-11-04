# HesapKitap

[![CI](https://github.com/AykanYilmz/Harcamam/actions/workflows/ci.yml/badge.svg)](https://github.com/AykanYilmz/Harcamam/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/AykanYilmz/Harcamam/graph/badge.svg)](https://codecov.io/gh/AykanYilmz/Harcamam)

Banka hesap ekstrelerini (PDF / CSV) yükleyip harcamaları otomatik olarak kategorize eden, aylık özet ve grafikler sunan kişisel finans uygulaması.

> 🚧 Proje geliştirme aşamasında. Yol haritası için aşağıya bakın.

## Özellikler

- Hesap ve kredi kartı ekstresi yükleme (CSV, PDF); Türkçe tarih ve tutar formatları, mükerrer işlem kontrolü
- Kural tabanlı otomatik kategorizasyon; kullanıcının düzeltmelerinden ve **Kategori Eğitimi** sayfasından öğrenen kurallar
- Aylık özet, kategori dağılımı, harcama trendi, takvim ve en çok harcama yapılan yerler; ay, istenirse kart hesap kesim gününe göre bölünür
- JWT ile kimlik doğrulama, e-posta doğrulama, açık/koyu tema

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
pytest --cov                     # testler + kapsam, %80 altı başarısız (önce: docker compose up -d db)
ruff check . && black --check .  # lint
```

### Frontend

```bash
cd frontend
npm install

npm run dev           # geliştirme sunucusu
npm run lint          # ESLint
npm run format:check  # Prettier
npm test              # Vitest
npm run build         # production build
```

### Demo hesabı

Sahte ekstrelerle (Mayıs–Ekim) dolu bir demo hesabı oluşturur; tekrar çalıştırınca hesabı sıfırlar:

```bash
docker compose exec backend python -m app.demo   # demo@hesapkitap.dev / demo12345
```

### Pre-commit hook'ları

Her commit öncesinde lint ve format kontrolleri otomatik çalışır. Backend sanal ortamı aktifken ve frontend bağımlılıkları kuruluyken:

```bash
pre-commit install
pre-commit run --all-files   # tüm dosyalarda elle çalıştırmak için
```

## Production

`docker-compose.prod.yml`, uygulamayı production imajlarıyla çalıştırır:

- **web:** Build alınmış site nginx ile sunulur. nginx `/api` isteklerini backend'e yönlendirir (aynı adres, CORS gerekmez), 6 MB'tan büyük yüklemeleri reddeder, giriş/kayıt/şifre/e-posta isteklerine rate limit uygular ve güvenlik başlıklarını ekler.
- **backend:** Yalnızca uygulama ve çalışma zamanı bağımlılıkları, root olmayan kullanıcı; açılışta migration'ları uygular. `ENVIRONMENT=production` iken geliştirme veritabanı şifresiyle ya da `https` olmayan bir site adresiyle başlamayı reddeder.
- **db:** PostgreSQL; dışarıya açık değildir.

```bash
cp .env.production.example .env.production   # bütün değerleri doldurun
docker compose -f docker-compose.prod.yml --env-file .env.production up -d --build
docker compose -f docker-compose.prod.yml --env-file .env.production exec backend python -m app.demo
```

Site `WEB_PORT` (varsayılan 80) üzerinden düz http ile yayınlanır; TLS (https) önündeki platform ya da Caddy gibi bir proxy tarafından sağlanmalıdır. API dokümantasyonu: `/api/docs`.

## CI

Her push ve pull request'te [GitHub Actions](.github/workflows/ci.yml) şunları çalıştırır: ruff, black, migration'ların modellerle uyumu, PostgreSQL'e karşı backend testleri ve kapsam ([Codecov](https://codecov.io/gh/AykanYilmz/Harcamam)), ESLint, Prettier, Vitest, frontend build ve iki production Docker imajının build'i.

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
├── docker-compose.yml        # geliştirme
└── docker-compose.prod.yml   # production
```

## Yol haritası

- [x] Faz 0 — Kurulum (Docker, FastAPI, React, lint ve pre-commit)
- [x] Faz 1 — Kimlik doğrulama (JWT access + refresh token)
- [x] Faz 2 — Ekstre yükleme ve ayrıştırma (CSV + PDF, mükerrer kontrolü)
- [x] Faz 3 — Kategorizasyon (anahtar kelime + kullanıcı kuralları)
- [x] Faz 4 — Raporlar (aylık özet, trend, en çok harcama yapılan yerler, işlem listesi)
- [x] Faz 5 — Frontend arayüzü (dashboard, işlemler, takvim, raporlar, kategoriler, ayarlar; açık/koyu tema)
- [x] Faz 6 — CI, test kapsamı, production imajları (deploy henüz yapılmadı)
- [ ] Faz 7 — Opsiyonel geliştirmeler (ML kategorizer, bütçe, abonelik tespiti)
- [ ] Faz 8 — Dokümantasyon ve portfolyo cilası

## Güvenlik notu

Repoda **gerçek banka verisi bulunmaz**. `sample_data/` altındaki tüm dosyalar sahtedir; `.gitignore` bu klasör dışındaki PDF, CSV ve Excel dosyalarını engeller.
