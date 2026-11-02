from app.database.database import SessionLocal
from app.models.note import Note
from app.models.article import Article
from app.models.document_embedding import DocumentEmbedding
from app.models.document_chunk import DocumentChunk

from app.services.embedding_service import save_embedding
from app.services.chunk_indexing_service import index_document_chunks


def embedding_exists(
    db,
    document_type: str,
    document_id: int
):
    return (
        db.query(DocumentEmbedding)
        .filter(
            DocumentEmbedding.document_type == document_type,
            DocumentEmbedding.document_id == document_id
        )
        .first()
        is not None
    )


def chunks_exist(
    db,
    document_type: str,
    document_id: int
):
    return (
        db.query(DocumentChunk)
        .filter(
            DocumentChunk.document_type == document_type,
            DocumentChunk.document_id == document_id
        )
        .first()
        is not None
    )


def backfill_embeddings():
    db = SessionLocal()

    notes_embeddings_added = 0
    articles_embeddings_added = 0
    notes_chunks_added = 0
    articles_chunks_added = 0

    try:
        notes = db.query(Note).all()

        for note in notes:
            text = f"{note.title}\n{note.content}"

            if not embedding_exists(db, "NOTE", note.id):
                save_embedding(
                    db=db,
                    document_type="NOTE",
                    document_id=note.id,
                    text=text
                )
                notes_embeddings_added += 1

            if not chunks_exist(db, "NOTE", note.id):
                count = index_document_chunks(
                    db=db,
                    document_type="NOTE",
                    document_id=note.id,
                    title=note.title,
                    content=note.content
                )
                notes_chunks_added += count

        articles = db.query(Article).all()

        for article in articles:
            text = f"{article.title}\n{article.summary}"

            if not embedding_exists(db, "ARTICLE", article.id):
                save_embedding(
                    db=db,
                    document_type="ARTICLE",
                    document_id=article.id,
                    text=text
                )
                articles_embeddings_added += 1

            if not chunks_exist(db, "ARTICLE", article.id):
                count = index_document_chunks(
                    db=db,
                    document_type="ARTICLE",
                    document_id=article.id,
                    title=article.title,
                    content=article.summary
                )
                articles_chunks_added += count

        db.commit()

        print(f"Backfilled note embeddings: {notes_embeddings_added}")
        print(f"Backfilled article embeddings: {articles_embeddings_added}")
        print(f"Backfilled note chunks: {notes_chunks_added}")
        print(f"Backfilled article chunks: {articles_chunks_added}")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    backfill_embeddings()
