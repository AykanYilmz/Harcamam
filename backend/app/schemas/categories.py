import uuid
from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

from app.models import CategoryKind

CategoryName = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=50)]
HexColor = Annotated[str, Field(pattern=r"^#[0-9a-fA-F]{6}$")]
IconName = Annotated[str, Field(pattern=r"^[a-z0-9-]{1,50}$")]


class CategoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    color: str
    icon: str
    kind: CategoryKind
    is_default: bool


class CategoryCreate(BaseModel):
    name: CategoryName
    color: HexColor
    icon: IconName
    kind: CategoryKind = CategoryKind.EXPENSE


class CategoryUpdate(BaseModel):
    name: CategoryName | None = None
    color: HexColor | None = None
    icon: IconName | None = None
    kind: CategoryKind | None = None


class RuleRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    keyword: str
    category_id: uuid.UUID
    created_at: datetime


class RuleCreate(BaseModel):
    keyword: str = Field(min_length=1, max_length=100)
    category_id: uuid.UUID
    apply_to_existing: bool = True


class RuleSaveResult(BaseModel):
    rule: RuleRead
    updated_transactions: int
