"""
RAG (Retrieval-Augmented Generation) chatbot service.

Combines semantic search with LLM to answer questions about course content.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from db.models import ChatMessage, Chapter
from schemas.chat import ChatQueryResponse, ChatSourceResponse, ConversationContextResponse
from services.vector_store import get_vector_store
from services.embedding_service import get_embedding_service, get_llm_service
from utils.logger import setup_logging
from utils.errors import ServiceUnavailableError, ValidationError

logger = setup_logging(__name__)


class ChatService:
    """RAG-based chatbot service."""

    def __init__(self):
        """Initialize chat service with dependencies."""
        self.vector_store = get_vector_store()
        self.embedding_service = get_embedding_service()
        self.llm_service = get_llm_service()

    async def answer_query(
        self,
        query: str,
        user_id: str,
        session: AsyncSession,
        mode: str = "global",
        chapter_id: Optional[str] = None,
        module_slug: Optional[str] = None,
        conversation_session_id: Optional[str] = None,
        parent_message_id: Optional[str] = None,
        intent: Optional[str] = None,
        user_difficulty: Optional[str] = "beginner",
    ) -> ChatQueryResponse:
        """
        Answer a user query using RAG (semantic search + LLM).

        Args:
            query: User's question
            user_id: Authenticated user ID
            session: Database session
            mode: "global" or "chapter" search mode
            chapter_id: Filter to specific chapter if mode="chapter"
            module_slug: Filter to specific module
            conversation_session_id: For Phase 1+ conversation tracking
            parent_message_id: For Phase 1+ follow-up tracking
            intent: User intent (explain, code_example, debug, etc.)
            user_difficulty: User's learning level (beginner, intermediate, advanced)

        Returns:
            ChatQueryResponse with answer, sources, and follow-up suggestions

        Raises:
            ValidationError: If query is invalid
            ServiceUnavailableError: If OpenAI/Qdrant unavailable
        """
        # Validate input
        if not query or len(query.strip()) == 0:
            raise ValidationError("Query cannot be empty")

        if len(query) > 5000:
            raise ValidationError("Query is too long (max 5000 characters)")

        logger.info(f"Processing query from user {user_id}: {query[:100]}...")

        try:
            # Step 1: Generate embedding for the query
            query_embedding = await self.embedding_service.embed_text(query)
            if not query_embedding:
                raise ServiceUnavailableError("OpenAI", "Failed to generate embedding")

            # Step 2: Semantic search in vector store
            search_filter = module_slug if mode == "chapter" else None
            search_results = await self.vector_store.search(
                query_vector=query_embedding,
                limit=5,
                min_score=0.6,
                module_slug=search_filter,
            )

            if not search_results:
                logger.warning(f"No search results found for query: {query}")
                # Return helpful response when no results found
                response_text = (
                    "I couldn't find specific course materials related to your question. "
                    "Could you try a different search term or visit the course materials directly? "
                    "If you're stuck, consider checking the prerequisites or earlier chapters."
                )
            else:
                # Step 3: Build context from search results
                context_texts = [result["content"] for result in search_results]
                chapter_references = [
                    result.get("chapter_id") for result in search_results
                ]

                # Step 4: Generate system prompt based on difficulty level
                system_prompt = self._build_system_prompt(
                    difficulty_level=user_difficulty,
                    module_slug=module_slug,
                    chapter_id=chapter_id,
                )

                # Step 5: Generate response using LLM with context
                response_text = await self.llm_service.generate_response_with_context(
                    system_prompt=system_prompt,
                    user_message=query,
                    context_texts=context_texts,
                    temperature=0.7,
                    max_tokens=1000,
                )

                if not response_text:
                    raise ServiceUnavailableError("OpenAI", "Failed to generate response")

            # Step 6: Fetch chapter details for sources
            sources = await self._fetch_sources(search_results, session)

            # Step 7: Generate follow-up suggestions
            follow_ups = self._generate_follow_ups(intent, user_difficulty)

            # Step 8: Store message in database
            message_id = str(uuid.uuid4())
            await self._store_message(
                message_id=message_id,
                query=query,
                response=response_text,
                user_id=user_id,
                session=session,
                session_id=conversation_session_id,
                parent_id=parent_message_id,
                intent=intent,
                chapter_id=chapter_id,
                module_slug=module_slug,
                difficulty=user_difficulty,
                sources=sources,
            )

            logger.info(f"✅ Generated response for query (msg_id: {message_id})")

            # Build response
            return ChatQueryResponse(
                message_id=message_id,
                response=response_text,
                sources=sources,
                conversation_context=ConversationContextResponse(
                    session_id=conversation_session_id,
                    topics=[s.chapter_title for s in sources] if sources else [],
                    next_suggestions=follow_ups,
                ),
                follow_up_options=follow_ups,
                created_at=datetime.utcnow(),
            )

        except (ValidationError, ServiceUnavailableError):
            raise
        except Exception as e:
            logger.error(f"❌ Chat service error: {e}")
            raise ServiceUnavailableError("Chat Service", str(e))

    def _build_system_prompt(
        self,
        difficulty_level: str = "beginner",
        module_slug: Optional[str] = None,
        chapter_id: Optional[str] = None,
    ) -> str:
        """
        Build system prompt for the LLM based on user context.

        Args:
            difficulty_level: User's learning level
            module_slug: Current module context
            chapter_id: Current chapter context

        Returns:
            System prompt string
        """
        difficulty_desc = {
            "beginner": "simple explanations without technical jargon",
            "intermediate": "moderate technical depth with practical examples",
            "advanced": "detailed technical explanations with advanced concepts",
        }.get(difficulty_level, "clear explanations")

        context_info = f"Module: {module_slug}" if module_slug else "Course"

        return f"""You are a helpful tutor for the Physical AI & Humanoid Robotics Course.

