"""
Chat/RAG endpoints.

Handles RAG-based question answering with vector search and LLM generation.
"""

from fastapi import APIRouter, Depends, status
from typing import Dict, Any, List

from utils.logger import setup_logging

logger = setup_logging(__name__)

router = APIRouter()


# TODO: Implement chat endpoints
# - POST /query - Ask a question (RAG)
# - GET /sessions/{session_id} - Get conversation history (Phase 1+)
# - POST /sessions - Create new conversation session (Phase 1+)
# - POST /messages/{message_id}/rate - Rate response quality (Phase 2)
