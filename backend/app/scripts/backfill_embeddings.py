from app.database.database import SessionLocal
from app.models.note import Note
from app.models.article import Article
from app.models.document_embedding import DocumentEmbedding
from app.services.embedding_service import save_embedding


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


def backfill_embeddings():
    db = SessionLocal()

    notes_added = 0
    articles_added = 0

    try:
        notes = db.query(Note).all()

        for note in notes:
            if embedding_exists(db, "NOTE", note.id):
                continue

            text = f"{note.title}\n{note.content}"

            save_embedding(
                db=db,
                document_type="NOTE",
                document_id=note.id,
                text=text
            )

            notes_added += 1

        articles = db.query(Article).all()

        for article in articles:
            if embedding_exists(db, "ARTICLE", article.id):
                continue

            text = f"{article.title}\n{article.summary}"

            save_embedding(
                db=db,
                document_type="ARTICLE",
                document_id=article.id,
                text=text
            )

            articles_added += 1

        print(f"Backfilled {notes_added} notes")
        print(f"Backfilled {articles_added} articles")

    finally:
        db.close()


if __name__ == "__main__":
    backfill_embeddings()