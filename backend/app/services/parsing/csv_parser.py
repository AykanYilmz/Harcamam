import csv
import io

from app.services.parsing.base import BaseParser, ParsedStatement, StatementParseError
from app.services.parsing.columns import ColumnMap, detect_columns, row_to_transaction

# UTF-8 first; Excel on Turkish Windows saves CSV files as cp1254.
ENCODINGS = ("utf-8-sig", "cp1254")
DELIMITERS = (";", ",", "\t")
# Banks often put account details above the table, so the header isn't always the first row.
MAX_HEADER_SEARCH_ROWS = 20


def decode(content: bytes) -> str:
    if b"\x00" in content:
        raise StatementParseError("The file is not a text CSV file")
    for encoding in ENCODINGS:
        try:
            return content.decode(encoding)
        except UnicodeDecodeError:
            continue
    raise StatementParseError("Could not detect the file's text encoding")


def find_table(text: str) -> tuple[list[list[str]], ColumnMap, int]:
    """Return the rows, the detected columns and the header's row index."""
    for delimiter in DELIMITERS:
        rows = list(csv.reader(io.StringIO(text), delimiter=delimiter))
        for index, row in enumerate(rows[:MAX_HEADER_SEARCH_ROWS]):
            if columns := detect_columns(row):
                return rows, columns, index
    raise StatementParseError("Could not find the transaction columns (date, description, amount)")


class CsvParser(BaseParser):
    def can_parse(self, file_name: str, content: bytes) -> bool:
        return file_name.lower().endswith(".csv")

    def parse(self, content: bytes) -> ParsedStatement:
        text = decode(content)
        rows, columns, header_index = find_table(text)

        transactions = []
        for index in range(header_index + 1, len(rows)):
            row = rows[index]
            if not any(cell.strip() for cell in row):
                continue
            # Row numbers in messages match what the user sees in a spreadsheet (1-based).
            transaction = row_to_transaction(row, columns, row_label=f"Row {index + 1}")
            if transaction:
                transactions.append(transaction)

        if not transactions:
            raise StatementParseError("No transactions found in the file")
        return ParsedStatement(transactions=transactions)
