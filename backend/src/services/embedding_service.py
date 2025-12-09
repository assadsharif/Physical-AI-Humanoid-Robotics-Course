"""
OpenAI embedding and LLM generation service.

Handles generating embeddings and LLM responses for the RAG system.
"""

from typing import List, Optional
import openai
from openai import AsyncOpenAI

from config import settings
from utils.logger import setup_logging
from utils.errors import ServiceUnavailableError

logger = setup_logging(__name__)


class EmbeddingService:
    """Generate embeddings using OpenAI API."""

    def __init__(self):
        """Initialize OpenAI client."""
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_EMBEDDING_MODEL  # text-embedding-3-small

    async def embed_text(self, text: str) -> Optional[List[float]]:
        """
        Generate embedding for a text string.

        Args:
            text: Text to embed

        Returns:
            Embedding vector (list of floats) or None if failed
        """
        try:
            response = await self.client.embeddings.create(
                input=text,
                model=self.model,
            )

            # Extract embedding vector
            embedding = response.data[0].embedding
            return embedding

        except openai.RateLimitError:
            logger.error("OpenAI rate limit exceeded")
            raise ServiceUnavailableError("OpenAI", "Rate limit exceeded")
        except openai.APIError as e:
            logger.error(f"OpenAI API error: {e}")
            raise ServiceUnavailableError("OpenAI", str(e))

    async def embed_batch(self, texts: List[str]) -> Optional[List[List[float]]]:
        """
        Generate embeddings for multiple texts.

        Args:
            texts: List of texts to embed

        Returns:
            List of embedding vectors or None if failed
        """
        try:
            if not texts:
                return []

            response = await self.client.embeddings.create(
                input=texts,
                model=self.model,
            )

            # Sort by index to maintain order
            embeddings = [None] * len(texts)
            for item in response.data:
                embeddings[item.index] = item.embedding

            return embeddings

        except openai.RateLimitError:
            logger.error("OpenAI rate limit exceeded")
            raise ServiceUnavailableError("OpenAI", "Rate limit exceeded")
        except openai.APIError as e:
            logger.error(f"OpenAI API error: {e}")
            raise ServiceUnavailableError("OpenAI", str(e))


class LLMService:
    """Generate LLM responses using OpenAI API."""

    def __init__(self):
        """Initialize OpenAI client."""
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL  # gpt-4o

    async def generate_response(
        self,
        system_prompt: str,
        user_message: str,
        temperature: float = 0.7,
        max_tokens: int = 1000,
    ) -> Optional[str]:
        """
        Generate LLM response based on system prompt and user message.

        Args:
            system_prompt: System instructions for the LLM
            user_message: User's question/query
            temperature: Creativity (0-2, default 0.7)
            max_tokens: Maximum response length

        Returns:
            Generated response text or None if failed
        """
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message},
                ],
                temperature=temperature,
                max_tokens=max_tokens,
            )

            # Extract response text
            return response.choices[0].message.content

        except openai.RateLimitError:
            logger.error("OpenAI rate limit exceeded")
            raise ServiceUnavailableError("OpenAI", "Rate limit exceeded")
        except openai.APIError as e:
            logger.error(f"OpenAI API error: {e}")
            raise ServiceUnavailableError("OpenAI", str(e))

    async def generate_response_with_context(
        self,
        system_prompt: str,
        user_message: str,
        context_texts: List[str],
        temperature: float = 0.7,
        max_tokens: int = 1000,
    ) -> Optional[str]:
        """
        Generate response with RAG context included in the prompt.

        Args:
            system_prompt: System instructions
            user_message: User query
            context_texts: List of relevant context texts from vector search
            temperature: Creativity level
            max_tokens: Max response length

        Returns:
            Generated response with context
        """
        # Format context into the prompt
        context_prompt = "\n\n".join(
            [f"Context {i+1}:\n{text}" for i, text in enumerate(context_texts)]
        )

        enhanced_prompt = f"""{system_prompt}

Here is relevant context from course materials:

{context_prompt}

Please use the above context to answer the user's question."""

        return await self.generate_response(
            system_prompt=enhanced_prompt,
            user_message=user_message,
            temperature=temperature,
            max_tokens=max_tokens,
        )


# Global service instances
_embedding_service: Optional[EmbeddingService] = None
_llm_service: Optional[LLMService] = None


def get_embedding_service() -> EmbeddingService:
    """Get or initialize embedding service."""
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService()
    return _embedding_service


def get_llm_service() -> LLMService:
    """Get or initialize LLM service."""
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service
