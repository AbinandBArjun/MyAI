from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Literal, Optional

from app.services.chat_service import ask_llm
from app.rag.retriever import (
    _retrieve_documents,
    _get_document,
)
from app.database.database import SessionLocal


router = APIRouter()


class ChatContext(BaseModel):
    type: Literal["NOTE", "ARTICLE"]
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
        # retrieve only that document.
        #
        # Otherwise, perform normal semantic RAG retrieval
        # across the knowledge base.
        # ---------------------------------------------------------

        if request.context:

            document = _get_document(
                db=db,
                document_type=request.context.type,
                document_id=request.context.id,
            )

            if document is None:
                raise HTTPException(
                    status_code=404,
                    detail=(
                        f"{request.context.type} "
                        f"with id {request.context.id} "
                        f"was not found."
                    ),
                )

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

            # -----------------------------------------------------
            # GLOBAL RAG
            # -----------------------------------------------------

            documents = _retrieve_documents(
                request.message,
                db,
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
            # Context-specific retrieval does not need one.
            if "score" in document:
                source["score"] = document["score"]

            sources.append(source)

        # ---------------------------------------------------------
        # GENERATE ANSWER
        # ---------------------------------------------------------

        response = ask_llm(
            request.message,
            context,
        )

        return {
            "response": response,
            "sources": sources,
        }

    finally:
        db.close()