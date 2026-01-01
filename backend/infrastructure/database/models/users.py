from sqlalchemy import BIGINT, String
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base, TimestampMixin, TableNameMixin, int_pk


class User(Base, TableNameMixin, TimestampMixin):
    id: Mapped[int_pk] = mapped_column(BIGINT)
    first_name: Mapped[str | None]
    last_name: Mapped[str | None]
    username: Mapped[str | None]
    language: Mapped[str] = mapped_column(String, server_default="en")

    #  joinedload - для m2o и o2o связей
    #  selectinload - для o2m и m2m связей