Context:
- Student learning level: {difficulty_level}
- Current context: {context_info}
- Explanation style: {difficulty_desc}

Instructions:
- Provide clear, accurate answers based on course materials
- If a follow-up clarification might help, offer it
- Use code examples when appropriate for the learning level
- Suggest related topics that might be helpful
- Be encouraging and supportive

When answering:
1. Start with a direct answer to the question
2. Provide context and explanation as needed
3. Include code examples if relevant
4. End with suggestions for what to learn next"""

    def _generate_follow_ups(
        self, intent: Optional[str] = None, difficulty: str = "beginner"
    ) -> List[str]:
        """
        Generate relevant follow-up question suggestions.

        Args:
            intent: User's stated intent (explain, code_example, etc.)
            difficulty: User's difficulty level

        Returns:
            List of follow-up suggestions
        """
        base_suggestions = {
            "explain": [
                "Can you provide a code example?",
                "How is this used in practice?",
                "What are common mistakes with this?",
            ],
            "code_example": [
                "Can you explain this code line by line?",
                "How would I modify this example?",
                "Are there alternative approaches?",
            ],
            "debug": [
                "What's the most common cause of this error?",
                "How can I prevent this issue?",
                "Are there debugging tools that help?",
            ],
            "clarify": [
                "Can you use an analogy?",
                "Do you have a simpler example?",
                "What are the key points to remember?",
            ],
        }

        suggestions = base_suggestions.get(intent, base_suggestions["explain"])

        # Customize for difficulty level
        if difficulty == "beginner":
            suggestions = [
                s.replace("line by line", "in simple terms") for s in suggestions
            ]
        elif difficulty == "advanced":
            suggestions.append("What are the underlying theoretical concepts?")

        return suggestions[:4]  # Return top 4

    async def _fetch_sources(
        self, search_results: List[Dict[str, Any]], session: AsyncSession
    ) -> List[ChatSourceResponse]:
        """
        Fetch chapter details for search results to create source citations.

        Args:
            search_results: Results from vector search
            session: Database session

        Returns:
            List of formatted source responses
        """
        sources = []

        for result in search_results[:5]:  # Top 5 sources
            chapter_id = result.get("chapter_id")
            if chapter_id:
                # Fetch chapter details
                stmt = select(Chapter).where(Chapter.id == chapter_id)
                db_result = await session.execute(stmt)
                chapter = db_result.scalar_one_or_none()

                if chapter:
                    sources.append(
                        ChatSourceResponse(
                            chapter_id=chapter_id,
                            chapter_title=chapter.title,
                            module_slug=result.get("module_slug", "unknown"),
                            excerpt=result["content"][:200],  # First 200 chars
                            relevance_score=result.get("score", 0.0),
                        )
                    )

        return sources

    async def _store_message(
        self,
        message_id: str,
        query: str,
        response: str,
        user_id: str,
        session: AsyncSession,
        session_id: Optional[str] = None,
        parent_id: Optional[str] = None,
        intent: Optional[str] = None,
        chapter_id: Optional[str] = None,
        module_slug: Optional[str] = None,
        difficulty: Optional[str] = None,
        sources: Optional[List[ChatSourceResponse]] = None,
    ) -> ChatMessage:
        """
        Store chat message in database for history and analytics.

        Args:
            message_id: Message identifier
            query: User's question
            response: Generated answer
            user_id: User who sent the query
            session: Database session
            session_id: Conversation session ID (Phase 1+)
            parent_id: Parent message ID for follow-ups (Phase 1+)
            intent: User intent
            chapter_id: Chapter context
            module_slug: Module context
            difficulty: User difficulty level
            sources: Source citations

        Returns:
            Stored ChatMessage object
        """
        # Format sources as JSON string
        sources_json = None
        if sources:
            sources_json = str(
                [
                    {
                        "chapter_id": s.chapter_id,
                        "title": s.chapter_title,
                        "module": s.module_slug,
                    }
                    for s in sources
                ]
            )

        message = ChatMessage(
            id=message_id,
            user_id=user_id,
            query=query,
            response=response,
            conversation_session_id=session_id,
            parent_message_id=parent_id,
            intent=intent,
            context_chapter_id=chapter_id,
            context_module_slug=module_slug,
            user_difficulty_level=difficulty,
            was_follow_up=bool(parent_id),
            sources=sources_json,
        )

        session.add(message)
        await session.commit()

        return message
