from sqlalchemy.orm import Session

from app.models.document_chunk import DocumentChunk
from app.services.chunking_service import (
    split_into_chunks,
    build_embedding_text,
)
from app.rag.embeddings import get_embedding


def index_document_chunks(
    db: Session,
    document_type: str,
    document_id: int,
    title: str,
    content: str,
) -> int:
    """
    Generate and store chunks and embeddings for a document.

    Existing chunks for the document are replaced.

    This function does not commit. The caller owns the
    database transaction.
    """

    if document_type not in {"NOTE", "ARTICLE"}:
        raise ValueError(
            "document_type must be NOTE or ARTICLE"
        )

    chunks = split_into_chunks(
        text=content,
        title=title,
    )

    # Generate embeddings before modifying existing chunks.
    chunk_records = []

    for chunk_index, chunk_content in enumerate(chunks):

        embedding_text = build_embedding_text(
            title=title,
            chunk_content=chunk_content,
        )

        embedding = get_embedding(
            embedding_text
        )

        chunk_records.append(
            DocumentChunk(
                document_type=document_type,
                document_id=document_id,
                chunk_index=chunk_index,
                content=chunk_content,
                embedding=embedding.tolist(),
            )
        )

    # Replace existing chunks only after generation succeeds.
    (
        db.query(DocumentChunk)
        .filter(
            DocumentChunk.document_type == document_type,
            DocumentChunk.document_id == document_id,
        )
        .delete(synchronize_session=False)
    )

    db.add_all(chunk_records)

    return len(chunk_records)


def delete_document_chunks(
    db: Session,
    document_type: str,
    document_id: int,
) -> int:
    """
    Delete all chunks associated with a document.

    This function does not commit.
    """

    if document_type not in {"NOTE", "ARTICLE"}:
        raise ValueError(
            "document_type must be NOTE or ARTICLE"
        )

    deleted_count = (
        db.query(DocumentChunk)
        .filter(
            DocumentChunk.document_type == document_type,
            DocumentChunk.document_id == document_id,
        )
        .delete(synchronize_session=False)
    )

    return deleted_count

