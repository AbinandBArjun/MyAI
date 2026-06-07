import feedparser


RSS_URL = "https://techcrunch.com/feed/"


def fetch_articles():
    feed = feedparser.parse(RSS_URL)

    articles = []

    for entry in feed.entries[:20]:
        articles.append(
            {
                "title": entry.title,
                "summary": entry.summary,
                "source": "TechCrunch",
                "url": entry.link,
            }
        )

    return articles