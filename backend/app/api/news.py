from fastapi import APIRouter
import feedparser

router = APIRouter()

RSS_URL = "https://techcrunch.com/category/artificial-intelligence/feed/"


@router.get("/")
def get_news():
    feed = feedparser.parse(RSS_URL)

    articles = []

    for entry in feed.entries[:10]:
        articles.append(
            {
                "title": entry.title,
                "link": entry.link,
            }
        )

    return articles