from sqlalchemy.orm import Session
from sentence_transformers import util
import numpy as np

from app.models.document_embedding import DocumentEmbedding
from app.models.note import Note
from app.models.article import Article
from app.rag.embeddings import get_embedding


TOP_K = 5
SIMILARITY_THRESHOLD = 0.50


def retrieve_context(
    query: str,
    db: Session
):
    """
    Retrieve relevant notes and articles using
    embeddings stored in PostgreSQL.
    """

    # Generate an embedding only for the user's query
    query_embedding = get_embedding(query)

    stored_embeddings = (
        db.query(DocumentEmbedding)
        .all()
    )

    candidates = []

    for stored_embedding in stored_embeddings:

        if stored_embedding.embedding is None:
            continue

        # Convert the PostgreSQL vector into a NumPy array
        document_embedding = np.array(
            stored_embedding.embedding,
            dtype=np.float32
        )

        # Calculate cosine similarity
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

        # Extract title and content
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
                "score": score
            }
        )

    # Sort all candidates from highest to lowest similarity
    candidates.sort(
        key=lambda item: item["score"],
        reverse=True
    )

    # Debugging: display the top 10 candidates
    print("\nTop retrieved candidates:")

    for item in candidates[:10]:
        print(
            f"{item['type']}: "
            f"{item['title']} "
            f"(score={item['score']:.3f})"
        )

    # Keep only candidates above the similarity threshold
    relevant = [
        item
        for item in candidates
        if item["score"] >= SIMILARITY_THRESHOLD
    ][:TOP_K]

    print(
        f"Retrieved {len(relevant)} relevant items"
    )

    # Display the final selected documents
    for item in relevant:
        print(
            f"Selected: "
            f"{item['type']}: "
            f"{item['title']} "
            f"(score={item['score']:.3f})"
        )

    # Return an empty context if nothing relevant was found
    if not relevant:
        return ""

    # Build the context passed to the LLM
    context = []

    for item in relevant:
        context.append(
            f"{item['type']}: "
            f"{item['title']}\n"
            f"{item['content']}"
        )

    return "\n\n".join(context)