import datetime as dt
from enum import StrEnum
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, Response, status

from app.core.dependencies import CurrentUser, DbSession
from app.services import exports

router = APIRouter(prefix="/exports", tags=["exports"])

# Long enough for any report, short enough that one request can't build a huge file.
MAX_DAYS = 3 * 366


class ExportFormat(StrEnum):
    XLSX = "xlsx"
    CSV = "csv"


MEDIA_TYPES = {
    ExportFormat.XLSX: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    ExportFormat.CSV: "text/csv; charset=utf-8",
}


@router.get(
    "/transactions",
    response_class=Response,
    responses={200: {"content": {media: {} for media in MEDIA_TYPES.values()}}},
)
def export_transactions(
    current_user: CurrentUser,
    db: DbSession,
    start: Annotated[dt.date, Query(description="First day, inclusive")],
    end: Annotated[dt.date, Query(description="Last day, inclusive")],
    file_format: Annotated[ExportFormat, Query(alias="format")] = ExportFormat.XLSX,
) -> Response:
    """The transactions from `start` to `end`; the Excel file also has monthly and
    per-category totals."""
    if end < start:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, detail="end is before start")
    if (end - start).days > MAX_DAYS:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_CONTENT, detail="At most three years at a time"
        )

    if file_format is ExportFormat.XLSX:
        content: bytes = exports.xlsx(db, current_user, start, end)
    else:
        content = exports.csv_text(db, current_user, start, end).encode("utf-8")
    file_name = f"hesapkitap_{start}_{end}.{file_format.value}"
    return Response(
        content,
        media_type=MEDIA_TYPES[file_format],
        headers={"Content-Disposition": f'attachment; filename="{file_name}"'},
    )
