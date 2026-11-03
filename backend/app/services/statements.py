import hashlib
import uuid
from collections import Counter
from dataclasses import dataclass
from decimal import Decimal
from pathlib import PurePath

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import OTHER_CATEGORY, Statement, Transaction, TransactionType, User
from app.services.categories import get_default_category
from app.services.parsing.base import ParsedTransaction
from app.services.parsing.formats import normalize_description
from app.services.parsing.registry import get_parser

SUPPORTED_EXTENSIONS = {".csv", ".pdf"}
PDF_SIGNATURE = b"%PDF-"


class UnsupportedFileError(Exception):
    pass


class DuplicateStatementError(Exception):
    pass


@dataclass(frozen=True)
class ImportResult:
    statement: Statement
    imported: int
    skipped_duplicates: int


def safe_file_name(file_name: str | None) -> str:
    """Drop any client-supplied directory parts (`../../x.csv` -> `x.csv`)."""
    name = PurePath((file_name or "").replace("\\", "/")).name
    return name[:255] or "statement"


def validate_file_type(file_name: str, content: bytes) -> None:
    """Trust the file's bytes, not the extension or the client's Content-Type alone."""
    extension = PurePath(file_name).suffix.lower()
    if extension not in SUPPORTED_EXTENSIONS:
        raise UnsupportedFileError("Only PDF and CSV files are supported")
    is_pdf = content.startswith(PDF_SIGNATURE)
    if (extension == ".pdf") != is_pdf:
        raise UnsupportedFileError("The file's contents do not match its extension")


def fingerprints(transactions: list[ParsedTransaction]) -> list[str]:
    """A stable identity per transaction, used to skip ones already imported from another file.

    Identical transactions within one file (two 85 TL coffees on the same day) get different
    occurrence numbers, so both are kept; the same pair in an overlapping file maps to the
    same two fingerprints and is skipped.
    """
    seen: Counter[tuple[str, ...]] = Counter()
    result = []
    for transaction in transactions:
        key = (
            transaction.date.isoformat(),
            str(transaction.amount.quantize(Decimal("0.01"))),
            normalize_description(transaction.description).casefold(),
        )
        occurrence = seen[key]
        seen[key] += 1
        raw = "|".join((*key, str(occurrence)))
        result.append(hashlib.sha256(raw.encode()).hexdigest())
    return result


def import_statement(
    db: Session, user: User, file_name: str, content: bytes, bank_name: str | None = None
) -> ImportResult:
    """Parse a statement file and store its new transactions.

    Raises UnsupportedFileError, DuplicateStatementError or StatementParseError.
    """
    validate_file_type(file_name, content)

    file_hash = hashlib.sha256(content).hexdigest()
    already_uploaded = db.scalar(
        select(Statement.id).where(Statement.user_id == user.id, Statement.file_hash == file_hash)
    )
    if already_uploaded:
        raise DuplicateStatementError("This statement has already been uploaded")

    parser = get_parser(file_name, content)
    if parser is None:
        raise UnsupportedFileError("Only PDF and CSV files are supported")
    parsed = parser.parse(content)

    parsed_with_fingerprints = list(
        zip(parsed.transactions, fingerprints(parsed.transactions), strict=True)
    )
    existing = set(
        db.scalars(
            select(Transaction.fingerprint).where(
                Transaction.user_id == user.id,
                Transaction.fingerprint.in_([fp for _, fp in parsed_with_fingerprints]),
            )
        )
    )
    new = [(t, fp) for t, fp in parsed_with_fingerprints if fp not in existing]
    if not new:
        raise DuplicateStatementError("All transactions in this file were already imported")

    other = get_default_category(db, OTHER_CATEGORY)
    dates = [t.date for t in parsed.transactions]
    statement = Statement(
        user_id=user.id,
        file_name=file_name,
        bank_name=bank_name or parsed.bank_name,
        file_hash=file_hash,
        period_start=min(dates),
        period_end=max(dates),
        transactions=[
            Transaction(
                user_id=user.id,
                date=t.date,
                description=t.description[:500],
                amount=abs(t.amount),
                type=TransactionType.EXPENSE if t.amount < 0 else TransactionType.INCOME,
                fingerprint=fp,
                category_id=other.id,
            )
            for t, fp in new
        ],
    )
    db.add(statement)
    try:
        db.commit()
    except IntegrityError as exc:
        # A concurrent upload of the same file or transactions won the race.
        db.rollback()
        raise DuplicateStatementError("This statement has already been uploaded") from exc

    return ImportResult(
        statement=statement,
        imported=len(new),
        skipped_duplicates=len(parsed.transactions) - len(new),
    )


def list_statements(db: Session, user: User) -> list[tuple[Statement, int]]:
    """The user's statements, newest first, with their transaction counts."""
    rows = db.execute(
        select(Statement, func.count(Transaction.id))
        .outerjoin(Transaction, Transaction.statement_id == Statement.id)
        .where(Statement.user_id == user.id)
        .group_by(Statement.id)
        .order_by(Statement.uploaded_at.desc())
    )
    return [(statement, count) for statement, count in rows]


def get_user_statement(db: Session, user: User, statement_id: uuid.UUID) -> Statement | None:
    return db.scalar(
        select(Statement).where(Statement.id == statement_id, Statement.user_id == user.id)
    )
