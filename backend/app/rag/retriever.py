from sqlalchemy.orm import Session

from app.models.note import Note
from app.models.article import Article


def retrieve_context(
    query: str,
    db: Session
):
    notes = db.query(Note).all()
    articles = db.query(Article).all()

    context = []

    for note in notes:
        context.append(
            f"NOTE: {note.title}\n{note.content}"
        )

    for article in articles[:2]:
        context.append(
            f"ARTICLE: {article.title}\n{article.summary}"
        )

    return "\n\n".join(context)