import uuid
from typing import Annotated

from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status

from app.core.config import get_settings
from app.core.dependencies import CurrentUser, DbSession
from app.models import Statement
from app.schemas.statements import StatementImportResult, StatementRead
from app.services.parsing.base import StatementParseError
from app.services.statements import (
    DuplicateStatementError,
    UnsupportedFileError,
    get_user_statement,
    import_statement,
    list_statements,
    safe_file_name,
)

router = APIRouter(prefix="/statements", tags=["statements"])


def to_read(statement: Statement, transaction_count: int) -> StatementRead:
    return StatementRead(
        id=statement.id,
        file_name=statement.file_name,
        bank_name=statement.bank_name,
        period_start=statement.period_start,
        period_end=statement.period_end,
        uploaded_at=statement.uploaded_at,
        transaction_count=transaction_count,
    )


@router.post("/upload", response_model=StatementImportResult, status_code=status.HTTP_201_CREATED)
def upload_statement(
    file: Annotated[UploadFile, File(description="Bank statement as PDF or CSV")],
    current_user: CurrentUser,
    db: DbSession,
    bank_name: Annotated[str | None, Form(max_length=100)] = None,
) -> StatementImportResult:
    max_size = get_settings().max_upload_size_bytes
    # Read one byte past the limit to detect oversized files without loading more.
    content = file.file.read(max_size + 1)
    if len(content) > max_size:
        raise HTTPException(
            status_code=status.HTTP_413_CONTENT_TOO_LARGE,
            detail=f"The file is larger than {max_size // (1024 * 1024)} MB",
        )
    if not content:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, detail="The file is empty")

    try:
        result = import_statement(
            db, current_user, safe_file_name(file.filename), content, bank_name or None
        )
    except UnsupportedFileError as exc:
        raise HTTPException(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, detail=str(exc)) from exc
    except DuplicateStatementError as exc:
        raise HTTPException(status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except StatementParseError as exc:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(exc)) from exc

    return StatementImportResult(
        statement=to_read(result.statement, result.imported),
        imported=result.imported,
        skipped_duplicates=result.skipped_duplicates,
        uncategorized=result.uncategorized,
    )


@router.get("", response_model=list[StatementRead])
def get_statements(current_user: CurrentUser, db: DbSession) -> list[StatementRead]:
    return [to_read(statement, count) for statement, count in list_statements(db, current_user)]


@router.delete("/{statement_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_statement(statement_id: uuid.UUID, current_user: CurrentUser, db: DbSession) -> None:
    statement = get_user_statement(db, current_user, statement_id)
    # 404 rather than 403 for other users' statements, so their existence isn't revealed.
    if statement is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Statement not found")
    db.delete(statement)
    db.commit()
