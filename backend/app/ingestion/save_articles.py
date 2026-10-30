from app.database.database import SessionLocal
from app.models.article import Article
from app.ingestion.techcrunch import fetch_articles
from app.services.embedding_service import save_embedding
from app.services.chunk_indexing_service import index_document_chunks


def save_articles():
    db = SessionLocal()

    try:
        articles = fetch_articles()
        count = 0

        for article in articles:
            existing = (
                db.query(Article)
                .filter(Article.url == article["url"])
                .first()
            )

            if existing:
                continue

            new_article = Article(
                title=article["title"],
                summary=article["summary"],
                source=article["source"],
                url=article["url"],
            )

            db.add(new_article)
            db.flush()

            text = (
                f"{new_article.title}\n"
                f"{new_article.summary}"
            )

            save_embedding(
                db=db,
                document_type="ARTICLE",
                document_id=new_article.id,
                text=text
            )

            index_document_chunks(
                db=db,
                document_type="ARTICLE",
                document_id=new_article.id,
                title=new_article.title,
                content=new_article.summary
            )

            count += 1

        db.commit()
        print(f"Saved {count} new articles")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    save_articles()
