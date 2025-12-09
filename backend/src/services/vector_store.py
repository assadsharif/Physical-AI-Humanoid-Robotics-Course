"""
Qdrant vector store integration for semantic search.

Handles embedding storage, retrieval, and similarity search.
"""

from typing import List, Optional, Dict, Any
from qdrant_client import QdrantClient
from qdrant_client.http import models
import asyncio
from concurrent.futures import ThreadPoolExecutor

from config import settings
from utils.logger import setup_logging

logger = setup_logging(__name__)


class VectorStore:
    """Qdrant vector store for semantic search over course content."""

    def __init__(self):
        """Initialize Qdrant client."""
        self.client = QdrantClient(
            url=settings.QDRANT_URL,
            api_key=settings.QDRANT_API_KEY,
        )
        self.collection_name = settings.QDRANT_COLLECTION_NAME
        self.executor = ThreadPoolExecutor(max_workers=4)

    def create_collection(
        self, vector_size: int = 1536, force: bool = False
    ) -> bool:
        """
        Create Qdrant collection for embeddings.

        Args:
            vector_size: Size of embedding vectors (1536 for text-embedding-3-small)
            force: Delete existing collection if it exists

        Returns:
            True if created or already exists
        """
        try:
            # Check if collection exists
            try:
                self.client.get_collection(self.collection_name)
                if force:
                    self.client.delete_collection(self.collection_name)
                    logger.info(f"Deleted existing collection: {self.collection_name}")
                else:
                    logger.info(f"Collection already exists: {self.collection_name}")
                    return True
            except Exception:
                pass  # Collection doesn't exist

            # Create collection
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(
                    size=vector_size,
                    distance=models.Distance.COSINE,
                ),
            )

            logger.info(f"✅ Created collection: {self.collection_name}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to create collection: {e}")
            return False

    async def add_embedding(
        self,
        embedding_id: str,
        vector: List[float],
        content: str,
        chapter_id: str,
        module_slug: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Add an embedding to the vector store.

        Args:
            embedding_id: Unique identifier for the embedding
            vector: Embedding vector (list of floats)
            content: Original text content
            chapter_id: Associated chapter ID
            module_slug: Associated module slug
            metadata: Additional metadata

        Returns:
            True if successful
        """
        try:
            if metadata is None:
                metadata = {}

            # Prepare payload with metadata
            payload = {
                "content": content,
                "chapter_id": chapter_id,
                "module_slug": module_slug,
                **metadata,
            }

            # Add point to collection
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                self.executor,
                lambda: self.client.upsert(
                    collection_name=self.collection_name,
                    points=[
                        models.PointStruct(
                            id=int(embedding_id.replace("-", "")[:15]) % (2**63 - 1),
                            vector=vector,
                            payload=payload,
                        )
                    ],
                ),
            )

            return True

        except Exception as e:
            logger.error(f"❌ Failed to add embedding: {e}")
            return False

    async def search(
        self,
        query_vector: List[float],
        limit: int = 5,
        min_score: float = 0.6,
        module_slug: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Semantic search for similar embeddings.

        Args:
            query_vector: Query embedding vector
            limit: Number of results to return
            min_score: Minimum similarity score (0-1)
            module_slug: Filter by module (optional)

        Returns:
            List of matching results with scores
        """
        try:
            # Build query filter if module_slug provided
            query_filter = None
            if module_slug:
                query_filter = models.Filter(
                    must=[
                        models.HasIdCondition(
                            has_id=[
                                models.FieldCondition(
                                    key="module_slug",
                                    match=models.MatchValue(value=module_slug),
                                )
                            ]
                        )
                    ]
                )

            # Execute search
            loop = asyncio.get_event_loop()
            results = await loop.run_in_executor(
                self.executor,
                lambda: self.client.search(
                    collection_name=self.collection_name,
                    query_vector=query_vector,
                    limit=limit,
                    query_filter=query_filter,
                ),
            )

            # Format results
            matches = []
            for result in results:
                if result.score >= min_score:
                    matches.append(
                        {
                            "score": result.score,
                            "content": result.payload.get("content", ""),
                            "chapter_id": result.payload.get("chapter_id"),
                            "module_slug": result.payload.get("module_slug"),
                            "metadata": {
                                k: v
                                for k, v in result.payload.items()
                                if k not in ["content", "chapter_id", "module_slug"]
                            },
                        }
                    )

            return matches

        except Exception as e:
            logger.error(f"❌ Search failed: {e}")
            return []

    async def bulk_add_embeddings(
        self,
        embeddings: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Add multiple embeddings to vector store.

        Args:
            embeddings: List of embedding dicts with:
                - id: unique identifier
                - vector: embedding vector
                - content: original text
                - chapter_id: chapter reference
                - module_slug: module reference
                - metadata: optional additional data

        Returns:
            Dict with success count and failures
        """
        success_count = 0
        failures = []

        try:
            points = []
            for emb in embeddings:
                try:
                    # Create numeric ID from string (Qdrant requires integers)
                    numeric_id = int(emb["id"].replace("-", "")[:15]) % (2**63 - 1)

                    payload = {
                        "content": emb["content"],
                        "chapter_id": emb["chapter_id"],
                        "module_slug": emb["module_slug"],
                        **(emb.get("metadata") or {}),
                    }

                    points.append(
                        models.PointStruct(
                            id=numeric_id,
                            vector=emb["vector"],
                            payload=payload,
                        )
                    )
                except Exception as e:
                    failures.append({"id": emb.get("id"), "error": str(e)})

            # Batch upload
            if points:
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(
                    self.executor,
                    lambda: self.client.upsert(
                        collection_name=self.collection_name,
                        points=points,
                    ),
                )
                success_count = len(points)

            logger.info(
                f"✅ Added {success_count} embeddings to Qdrant. Failures: {len(failures)}"
            )

            return {
                "success": success_count,
                "failures": failures,
                "total": len(embeddings),
            }

        except Exception as e:
            logger.error(f"❌ Bulk embedding failed: {e}")
            return {
                "success": 0,
                "failures": [{"error": str(e)}],
                "total": len(embeddings),
            }

    async def delete_collection(self) -> bool:
        """Delete the entire collection (be careful!)."""
        try:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                self.executor,
                lambda: self.client.delete_collection(self.collection_name),
            )
            logger.warning(f"🗑️  Deleted collection: {self.collection_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete collection: {e}")
            return False


# Global vector store instance
_vector_store: Optional[VectorStore] = None


def get_vector_store() -> VectorStore:
    """Get or initialize the global vector store instance."""
    global _vector_store
    if _vector_store is None:
        _vector_store = VectorStore()
    return _vector_store
