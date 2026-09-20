from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column
from pgvector.sqlalchemy import Vector

from .base import Base


class DocumentEmbedding(Base):
    __tablename__ = "document_embeddings"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    document_type: Mapped[str] = mapped_column(
        String(20)
    )

    document_id: Mapped[int] = mapped_column(
        Integer
    )

    embedding = mapped_column(
        Vector(384)
    )