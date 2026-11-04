"""Writes the FAKE sample statements in sample_data/ (data: app/demo/statements.py).

Every bank, account and transaction is invented. Run from backend/:

    python scripts/generate_sample_data.py --font C:/Windows/Fonts/arial.ttf

The PDF needs a Unicode TrueType font for Turkish letters (e.g. DejaVuSans.ttf on Linux).
"""

import argparse
from decimal import Decimal
from pathlib import Path

from fpdf import FPDF

from app.demo.statements import ACCOUNT_OCTOBER, BANK, account_csvs, card_csv, tr, with_balances

SAMPLE_DIR = Path(__file__).resolve().parents[2] / "sample_data"
# The committed PDF's opening balance; kept so regenerating it doesn't change its contents.
OCTOBER_PDF_OPENING = Decimal("4932.30")


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

    rows = with_balances(ACCOUNT_OCTOBER, OCTOBER_PDF_OPENING)
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

    for file_name, text in account_csvs():
        (SAMPLE_DIR / file_name).write_text(text, encoding="utf-8")
    # Excel on Turkish Windows exports CSV in this encoding.
    (SAMPLE_DIR / "ornek_kredi_karti_2026_10.csv").write_text(card_csv(), encoding="cp1254")
    write_account_pdf(SAMPLE_DIR / "ornek_hesap_ekstresi_2026_10.pdf", args.font)
    print(f"Sample statements written to {SAMPLE_DIR}")


if __name__ == "__main__":
    main()
