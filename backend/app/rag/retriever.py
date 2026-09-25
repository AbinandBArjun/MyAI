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


def _get_document(
    db: Session,
    document_type: str,
    document_id: int
):
    """
    Retrieve the original document associated with an embedding.
    """

    if document_type == "NOTE":
        return (
            db.query(Note)
            .filter(Note.id == document_id)
            .first()
        )

    if document_type == "ARTICLE":
        return (
            db.query(Article)
            .filter(Article.id == document_id)
            .first()
        )

    return None


def _semantic_retrieve(
    query: str,
    db: Session
):
    """
    Perform semantic retrieval once and return structured
    candidate documents.

    Each candidate contains:
    - document type
    - document ID
    - title
    - content
    - similarity score
    """

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

        document = _get_document(
            db,
            stored_embedding.document_type,
            stored_embedding.document_id
        )

        # Skip embeddings whose original document no longer exists
        if document is None:
            continue

        if stored_embedding.document_type == "NOTE":
            content = document.content
        else:
            content = document.summary

        candidates.append(
            {
                "type": stored_embedding.document_type,
                "id": document.id,
                "title": document.title,
                "content": content,
                "score": score,
            }
        )

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

    return relevant


def _listing_retrieve(
    listing_type: str,
    db: Session
):
    """
    Retrieve documents for direct listing queries.
    """

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

        return [
            {
                "type": "NOTE",
                "id": note.id,
                "title": note.title,
                "content": note.content,
            }
            for note in notes
        ]

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

        return [
            {
                "type": "ARTICLE",
                "id": article.id,
                "title": article.title,
                "content": article.summary,
            }
            for article in articles
        ]

    return []


def _retrieve_documents(
    query: str,
    db: Session
):
    """
    Perform the complete retrieval operation once.

    Listing queries are handled directly from the database.
    Other queries use semantic retrieval.
    """

    listing_type = detect_listing_intent(query)

    if listing_type:
        return _listing_retrieve(
            listing_type,
            db
        )

    return _semantic_retrieve(
        query,
        db
    )


def retrieve_context(
    query: str,
    db: Session
):
    """
    Retrieve relevant notes and articles and convert them
    into LLM-readable context.
    """

    documents = _retrieve_documents(
        query,
        db
    )

    if not documents:
        return ""

    context = []

    for document in documents:
        context.append(
            f"{document['type']}: "
            f"{document['title']}\n"
            f"{document['content']}"
        )

    return "\n\n".join(context)


def retrieve_sources(
    query: str,
    db: Session
):
    """
    Retrieve structured source metadata.

    This uses the same retrieval operation as retrieve_context()
    and therefore does not perform a second embedding search.
    """

    documents = _retrieve_documents(
        query,
        db
    )

    sources = []

    for document in documents:
        source = {
            "type": document["type"],
            "id": document["id"],
            "title": document["title"],
        }

        # Similarity is available for semantic retrieval.
        if "score" in document:
            source["score"] = document["score"]

        sources.append(source)

    print("\nRetrieved sources:")

    for source in sources:
        if "score" in source:
            print(
                f"{source['type']}: "
                f"{source['title']} "
                f"(score={source['score']:.3f})"
            )
        else:
            print(
                f"{source['type']}: "
                f"{source['title']}"
            )

    return sources