import io
import re
from collections.abc import Callable
from decimal import Decimal

import pdfplumber
from pdfplumber.page import Page
from pdfplumber.pdf import PDF

from app.services.parsing.base import (
    BaseParser,
    ParsedStatement,
    ParsedTransaction,
    StatementParseError,
)
from app.services.parsing.columns import ColumnMap, detect_columns, row_to_transaction
from app.services.parsing.formats import (
    normalize_description,
    normalize_text,
    parse_amount,
    parse_card_amount,
    parse_date,
)

# A crafted PDF can be small on disk but have thousands of pages; statements never do.
MAX_PAGES = 50

_AMOUNT = r"[-+]?[\d.]+,\d{2}[-+]?(?:\s*(?:TL|TRY|₺))?"
# "05.10.2026  MIGROS KADIKOY  -1.234,56 TL  [balance]" for PDFs without ruled tables.
_TEXT_LINE = re.compile(
    rf"^(?P<date>\d{{2}}[./]\d{{2}}[./]\d{{4}})\s+(?P<description>.+?)\s+"
    rf"(?P<amount>{_AMOUNT})(?:\s+{_AMOUNT})?$"
)


# Phrases found on credit card statements but not on account statements.
_CARD_MARKERS = ("hesap kesim tarihi", "son odeme tarihi", "asgari odeme", "kart limiti")

AmountParser = Callable[[str], Decimal]


def _unique_pages(pdf: PDF) -> list[tuple[int, Page, str]]:
    """Pages with their number and text, skipping exact copies of an earlier page.

    Some banks print the whole statement twice in one file; reading both would import
    every transaction twice.
    """
    seen: set[str] = set()
    pages = []
    for number, page in enumerate(pdf.pages, start=1):
        text = page.extract_text() or ""
        if text.strip() and text in seen:
            continue
        seen.add(text)
        pages.append((number, page, text))
    return pages


def _is_card_statement(texts: list[str]) -> bool:
    text = normalize_text(" ".join(texts))
    return sum(marker in text for marker in _CARD_MARKERS) >= 2


def _from_tables(
    pages: list[tuple[int, Page, str]], amount_parser: AmountParser
) -> list[ParsedTransaction]:
    transactions = []
    # Kept across pages: continuation pages often repeat the table without its header.
    columns: ColumnMap | None = None
    for page_number, page, _ in pages:
        for table in page.extract_tables():
            for row in table:
                if detected := detect_columns(row):
                    columns = detected
                elif columns:
                    label = f"Page {page_number}"
                    if transaction := row_to_transaction(row, columns, label, amount_parser):
                        transactions.append(transaction)
    return transactions


def _from_text(
    pages: list[tuple[int, Page, str]], amount_parser: AmountParser
) -> list[ParsedTransaction]:
    transactions = []
    for _, _, text in pages:
        for line in text.splitlines():
            match = _TEXT_LINE.match(line.strip())
            if not match:
                continue
            try:
                amount = amount_parser(match["amount"])
                date = parse_date(match["date"])
            except ValueError:
                continue
            if amount != 0:
                description = normalize_description(match["description"])
                transactions.append(ParsedTransaction(date, description, amount))
    return transactions


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
                pages = _unique_pages(pdf)
                texts = [text for _, _, text in pages]
                amount_parser = parse_card_amount if _is_card_statement(texts) else parse_amount
                transactions = _from_tables(pages, amount_parser) or _from_text(
                    pages, amount_parser
                )
                has_text = any(text.strip() for text in texts)
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
