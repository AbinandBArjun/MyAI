from sqlalchemy import String, Integer, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from pgvector.sqlalchemy import Vector

from .base import Base


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    __table_args__ = (
        UniqueConstraint(
            "document_type",
            "document_id",
            "chunk_index",
            name="uq_document_chunks_parent_index"
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    document_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False
    )

    document_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    chunk_index: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    content: Mapped[str] = mapped_column(
        Text(),
        nullable=False
    )

    embedding = mapped_column(
        Vector(384),
        nullable=False
    )

