from pydantic import BaseModel, ConfigDict, EmailStr, Field
from datetime import datetime

class ContactBase(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(..., max_length=255)
    phone_number: str = Field(..., max_length=20)
    email: EmailStr | None = None
    address: str | None = None
    tags: list[str] = Field(default_factory=list, max_length=10)


class ContactCreate(ContactBase):
    pass


class ContactUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str | None = Field(None, max_length=255)
    phone_number: str | None = Field(None, max_length=20)
    email: EmailStr | None = None
    address: str | None = None
    tags: list[str] | None = Field(None, max_length=10)


class TagResponse(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)


class ContactResponse(BaseModel):
    id: int
    name: str
    phone_number: str
    email: str | None
    address: str | None

    is_favorite: bool
    last_viewed_at: datetime | None

    created_at: datetime
    updated_at: datetime
    tags: list[TagResponse] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class ContactListResponse(BaseModel):
    contacts: list[ContactResponse]
    page: int
    limit: int
    total: int


class ContactMetricsResponse(BaseModel):
    total: int
    favorites: int
    recently_added: int
    unlabeled: int


class ContactImportRequest(BaseModel):
    rows: list[ContactCreate] = Field(..., max_length=5000)


class ContactImportError(BaseModel):
    row: int
    reason: str


class ContactImportResponse(BaseModel):
    imported: int
    skipped: int
    errors: list[ContactImportError] = Field(default_factory=list)

class FavoriteUpdate(BaseModel):
    is_favorite: bool