from sqlalchemy.orm import Session
from sentence_transformers import util

from app.models.note import Note
from app.models.article import Article
from app.rag.embeddings import get_embedding


TOP_K = 5
SIMILARITY_THRESHOLD = 0.40


def retrieve_context(
    query: str,
    db: Session
):
    notes = db.query(Note).all()
    articles = db.query(Article).all()

    query_embedding = get_embedding(query)

    candidates = []

    # Embed Notes
    for note in notes:
        text = f"{note.title}\n{note.content}"

        embedding = get_embedding(text)

        score = util.cos_sim(
            query_embedding,
            embedding
        ).item()

        candidates.append(
            {
                "type": "NOTE",
                "title": note.title,
                "content": note.content,
                "score": score
            }
        )

    # Embed Articles
    for article in articles:
        text = f"{article.title}\n{article.summary}"

        embedding = get_embedding(text)

        score = util.cos_sim(
            query_embedding,
            embedding
        ).item()

        candidates.append(
            {
                "type": "ARTICLE",
                "title": article.title,
                "content": article.summary,
                "score": score
            }
        )

    # Highest similarity first
    candidates.sort(
        key=lambda item: item["score"],
        reverse=True
    )

    # Keep only sufficiently relevant results
    relevant = [
        item
        for item in candidates
        if item["score"] >= SIMILARITY_THRESHOLD
    ][:TOP_K]

    print(f"Retrieved {len(relevant)} relevant items")

    for item in relevant:
        print(
            f"{item['type']}: "
            f"{item['title']} "
            f"(score={item['score']:.3f})"
        )

    # No sufficiently relevant information
    if not relevant:
        return ""

    context = []

    for item in relevant:
        context.append(
            f"{item['type']}: "
            f"{item['title']}\n"
            f"{item['content']}"
        )

    return "\n\n".join(context)