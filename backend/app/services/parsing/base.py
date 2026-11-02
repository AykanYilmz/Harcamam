from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal


@dataclass(frozen=True)
class ParsedTransaction:
    date: date
    description: str
    # Signed from the account holder's point of view: negative means money went out.
    amount: Decimal


@dataclass(frozen=True)
class ParsedStatement:
    transactions: list[ParsedTransaction] = field(default_factory=list)
    bank_name: str | None = None


class StatementParseError(Exception):
    """The file is of a supported type but its contents could not be read as a statement."""


class BaseParser(ABC):
    """One strategy for turning a statement file into transactions.

    To support a new bank format, subclass this, make `can_parse` recognize the format and
    register the instance in `app.services.parsing.registry.PARSERS` before the generic parsers.
    """

    @abstractmethod
    def can_parse(self, file_name: str, content: bytes) -> bool: ...

    @abstractmethod
    def parse(self, content: bytes) -> ParsedStatement: ...
