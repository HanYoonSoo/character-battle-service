from __future__ import annotations

from uuid import UUID

from app.schemas.base import ApiSchema


class SessionBootstrapResponse(ApiSchema):
    visitor_id: UUID
    is_new: bool
