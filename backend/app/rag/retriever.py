from sqlalchemy.orm import Session

from app.models.note import Note
from app.models.article import Article
import re

def retrieve_context(
    query: str,
    db: Session
):
    notes = db.query(Note).all()
    articles = db.query(Article).all()

    context = []

    stop_words = {
        "what",
        "when",
        "where",
        "which",
        "about",
        "have",
        "does",
        "your",
        "tell",
        "notes",
        "article",
        "articles"
    }

    keywords = [
        word
        for word in re.findall(
            r"\w+",
            query.lower()
        )
        if len(word) > 3
        and word not in stop_words
    ]

    print("Keywords:", keywords)    
    # Search Notes
    for note in notes:
        text = (
            note.title + " " + note.content
        ).lower()

        if any(
            keyword in text
            for keyword in keywords
        ):
            context.append(
                f"NOTE: {note.title}\n{note.content}"
            )

    # Search Articles
    for article in articles:
        text = (
            article.title + " " + article.summary
        ).lower()

        if any(
            keyword in text
            for keyword in keywords
        ):
            context.append(
                f"ARTICLE: {article.title}\n{article.summary}"
            )

    # Fallback
    if not context:
        for note in notes[:3]:
            context.append(
                f"NOTE: {note.title}\n{note.content}"
            )

        for article in articles[:2]:
            context.append(
                f"ARTICLE: {article.title}\n{article.summary}"
            )

    print(f"Retrieved {len(context)} context items")

    return "\n\n".join(context)