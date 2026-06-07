from app.database.database import SessionLocal
from app.models.article import Article
from app.ingestion.techcrunch import fetch_articles


def save_articles():
    db = SessionLocal()

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
        count += 1

    db.commit()
    db.close()

    print(f"Saved {count} new articles")


if __name__ == "__main__":
    save_articles()