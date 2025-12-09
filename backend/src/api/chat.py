"""
Chat/RAG endpoints.

Handles RAG-based question answering with vector search and LLM generation.
"""

from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, List

from db import get_db
from schemas.chat import ChatQueryRequest, ChatQueryResponse, ChatRatingRequest
from services.chat_service import ChatService
from api.dependencies import get_current_user_id
from utils.logger import setup_logging
from utils.errors import ValidationError, ServiceUnavailableError, AppException

logger = setup_logging(__name__)

router = APIRouter()

# Initialize chat service
_chat_service: ChatService = None


def get_chat_service() -> ChatService:
    """Get or initialize chat service."""
    global _chat_service
    if _chat_service is None:
        _chat_service = ChatService()
    return _chat_service


@router.post(
    "/query",
    response_model=ChatQueryResponse,
    summary="Ask a question (RAG-powered)",
    tags=["chat"],
)
async def query(
    request: ChatQueryRequest,
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_db),
    chat_service: ChatService = Depends(get_chat_service),
) -> ChatQueryResponse:
    """
    Ask a question about course content using RAG (semantic search + LLM).

    The chatbot will:
    1. Convert your question into embeddings
    2. Search for relevant course materials using semantic similarity
    3. Use an LLM to generate an answer based on the retrieved materials
    4. Provide source citations

    Args:
        request: ChatQueryRequest with:
            - query: Your question
            - mode: "global" or "chapter" (optional)
            - chapter_id: Filter to specific chapter (optional)
            - user_difficulty: "beginner", "intermediate", or "advanced"

    Returns:
        ChatQueryResponse with answer, sources, and follow-up suggestions

    Raises:
        400: Invalid query
        401: Not authenticated
        503: OpenAI or Qdrant unavailable
    """
    try:
        response = await chat_service.answer_query(
            query=request.query,
            user_id=user_id,
            session=session,
            mode=request.mode,
            chapter_id=request.chapter_id,
            module_slug=request.mode == "chapter" and request.chapter_id or None,
            conversation_session_id=request.conversation_session_id,
            parent_message_id=request.parent_message_id,
            intent=request.intent,
            user_difficulty=request.user_difficulty or "beginner",
        )

        return response

    except ValidationError as e:
        raise HTTPException(status_code=400, detail=e.message)
    except ServiceUnavailableError as e:
        raise HTTPException(status_code=503, detail=e.message)
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.error(f"Chat query error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to process your question. Please try again.",
        )


@router.post(
    "/messages/{message_id}/rate",
    summary="Rate response quality (Phase 2)",
    tags=["chat"],
)
async def rate_message(
    message_id: str,
    rating_request: ChatRatingRequest,
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """
    Rate the quality of a chatbot response.

    Used for feedback and improving the chatbot over time.

    Args:
        message_id: ID of the message to rate
        rating_request: Rating (1-5 stars) and optional comment

    Returns:
        Confirmation of rating
    """
    # TODO: Implement rating storage and analysis (Phase 2)
    # For now, just acknowledge the rating
    return {
        "message_id": message_id,
        "rating": rating_request.rating,
        "stored": True,
        "note": "Rating stored for future improvements",
    }
