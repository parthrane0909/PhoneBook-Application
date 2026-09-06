from datetime import datetime
import re

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class ContactBase(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(..., max_length=255)
    phone_number: str = Field(..., max_length=20)
    email: EmailStr | None = None
    address: str | None = None
    tags: list[str] = Field(default_factory=list, max_length=10)

    @field_validator("phone_number")
    @classmethod
    def validate_phone_number(cls, value: str) -> str:
        value = value.strip()
        digits = "".join(character for character in value if character.isdigit())

        if (
            not value
            or len(digits) < 7
            or len(digits) > 15
            or not re.fullmatch(r"\+?[0-9\s()\-]+", value)
        ):
            raise ValueError("Enter a valid phone number with 7–15 digits.")

        return value

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, value: list[str]) -> list[str]:
        cleaned = []
        seen = set()

        for tag in value:
            name = str(tag).strip()
            key = name.lower()

            if not name or key in seen:
                continue

            if len(name) > 80:
                raise ValueError("Each tag must be 80 characters or fewer.")

            seen.add(key)
            cleaned.append(name)

        if len(cleaned) > 10:
            raise ValueError("A contact can have at most 10 tags.")

        return cleaned


class ContactCreate(ContactBase):
    pass


class ContactUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str | None = Field(None, max_length=255)
    phone_number: str | None = Field(None, max_length=20)
    email: EmailStr | None = None
    address: str | None = None
    tags: list[str] | None = Field(None, max_length=10)

    @field_validator("phone_number")
    @classmethod
    def validate_phone_number(cls, value: str | None) -> str | None:
        if value is None:
            return value

        value = value.strip()
        digits = "".join(character for character in value if character.isdigit())

        if (
            not value
            or len(digits) < 7
            or len(digits) > 15
            or not re.fullmatch(r"\+?[0-9\s()\-]+", value)
        ):
            raise ValueError("Enter a valid phone number with 7–15 digits.")

        return value

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, value: list[str] | None) -> list[str] | None:
        if value is None:
            return value

        cleaned = []
        seen = set()

        for tag in value:
            name = str(tag).strip()
            key = name.lower()

            if not name or key in seen:
                continue

            if len(name) > 80:
                raise ValueError("Each tag must be 80 characters or fewer.")

            seen.add(key)
            cleaned.append(name)

        if len(cleaned) > 10:
            raise ValueError("A contact can have at most 10 tags.")

        return cleaned


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