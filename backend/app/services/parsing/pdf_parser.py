import io
import re

import pdfplumber
from pdfplumber.pdf import PDF

from app.services.parsing.base import (
    BaseParser,
    ParsedStatement,
    ParsedTransaction,
    StatementParseError,
)
from app.services.parsing.columns import ColumnMap, detect_columns, row_to_transaction
from app.services.parsing.formats import normalize_description, parse_amount, parse_date

# A crafted PDF can be small on disk but have thousands of pages; statements never do.
MAX_PAGES = 50

_AMOUNT = r"[-+]?[\d.]+,\d{2}-?(?:\s*(?:TL|TRY|₺))?"
# "05.10.2026  MIGROS KADIKOY  -1.234,56 TL  [balance]" for PDFs without ruled tables.
_TEXT_LINE = re.compile(
    rf"^(?P<date>\d{{2}}[./]\d{{2}}[./]\d{{4}})\s+(?P<description>.+?)\s+"
    rf"(?P<amount>{_AMOUNT})(?:\s+{_AMOUNT})?$"
)


def _from_tables(pdf: PDF) -> list[ParsedTransaction]:
    transactions = []
    # Kept across pages: continuation pages often repeat the table without its header.
    columns: ColumnMap | None = None
    for page_number, page in enumerate(pdf.pages, start=1):
        for table in page.extract_tables():
            for row in table:
                if detected := detect_columns(row):
                    columns = detected
                elif columns:
                    label = f"Page {page_number}"
                    if transaction := row_to_transaction(row, columns, row_label=label):
                        transactions.append(transaction)
    return transactions


def _from_text(pdf: PDF) -> list[ParsedTransaction]:
    transactions = []
    for page in pdf.pages:
        for line in (page.extract_text() or "").splitlines():
            match = _TEXT_LINE.match(line.strip())
            if not match:
                continue
            try:
                amount = parse_amount(match["amount"])
                date = parse_date(match["date"])
            except ValueError:
                continue
            if amount != 0:
                description = normalize_description(match["description"])
                transactions.append(ParsedTransaction(date, description, amount))
    return transactions


def _has_text(pdf: PDF) -> bool:
    return any((page.extract_text() or "").strip() for page in pdf.pages)


class GenericPdfParser(BaseParser):
    def can_parse(self, file_name: str, content: bytes) -> bool:
        return content.startswith(b"%PDF-")

    def parse(self, content: bytes) -> ParsedStatement:
        try:
            pdf = pdfplumber.open(io.BytesIO(content))
        except Exception as exc:  # pdfminer raises many unrelated types for broken files
            raise StatementParseError(
                "The PDF could not be opened (it may be damaged or password-protected)"
            ) from exc

        with pdf:
            if len(pdf.pages) > MAX_PAGES:
                raise StatementParseError(f"The PDF has more than {MAX_PAGES} pages")
            try:
                transactions = _from_tables(pdf) or _from_text(pdf)
                has_text = transactions or _has_text(pdf)
            except StatementParseError:
                raise
            except Exception as exc:
                raise StatementParseError("The PDF could not be read") from exc

        if not has_text:
            raise StatementParseError(
                "The PDF contains no text; scanned statements are not supported"
            )
        if not transactions:
            raise StatementParseError("No transactions found in the file")
        return ParsedStatement(transactions=transactions)
