from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class Article(Base):
    __tablename__ = "articles"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    title: Mapped[str] = mapped_column(
        String(500)
    )

    summary: Mapped[str] = mapped_column(
        Text()
    )

    source: Mapped[str] = mapped_column(
        String(200)
    )

    url: Mapped[str] = mapped_column(
        String(1000),
        unique=True
    )