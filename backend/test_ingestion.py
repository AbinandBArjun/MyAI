from app.ingestion.techcrunch import fetch_articles

articles = fetch_articles()

print(f"Found {len(articles)} articles")

print(articles[0])