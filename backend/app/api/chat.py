from fastapi import APIRouter
from pydantic import BaseModel

from app.services.chat_service import ask_llm
from app.rag.retriever import _retrieve_documents
from app.database.database import SessionLocal


router = APIRouter()


class ChatRequest(BaseModel):
    message: str


@router.post("/")
def chat(request: ChatRequest):

    db = SessionLocal()

    try:
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