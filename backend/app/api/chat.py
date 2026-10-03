from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional

from app.services.chat_service import ask_llm
from app.rag.retriever import (
    _retrieve_documents,
    _get_document,
)
from app.database.database import SessionLocal


router = APIRouter()


class ChatContext(BaseModel):
    type: str
    id: int


class ChatRequest(BaseModel):
    message: str
    context: Optional[ChatContext] = None


@router.post("/")
def chat(request: ChatRequest):

    db = SessionLocal()

    try:
        # ---------------------------------------------------------
        # CONTEXT-AWARE RETRIEVAL
        # ---------------------------------------------------------
        #
        # If the frontend provides a specific Note or Article,
        # retrieve that document directly.
        #
        # Otherwise, perform normal semantic RAG retrieval.
        # ---------------------------------------------------------

        if request.context:

            document = _get_document(
                db=db,
                document_type=request.context.type,
                document_id=request.context.id,
            )

            if document is not None:

                if request.context.type == "NOTE":
                    content = document.content
                else:
                    content = document.summary

                documents = [
                    {
                        "type": request.context.type,
                        "id": document.id,
                        "title": document.title,
                        "content": content,
                    }
                ]

            else:
                # If the requested context no longer exists,
                # fall back to normal RAG retrieval.
                documents = _retrieve_documents(
                    request.message,
                    db
                )

        else:
            # -----------------------------------------------------
            # NORMAL GLOBAL RAG
            # -----------------------------------------------------

            documents = _retrieve_documents(
                request.message,
                db
            )

        # ---------------------------------------------------------
        # BUILD LLM CONTEXT
        # ---------------------------------------------------------

        context_parts = []

        for document in documents:
            context_parts.append(
                f"{document['type']}: "
                f"{document['title']}\n"
                f"{document['content']}"
            )

        context = "\n\n".join(context_parts)

        # ---------------------------------------------------------
        # BUILD SOURCE METADATA
        # ---------------------------------------------------------

        sources = []

        for document in documents:

            source = {
                "type": document["type"],
                "id": document["id"],
                "title": document["title"],
            }

            # Semantic retrieval provides similarity scores.
            if "score" in document:
                source["score"] = document["score"]

            sources.append(source)

        # ---------------------------------------------------------
        # GENERATE ANSWER
        # ---------------------------------------------------------

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