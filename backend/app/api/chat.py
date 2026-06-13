from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.services.chat_service import ask_llm
from app.database.database import get_db
from app.rag.retriever import retrieve_context

router = APIRouter()


class ChatRequest(BaseModel):
    message: str


@router.post("/")
def chat(
    request: ChatRequest,
    db: Session = Depends(get_db)
):
    context = retrieve_context(
        request.message,
        db
    )

    prompt = f"""
Context:
{context}

Question:
{request.message}

Answer using the provided context when relevant.
"""

    response = ask_llm(prompt)

    return {
        "response": response
    }