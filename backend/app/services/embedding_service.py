from sqlalchemy.orm import Session

from app.models.document_embedding import DocumentEmbedding
from app.rag.embeddings import get_embedding


def save_embedding(
    db: Session,
    document_type: str,
    document_id: int,
    text: str
):
    """
    Create or update the embedding for a document.
    """

    embedding = get_embedding(text)

    embedding_list = embedding.tolist()

    existing = (
        db.query(DocumentEmbedding)
        .filter(
            DocumentEmbedding.document_type == document_type,
            DocumentEmbedding.document_id == document_id
        )
        .first()
    )

    if existing:
        existing.embedding = embedding_list

    else:
        new_embedding = DocumentEmbedding(
            document_type=document_type,
            document_id=document_id,
            embedding=embedding_list
        )

        db.add(new_embedding)

    db.commit()


def delete_embedding(
    db: Session,
    document_type: str,
    document_id: int
):
    """
    Delete the embedding associated with a document.
    """

    existing = (
        db.query(DocumentEmbedding)
        .filter(
            DocumentEmbedding.document_type == document_type,
            DocumentEmbedding.document_id == document_id
        )
        .first()
    )

    if existing:
        db.delete(existing)
        db.commit()