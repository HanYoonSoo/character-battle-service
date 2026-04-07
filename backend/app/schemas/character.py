from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import Field, model_validator

from app.schemas.base import ApiSchema


class CharacterCreateRequest(ApiSchema):
    name: str = Field(min_length=1, max_length=20)
    power_description: str = Field(min_length=1, max_length=255)


class CharacterUpdateRequest(ApiSchema):
    name: str | None = Field(default=None, min_length=1, max_length=20)
    power_description: str | None = Field(default=None, min_length=1, max_length=255)

    @model_validator(mode="after")
    def ensure_any_field(self) -> "CharacterUpdateRequest":
        if self.name is None and self.power_description is None:
            raise ValueError("At least one field must be provided for character updates.")
        return self


class CharacterResponse(ApiSchema):
    id: UUID
    owner_visitor_id: UUID
    name: str
    power_description: str
    created_at: datetime
    updated_at: datetime


class CharacterListResponse(ApiSchema):
    items: list[CharacterResponse]
