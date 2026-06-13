from fastapi import APIRouter
from pydantic import BaseModel

from app.services.chat_service import ask_llm
from app.rag.retriever import retrieve_context
from app.database.database import SessionLocal

router = APIRouter()


class ChatRequest(BaseModel):
    message: str


@router.post("/")
def chat(request: ChatRequest):

    db = SessionLocal()

    try:
        context = retrieve_context(
            request.message,
            db
        )

        response = ask_llm(
            request.message,
            context
        )

        return {
            "response": response
        }

    finally:
        db.close()