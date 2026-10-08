from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Literal, Optional, List

from app.services.chat_service import ask_llm
from app.rag.retriever import (
    _retrieve_documents,
    _get_document,
    detect_listing_intent,
)
from app.database.database import SessionLocal


router = APIRouter()


class ChatContext(BaseModel):
    type: Literal["NOTE", "ARTICLE"]
    id: int


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class ChatRequest(BaseModel):
    message: str
    context: Optional[ChatContext] = None
    history: List[ChatMessage] = Field(default_factory=list)


def is_follow_up_question(
    current_question: str,
) -> bool:
    """
    Detect simple conversational follow-up questions.
    """

    normalized = current_question.lower().strip()

    words = normalized.split()

    follow_up_phrases = [
        "why is it",
        "why is this",
        "why are they",
        "why are these",
        "how does it",
        "how does this",
        "how is it",
        "how is this",
        "what about it",
        "what about this",
        "what about that",
        "tell me more",
        "explain more",
        "can you explain more",
        "why does it",
        "why does this",
        "how is that",
        "what does it",
        "what does this",
    ]

    if any(
        phrase in normalized
        for phrase in follow_up_phrases
    ):
        return True

    reference_words = {
        "it",
        "this",
        "that",
        "they",
        "these",
        "those",
    }

    if len(words) <= 8 and any(
        word in reference_words
        for word in words
    ):
        return True

    return False


def build_retrieval_query(
    current_question: str,
    history: List[dict],
) -> str:
    """
    Build a retrieval query without polluting semantic
    retrieval with unrelated older conversation.
    """

    if not history:
        return current_question

    if not is_follow_up_question(
        current_question
    ):
        return current_question

    previous_user_messages = [
        message["content"]
        for message in history
        if message["role"] == "user"
    ]

    if not previous_user_messages:
        return current_question

    previous_question = previous_user_messages[-1]

    return (
        f"{previous_question} "
        f"{current_question}"
    )


def build_listing_response(
    listing_type: str,
    documents: list,
) -> str:
    """
    Build a deterministic response for listing queries.

    Listing questions do not need LLM generation because the
    database already contains the exact documents being requested.
    """

    if not documents:
        if listing_type == "NOTE":
            return "You do not have any notes."
        else:
            return "You do not have any articles."

    if listing_type == "NOTE":
        label = "notes"
    else:
        label = "articles"

    lines = [
        f"You have {len(documents)} {label}:"
    ]

    for document in documents:
        lines.append(
            f"• {document['title']}"
        )

    return "\n".join(lines)


@router.post("/")
def chat(request: ChatRequest):

    db = SessionLocal()

    try:
        # ---------------------------------------------------------
        # BUILD CONVERSATION HISTORY
        # ---------------------------------------------------------

        history = [
            {
                "role": message.role,
                "content": message.content,
            }
            for message in request.history[-6:]
        ]

        # ---------------------------------------------------------
        # DETECT LISTING INTENT
        # ---------------------------------------------------------

        listing_type = None

        if not request.context:
            listing_type = detect_listing_intent(
                request.message
            )

        # ---------------------------------------------------------
        # CONTEXT-AWARE RETRIEVAL
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

            retrieval_mode = "CONTEXT"

        else:

            # -----------------------------------------------------
            # GLOBAL RAG
            # -----------------------------------------------------

            if listing_type:

                # Listing queries must remain isolated from
                # conversation history.
                retrieval_query = request.message

            else:

                retrieval_query = build_retrieval_query(
                    current_question=request.message,
                    history=history,
                )

            print(
                "\n========== RETRIEVAL QUERY =========="
            )
            print(retrieval_query)

            documents = _retrieve_documents(
                retrieval_query,
                db,
            )

            if listing_type:
                retrieval_mode = "LISTING"
            else:
                retrieval_mode = "SEMANTIC"

        # ---------------------------------------------------------
        # BUILD SOURCE METADATA
        # ---------------------------------------------------------

        sources = []

        for document in documents:

            source = {
                "type": document["type"],
                "id": document["id"],
                "title": document["title"],
                "mode": retrieval_mode,
            }

            if "score" in document:
                source["score"] = document["score"]

            sources.append(source)

        # ---------------------------------------------------------
        # HANDLE LISTING QUERIES DIRECTLY
        # ---------------------------------------------------------
        #
        # No LLM is needed for a database listing.
        # This guarantees that the requested documents are listed
        # exactly as they exist in the knowledge base.
        # ---------------------------------------------------------

        if listing_type:

            response = build_listing_response(
                listing_type=listing_type,
                documents=documents,
            )

            return {
                "response": response,
                "sources": sources,
            }

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
        # GENERATE ANSWER
        # ---------------------------------------------------------

        response = ask_llm(
            query=request.message,
            context=context,
            history=history,
            listing_type=None,
        )

        return {
            "response": response,
            "sources": sources,
        }

    finally:
        db.close()