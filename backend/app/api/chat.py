from fastapi import APIRouter
from pydantic import BaseModel

from app.services.chat_service import ask_llm

router = APIRouter()


class ChatRequest(BaseModel):
    message: str


@router.post("/")
def chat(request: ChatRequest):
    response = ask_llm(request.message)

    return {
        "response": response
    }