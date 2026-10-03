from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, Literal

from app.services.chat_service import ask_llm
from app.rag.retriever import _retrieve_documents
from app.database.database import SessionLocal
from app.models.note import Note
from app.models.article import Article


router = APIRouter()


class ChatContext(BaseModel):
    type: Literal["NOTE", "ARTICLE"]
    id: int


class ChatRequest(BaseModel):
    message: str
    context: Optional[ChatContext] = None


def get_context_document(
    context: ChatContext,
    db
):
    if context.type == "NOTE":
        return (
            db.query(Note)
            .filter(Note.id == context.id)
            .first()
        )

    if context.type == "ARTICLE":
        return (
            db.query(Article)
            .filter(Article.id == context.id)
            .first()
        )

    return None


@router.post("/")
def chat(request: ChatRequest):

    db = SessionLocal()

    try:

        # --------------------------------------------------
        # CONTEXT-AWARE RETRIEVAL
        # --------------------------------------------------

        if request.context:

            document = get_context_document(
                request.context,
                db
            )

            if not document:
                return {
                    "response": (
                        "I couldn't find the document "
                        "you're currently viewing."
                    ),
                    "sources": [],
                }

            if request.context.type == "NOTE":
                content = document.content
            else:
                content = document.summary

            context = (
                f"{request.context.type}: "
                f"{document.title}\n"
                f"{content}"
            )

            sources = [
                {
                    "type": request.context.type,
                    "id": document.id,
                    "title": document.title,
                }
            ]

        # --------------------------------------------------
        # NORMAL RAG RETRIEVAL
        # --------------------------------------------------

        else:

            documents = _retrieve_documents(
                request.message,
                db
            )

            context_parts = []

            for document in documents:
                context_parts.append(
                    f"{document['type']}: "
                    f"{document['title']}\n"
                    f"{document['content']}"
                )

            context = "\n\n".join(context_parts)

            sources = []

            for document in documents:

                source = {
                    "type": document["type"],
                    "id": document["id"],
                    "title": document["title"],
                }

                if "score" in document:
                    source["score"] = document["score"]

                sources.append(source)

        # --------------------------------------------------
        # GENERATE RESPONSE
        # --------------------------------------------------

        response = ask_llm(
            request.message,
            context
        )

        return {
            "response": response,
            "sources": sources,
        }

    finally:
        db.close()