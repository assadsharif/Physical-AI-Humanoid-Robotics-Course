# Skill: Qdrant Vector Search Integration

**Description**: Implementing semantic search using Qdrant Cloud for RAG applications.

**Scope**:
- Vector database connection and management
- Embedding generation and storage
- Semantic similarity search
- Filtering and reranking
- Collection management
- Batch operations

**Key Technologies**:
- Qdrant Cloud
- Python Qdrant client
- OpenAI Embeddings (text-embedding-3-small)
- Vector distance metrics (cosine similarity)

**Vector Operations**:
- **Index**: Create embeddings from chapter text chunks
- **Search**: Find semantically similar content
- **Filter**: Restrict search by chapter_id, module_id, language
- **Rerank**: Sort results by relevance score

**Collection Schema**:
```python
{
  "name": "textbook-content",
  "vectors": {
    "size": 1536,  # OpenAI embedding dimension
    "distance": "Cosine"
  },
  "payload": {
    "chapter_id": "uuid",
    "chunk_text": "str",
    "language": "enum",
    "module": "str",
    "embedding_model": "str"
  }
}
```

**Embedding Strategy**:
- Chunk size: 300-500 tokens per chunk
- Overlap: 50 tokens between chunks
- Model: text-embedding-3-small (1536 dimensions)
- Batch size: 100 chunks per request

**Search Query Example**:
```python
results = qdrant_client.search(
    collection_name="textbook-content",
    query_vector=query_embedding,
    limit=5,
    query_filter=Filter(
        must=[
            FieldCondition(key="language", match={"value": "EN"}),
            FieldCondition(key="module", match={"value": "ros2"})
        ]
    ),
    score_threshold=0.7
)
```

**Performance Targets**:
- Search latency < 100ms (p95)
- Index throughput > 1000 vectors/sec
- Support millions of vectors

**Cost Optimization**:
- Batch indexing operations
- Reuse embeddings (don't regenerate)
- Archive old vectors when not needed

**Owner**: RAG Chatbot Agent

**Related**: rag-chatbot-agent.md, fastapi-backend.md
