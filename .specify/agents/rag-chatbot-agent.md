# RAG Chatbot Agent

**Purpose**: Develop and maintain the Retrieval-Augmented Generation (RAG) chatbot backend and integration.

**Responsibilities**:
- FastAPI backend development for chatbot endpoints
- Qdrant vector database integration for semantic search
- Neon Postgres database management for metadata and chat history
- LLM integration with OpenAI API
- Chatbot UI component development

**Technologies**:
- FastAPI (Python async web framework)
- Qdrant Cloud (vector database)
- Neon Postgres (relational database)
- OpenAI API (LLM completions)
- Pydantic (data validation)

**Key Endpoints**:
- `POST /api/chat/query` - Global question answering
- `POST /api/chat/highlight` - Context-aware highlight-to-answer
- `POST /api/chat/chapter-specific` - Chapter-scoped Q&A
- `GET /api/embeddings` - Vector search results

**Database Schema**:
- `users` - User profiles and authentication
- `chapters` - Textbook chapter metadata
- `embeddings` - Vector embeddings for semantic search (synced with Qdrant)
- `chat_history` - User conversation logs
- `translations` - Multi-language content

**Quality Metrics**:
- Response time < 3 seconds (p95)
- Accuracy > 90% (user satisfaction)
- Uptime > 95%
- Support 100 concurrent users

**Owner**: Claude Code Agent (to be assigned)

**Status**: In Planning
