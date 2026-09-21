import re

from sqlalchemy.orm import Session
from sentence_transformers import util
import numpy as np

from app.models.document_embedding import DocumentEmbedding
from app.models.note import Note
from app.models.article import Article
from app.rag.embeddings import get_embedding


TOP_K = 5
SIMILARITY_THRESHOLD = 0.25


def format_documents(documents, document_type: str):
    """
    Convert database documents into LLM-readable context.
    """

    context = []

    for document in documents:
        if document_type == "NOTE":
            title = document.title
            content = document.content
        else:
            title = document.title
            content = document.summary

        context.append(
            f"{document_type}: {title}\n"
            f"{content}"
        )

    return "\n\n".join(context)


def detect_listing_intent(query: str):
    """
    Detect simple listing-style queries that should not depend
    exclusively on semantic similarity.
    """

    normalized_query = query.lower().strip()

    note_patterns = [
        r"\bwhat notes do i have\b",
        r"\blist my notes\b",
        r"\bshow my notes\b",
        r"\bshow me my notes\b",
        r"\bmy saved notes\b",
        r"\bwhat are my notes\b",
    ]

    article_patterns = [
        r"\bwhat articles do i have\b",
        r"\blist my articles\b",
        r"\bshow my articles\b",
        r"\bshow me my articles\b",
        r"\bmy saved articles\b",
        r"\bwhat are my articles\b",
    ]

    if any(
        re.search(pattern, normalized_query)
        for pattern in note_patterns
    ):
        return "NOTE"

    if any(
        re.search(pattern, normalized_query)
        for pattern in article_patterns
    ):
        return "ARTICLE"

    return None


def retrieve_context(
    query: str,
    db: Session
):
    """
    Retrieve relevant notes and articles using stored embeddings.

    Listing queries are handled directly from the database.
    Other queries use cosine similarity over stored embeddings.
    """

    # ---------------------------------------------------------
    # 1. Handle direct listing queries
    # ---------------------------------------------------------

    listing_type = detect_listing_intent(query)

    if listing_type == "NOTE":
        notes = (
            db.query(Note)
            .order_by(Note.id.desc())
            .limit(20)
            .all()
        )

        print(
            f"Listing query detected: returning "
            f"{len(notes)} notes"
        )

        if not notes:
            return ""

        return format_documents(notes, "NOTE")

    if listing_type == "ARTICLE":
        articles = (
            db.query(Article)
            .order_by(Article.id.desc())
            .limit(20)
            .all()
        )

        print(
            f"Listing query detected: returning "
            f"{len(articles)} articles"
        )

        if not articles:
            return ""

        return format_documents(articles, "ARTICLE")

    # ---------------------------------------------------------
    # 2. Perform semantic retrieval for normal queries
    # ---------------------------------------------------------

    query_embedding = get_embedding(query)

    stored_embeddings = (
        db.query(DocumentEmbedding)
        .all()
    )

    candidates = []

    for stored_embedding in stored_embeddings:

        if stored_embedding.embedding is None:
            continue

        document_embedding = np.array(
            stored_embedding.embedding,
            dtype=np.float32
        )

        score = util.cos_sim(
            query_embedding,
            document_embedding
        ).item()

        document = None

        # Retrieve the original document
        if stored_embedding.document_type == "NOTE":

            document = (
                db.query(Note)
                .filter(
                    Note.id == stored_embedding.document_id
                )
                .first()
            )

        elif stored_embedding.document_type == "ARTICLE":

            document = (
                db.query(Article)
                .filter(
                    Article.id == stored_embedding.document_id
                )
                .first()
            )

        # Skip embeddings whose original document no longer exists
        if document is None:
            continue

        if stored_embedding.document_type == "NOTE":
            title = document.title
            content = document.content
        else:
            title = document.title
            content = document.summary

        candidates.append(
            {
                "type": stored_embedding.document_type,
                "title": title,
                "content": content,
                "score": score,
            }
        )

    # Sort candidates by similarity
    candidates.sort(
        key=lambda item: item["score"],
        reverse=True
    )

    print("\nTop retrieved candidates:")

    for item in candidates[:10]:
        print(
            f"{item['type']}: "
            f"{item['title']} "
            f"(score={item['score']:.3f})"
        )

    # Keep candidates above the relaxed threshold
    relevant = [
        item
        for item in candidates
        if item["score"] >= SIMILARITY_THRESHOLD
    ][:TOP_K]

    print(
        f"Retrieved {len(relevant)} relevant items"
    )

    for item in relevant:
        print(
            f"Selected: "
            f"{item['type']}: "
            f"{item['title']} "
            f"(score={item['score']:.3f})"
        )

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