from app.database.database import SessionLocal
from app.models.article import Article
from app.ingestion.techcrunch import fetch_articles
from app.services.embedding_service import save_embedding


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

            # Generate the article ID before creating its embedding
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

            count += 1

        db.commit()

        print(f"Saved {count} new articles")

    finally:
        db.close()


if __name__ == "__main__":
    save_articles()