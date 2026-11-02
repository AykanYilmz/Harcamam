"""Generates the FAKE sample statements in sample_data/.

Every bank, account and transaction here is invented. Run from backend/:

    python scripts/generate_sample_data.py --font C:/Windows/Fonts/arial.ttf

The PDF needs a Unicode TrueType font for Turkish letters (e.g. DejaVuSans.ttf on Linux).
"""

import argparse
from decimal import Decimal
from pathlib import Path

from fpdf import FPDF

SAMPLE_DIR = Path(__file__).resolve().parents[2] / "sample_data"
BANK = "ÖRNEK BANK A.Ş."

Row = tuple[str, str, str]  # date, description, signed amount

ACCOUNT_SEPTEMBER: list[Row] = [
    ("01.09.2026", "MAAŞ ÖDEMESİ - ÖRNEK TEKNOLOJİ A.Ş.", "45000.00"),
    ("01.09.2026", "KİRA ÖDEMESİ", "-15000.00"),
    ("02.09.2026", "MIGROS KADIKÖY İSTANBUL", "-1245.80"),
    ("03.09.2026", "İSTANBULKART DOLUM", "-500.00"),
    # Two identical purchases on the same day: both are real and must both be imported.
    ("04.09.2026", "STARBUCKS MODA", "-95.00"),
    ("04.09.2026", "STARBUCKS MODA", "-95.00"),
    ("05.09.2026", "NETFLIX.COM", "-149.99"),
    ("05.09.2026", "SPOTIFY", "-59.99"),
    ("07.09.2026", "SHELL KADIKÖY", "-1850.00"),
    ("08.09.2026", "A101 MODA", "-312.45"),
    ("10.09.2026", "TURKCELL FATURA", "-429.00"),
    ("11.09.2026", "İGDAŞ DOĞALGAZ", "-684.30"),
    ("12.09.2026", "YEMEKSEPETİ", "-387.50"),
    ("14.09.2026", "BİM KADIKÖY", "-198.75"),
    ("15.09.2026", "ATM NAKİT ÇEKİM", "-2000.00"),
    ("16.09.2026", "ECZANE ŞİFA", "-146.20"),
    ("18.09.2026", "LC WAIKIKI", "-899.99"),
    ("20.09.2026", "ŞOK MARKET", "-164.90"),
    ("21.09.2026", "CINEMAXIMUM", "-340.00"),
    ("23.09.2026", "TRENDYOL", "-1129.00"),
    ("24.09.2026", "CK BOĞAZİÇİ ELEKTRİK", "-512.60"),
    ("26.09.2026", "GETİR", "-245.40"),
    ("27.09.2026", "OPET ATAŞEHİR", "-1600.00"),
    ("28.09.2026", "MIGROS KADIKÖY İSTANBUL", "-876.15"),
    ("29.09.2026", "İSKİ SU FATURASI", "-238.70"),
    ("30.09.2026", "FAİZ GELİRİ", "87.35"),
]

# Starts on 26.09 so it overlaps the last five September transactions above.
ACCOUNT_OCTOBER: list[Row] = ACCOUNT_SEPTEMBER[-5:] + [
    ("01.10.2026", "MAAŞ ÖDEMESİ - ÖRNEK TEKNOLOJİ A.Ş.", "45000.00"),
    ("01.10.2026", "KİRA ÖDEMESİ", "-15000.00"),
    ("02.10.2026", "CARREFOURSA ATAŞEHİR", "-1432.60"),
    ("03.10.2026", "İSTANBULKART DOLUM", "-500.00"),
    ("05.10.2026", "NETFLIX.COM", "-149.99"),
    ("05.10.2026", "SPOTIFY", "-59.99"),
    ("06.10.2026", "YOUTUBE PREMIUM", "-57.99"),
    ("08.10.2026", "BP MASLAK", "-1725.00"),
    ("09.10.2026", "MIGROS KADIKÖY İSTANBUL", "-1088.40"),
    ("10.10.2026", "TURKCELL FATURA", "-429.00"),
    ("12.10.2026", "İGDAŞ DOĞALGAZ", "-912.75"),
    ("14.10.2026", "YEMEKSEPETİ", "-455.00"),
    ("15.10.2026", "GELEN HAVALE - BORÇ İADESİ", "1500.00"),
    ("17.10.2026", "A101 MODA", "-276.30"),
    ("19.10.2026", "ECZANE ŞİFA", "-89.50"),
    ("21.10.2026", "ATM NAKİT ÇEKİM", "-1000.00"),
    ("23.10.2026", "BİM KADIKÖY", "-221.10"),
    ("24.10.2026", "CK BOĞAZİÇİ ELEKTRİK", "-498.20"),
    ("26.10.2026", "SHELL KADIKÖY", "-1900.00"),
    ("28.10.2026", "KOTON", "-649.90"),
    ("29.10.2026", "İSKİ SU FATURASI", "-251.40"),
    ("31.10.2026", "FAİZ GELİRİ", "92.10"),
]

