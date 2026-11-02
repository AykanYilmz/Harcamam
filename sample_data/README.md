# Örnek ekstreler

Bu klasördeki **tüm dosyalar sahtedir.** Banka, müşteri, IBAN ve işlemler uydurmadır. Gerçek banka verisi bu repoya asla eklenmez.

| Dosya | Biçim | Neyi gösterir |
|---|---|---|
| `ornek_hesap_ekstresi_2026_09.csv` | UTF-8, `;` ayraç, tek tutar kolonu | Tablonun üstünde hesap bilgisi satırları; aynı gün iki özdeş harcama |
| `ornek_kredi_karti_2026_10.csv` | cp1254 (Windows Türkçe), Borç/Alacak kolonları | Kredi kartı ekstresi, iade ve ödeme satırları |
| `ornek_hesap_ekstresi_2026_10.pdf` | Tablolu PDF, 2 sayfa | Başlık yalnızca ilk sayfada; Eylül CSV'siyle son 5 işlemi çakışıyor (mükerrer kontrolü) |

Dosyalar [`backend/scripts/generate_sample_data.py`](../backend/scripts/generate_sample_data.py) ile üretilir:

```bash
cd backend
python scripts/generate_sample_data.py --font C:/Windows/Fonts/arial.ttf
# Linux: --font /usr/share/fonts/truetype/dejavu/DejaVuSans.ttf
```
