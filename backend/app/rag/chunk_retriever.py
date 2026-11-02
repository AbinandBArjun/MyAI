import numpy as np

from sqlalchemy.orm import Session
from sentence_transformers import util

from app.models.document_chunk import DocumentChunk
from app.models.note import Note
from app.models.article import Article
from app.rag.embeddings import get_embedding


CHUNK_TOP_K = 10
CHUNK_SIMILARITY_THRESHOLD = 0.25


def _get_document(
    db: Session,
    document_type: str,
    document_id: int,
):
    """
    Resolve a chunk's parent document.
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


def retrieve_relevant_chunks(
    query: str,
    db: Session,
    document_type: str | None = None,
    top_k: int = CHUNK_TOP_K,
    similarity_threshold: float = CHUNK_SIMILARITY_THRESHOLD,
):
    """
    Retrieve relevant document chunks using cosine similarity.

    Returns chunks with parent document metadata.
    Does not modify the existing whole-document retriever.
    """

    if not query or not query.strip():
        return []

    if document_type is not None and document_type not in {
        "NOTE",
        "ARTICLE",
    }:
        raise ValueError(
            "document_type must be NOTE or ARTICLE"
        )

    if top_k <= 0:
        return []

    query_embedding = get_embedding(query)

    chunk_query = db.query(DocumentChunk)

    if document_type is not None:
        chunk_query = chunk_query.filter(
            DocumentChunk.document_type == document_type
        )

    stored_chunks = chunk_query.all()

    candidates = []

    for chunk in stored_chunks:

        if chunk.embedding is None:
            continue

        chunk_embedding = np.asarray(
            chunk.embedding,
            dtype=np.float32,
        )

        score = util.cos_sim(
            query_embedding,
            chunk_embedding,
        ).item()

        document = _get_document(
            db=db,
            document_type=chunk.document_type,
            document_id=chunk.document_id,
        )

        # Ignore orphaned chunks.
        if document is None:
            continue

        candidates.append(
            {
                "type": chunk.document_type,
                "id": document.id,
                "title": document.title,
                "chunk_id": chunk.id,
                "chunk_index": chunk.chunk_index,
                "content": chunk.content,
                "score": float(score),
            }
        )

    candidates.sort(
        key=lambda item: item["score"],
        reverse=True,
    )

    relevant_chunks = [
        candidate
        for candidate in candidates
        if candidate["score"] >= similarity_threshold
    ][:top_k]

    print("\nTop retrieved chunks:")

    for chunk in relevant_chunks:
        print(
            f"{chunk['type']}: "
            f"{chunk['title']} | "
            f"Chunk {chunk['chunk_index']} | "
            f"Score={chunk['score']:.3f}"
        )

    return relevant_chunks


def group_chunks_by_document(
    chunks: list[dict],
):
    """
    Group retrieved chunks by their parent document.

    Each parent document appears only once.
    Chunks are ordered by their original chunk index.
    """

    grouped = {}

    for chunk in chunks:

        key = (
            chunk["type"],
            chunk["id"],
        )

        if key not in grouped:
            grouped[key] = {
                "type": chunk["type"],
                "id": chunk["id"],
                "title": chunk["title"],
                "content": [],
                "score": chunk["score"],
                "chunks": [],
            }

        grouped[key]["chunks"].append(
            {
                "chunk_id": chunk["chunk_id"],
                "chunk_index": chunk["chunk_index"],
                "content": chunk["content"],
                "score": chunk["score"],
            }
        )

        grouped[key]["score"] = max(
            grouped[key]["score"],
            chunk["score"],
        )

    documents = []

    for document in grouped.values():

        document["chunks"].sort(
            key=lambda item: item["chunk_index"]
        )

        document["content"] = "\n\n".join(
            chunk["content"]
            for chunk in document["chunks"]
        )

        documents.append(document)

    documents.sort(
        key=lambda item: item["score"],
        reverse=True,
    )

    return documents