# Credit card statement: purchases in the debit column, payments/refunds in credit.
CARD_OCTOBER: list[Row] = [
    ("02.10.2026", "AMAZON.COM.TR", "-1249.00"),
    ("04.10.2026", "MIGROS SANAL MARKET", "-687.35"),
    ("07.10.2026", "PEGASUS HAVA YOLLARI", "-2340.00"),
    ("09.10.2026", "DOMINOS PIZZA", "-329.00"),
    ("11.10.2026", "DECATHLON", "-1099.00"),
    ("13.10.2026", "STEAM PURCHASE", "-214.99"),
    ("15.10.2026", "ÖNCEKİ DÖNEM ÖDEMESİ", "5000.00"),
    ("18.10.2026", "ZARA", "-1799.95"),
    ("20.10.2026", "TRENDYOL İADE", "349.00"),
    ("22.10.2026", "BURGER KING", "-265.00"),
    ("25.10.2026", "HEPSİBURADA", "-899.00"),
    ("27.10.2026", "DİŞ HEKİMİ MUAYENE", "-1500.00"),
    ("30.10.2026", "APPLE.COM/BILL", "-49.99"),
]


def tr(amount: Decimal) -> str:
    """1234.5 -> '1.234,50'"""
    return f"{amount:,.2f}".replace(",", "_").replace(".", ",").replace("_", ".")


def with_balances(rows: list[Row], opening: Decimal) -> list[tuple[str, str, Decimal, Decimal]]:
    balance = opening
    result = []
    for day, description, amount in rows:
        balance += Decimal(amount)
        result.append((day, description, Decimal(amount), balance))
    return result


def write_account_csv(path: Path) -> None:
    lines = [
        f"{BANK} - HESAP HAREKETLERİ",
        "Müşteri;ÖRNEK KULLANICI",
        "IBAN;TR00 0000 0000 0000 0000 0000 00",
        "Dönem;01.09.2026 - 30.09.2026",
        "",
        "İşlem Tarihi;Açıklama;Tutar;Bakiye",
    ]
    for day, description, amount, balance in with_balances(ACCOUNT_SEPTEMBER, Decimal("12500")):
        lines.append(f"{day};{description};{tr(amount)} TL;{tr(balance)} TL")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_card_csv(path: Path) -> None:
    lines = [
        f"{BANK} KREDİ KARTI EKSTRESİ",
        "Kart No;**** **** **** 0000",
        "Hesap Kesim Tarihi;31.10.2026",
        "",
        "TARİH;AÇIKLAMA;BORÇ;ALACAK",
    ]
    for day, description, amount in CARD_OCTOBER:
        value = Decimal(amount)
        debit, credit = (tr(-value), "") if value < 0 else ("", tr(value))
        lines.append(f"{day};{description};{debit};{credit}")
    # Excel on Turkish Windows exports CSV in this encoding.
    path.write_text("\n".join(lines) + "\n", encoding="cp1254")


def write_account_pdf(path: Path, font: Path) -> None:
    widths = (28, 92, 35, 35)
    rows_per_page = 20

    pdf = FPDF()
    pdf.add_font("Body", fname=str(font))
    pdf.set_font("Body", size=10)

    def table_row(cells: tuple[str, ...]) -> None:
        for width, text in zip(widths, cells, strict=True):
            pdf.cell(width, 8, text, border=1)
        pdf.ln()

    rows = with_balances(ACCOUNT_OCTOBER, Decimal("4932.30"))
    for start in range(0, len(rows), rows_per_page):
        pdf.add_page()
        if start == 0:
            pdf.set_font_size(14)
            pdf.cell(0, 10, f"{BANK} - HESAP EKSTRESİ")
            pdf.ln()
            pdf.set_font_size(10)
            pdf.cell(0, 6, "Müşteri: ÖRNEK KULLANICI    IBAN: TR00 0000 0000 0000 0000 0000 00")
            pdf.ln()
            pdf.cell(0, 6, "Dönem: 26.09.2026 - 31.10.2026")
            pdf.ln(10)
            # Like many real statements, the header appears only on the first page.
            table_row(("Tarih", "Açıklama", "Tutar", "Bakiye"))
        for day, description, amount, balance in rows[start : start + rows_per_page]:
            table_row((day, description, f"{tr(amount)} TL", f"{tr(balance)} TL"))

    pdf.output(str(path))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--font", type=Path, required=True, help="Unicode .ttf font for the PDF")
    args = parser.parse_args()

    write_account_csv(SAMPLE_DIR / "ornek_hesap_ekstresi_2026_09.csv")
    write_card_csv(SAMPLE_DIR / "ornek_kredi_karti_2026_10.csv")
    write_account_pdf(SAMPLE_DIR / "ornek_hesap_ekstresi_2026_10.pdf", args.font)
    print(f"Sample statements written to {SAMPLE_DIR}")


if __name__ == "__main__":
    main()
