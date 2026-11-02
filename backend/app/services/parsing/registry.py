from app.services.parsing.base import BaseParser
from app.services.parsing.csv_parser import CsvParser
from app.services.parsing.pdf_parser import GenericPdfParser

# Tried in order; bank-specific parsers go before the generic ones.
PARSERS: list[BaseParser] = [
    CsvParser(),
    GenericPdfParser(),
]


def get_parser(file_name: str, content: bytes) -> BaseParser | None:
    return next((p for p in PARSERS if p.can_parse(file_name, content)), None)
