from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Battle(Base):
    __tablename__ = "battles"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    requested_by_user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("anonymous_users.id"),
        index=True,
        nullable=False,
    )
    left_character_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("characters.id"), nullable=False)
    right_character_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("characters.id"), nullable=False)
    left_character_name_snapshot: Mapped[str] = mapped_column(String(20), nullable=False)
    right_character_name_snapshot: Mapped[str] = mapped_column(String(20), nullable=False)
    left_character_description_snapshot: Mapped[str] = mapped_column(Text, nullable=False)
    right_character_description_snapshot: Mapped[str] = mapped_column(Text, nullable=False)
    winner_character_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("characters.id"),
        nullable=True,
    )
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    explanation: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    winner_recorded_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
