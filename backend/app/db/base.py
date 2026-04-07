from __future__ import annotations

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


from app.models.anonymous_user import AnonymousUser  # noqa: E402,F401
from app.models.battle import Battle  # noqa: E402,F401
from app.models.character import Character  # noqa: E402,F401
