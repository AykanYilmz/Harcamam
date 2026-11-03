"""Builds small PDFs for parser tests. Uses a core font, so text must be Latin-1."""

from fpdf import FPDF

COLUMN_WIDTHS = (30, 90, 40)


def _new_pdf() -> FPDF:
    pdf = FPDF()
    pdf.set_font("Helvetica", size=10)
    return pdf


def _table_row(pdf: FPDF, cells: tuple[str, ...]) -> None:
    for width, text in zip(COLUMN_WIDTHS, cells, strict=True):
        pdf.cell(width, 8, text, border=1)
    pdf.ln()


def table_pdf(header: tuple[str, ...], *pages: list[tuple[str, ...]]) -> bytes:
    """A ruled table; the header is drawn only on the first page, like many bank statements."""
    pdf = _new_pdf()
    for page_number, rows in enumerate(pages):
        pdf.add_page()
        if page_number == 0:
            _table_row(pdf, header)
        for row in rows:
            _table_row(pdf, row)
    return bytes(pdf.output())


def text_pdf(lines: list[str], copies: int = 1) -> bytes:
    """Plain lines of text without table borders, printed on `copies` identical pages."""
    pdf = _new_pdf()
    for _ in range(copies):
        pdf.add_page()
        for line in lines:
            pdf.cell(0, 8, line)
            pdf.ln()
    return bytes(pdf.output())


def blank_pdf(pages: int = 1) -> bytes:
    """Pages with no text, like a scanned statement."""
    pdf = _new_pdf()
    for _ in range(pages):
        pdf.add_page()
    return bytes(pdf.output())
