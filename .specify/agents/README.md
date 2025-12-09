# Agents & Skills Architecture

This directory contains agent definitions and technical skills for the Physical AI & Humanoid Robotics Textbook project.

## Agents (`.specify/agents/`)

Agents represent logical components/domains with specific responsibilities and teams.

### Active Agents

1. **RAG Chatbot Agent** (`rag-chatbot-agent.md`)
   - Responsible for: FastAPI backend, Qdrant integration, chatbot endpoints
   - Skills: FastAPI Backend, Qdrant Vector Search, OpenAI LLM Integration
   - Status: In Planning

2. **Docusaurus Content Agent** (`docusaurus-content-agent.md`)
   - Responsible for: Docusaurus frontend, content authoring, module structure
   - Skills: Docusaurus & React, Markdown authoring
   - Status: In Planning

3. **Authentication & User Management Agent** (`authentication-agent.md`)
   - Responsible for: User auth, progress tracking, personalization
   - Skills: Neon Postgres, better-auth integration
   - Status: In Planning

4. **Capstone & VLA Agent** (`capstone-vla-agent.md`)
   - Responsible for: Voice-to-action planning, ROS 2 execution, Gazebo simulation
   - Skills: Whisper Voice Recognition, OpenAI LLM Integration, ROS 2 Robotics
   - Status: In Planning

5. **i18n & Translation Agent** (`i18n-translation-agent.md`)
   - Responsible for: Multi-language support, Urdu translations, content versioning
   - Skills: i18next, translation management
   - Status: In Planning

## Skills (`.specify/skills/`)

Skills represent specific technical competencies and implementation patterns.

### Active Skills

1. **FastAPI Backend** (`fastapi-backend.md`)
   - Async Python web services with Pydantic
   - Used by: RAG Chatbot Agent, Authentication Agent

2. **Qdrant Vector Search** (`qdrant-vector-search.md`)
   - Semantic search and vector database management
   - Used by: RAG Chatbot Agent

3. **ROS 2 Robotics** (`ros2-robotics.md`)
   - ROS 2 nodes, actions, URDF, launch files
   - Used by: Capstone & VLA Agent

4. **Docusaurus & React** (`docusaurus-react.md`)
   - Static site generation, MDX, React components
   - Used by: Docusaurus Content Agent

5. **Neon Postgres** (`neon-postgres.md`)
   - Serverless PostgreSQL database management
   - Used by: Authentication Agent, RAG Chatbot Agent

6. **Whisper Voice Recognition** (`whisper-voice-recognition.md`)
   - Speech-to-text transcription via OpenAI Whisper
   - Used by: Capstone & VLA Agent

7. **OpenAI LLM Integration** (`openai-llm-integration.md`)
   - Chat completions, prompt engineering, action planning
   - Used by: RAG Chatbot Agent, Capstone & VLA Agent

## Relationships

```
RAG Chatbot Agent
  ├─ FastAPI Backend
  ├─ Qdrant Vector Search
  ├─ Neon Postgres
  └─ OpenAI LLM Integration

Docusaurus Content Agent
  ├─ Docusaurus & React
  └─ Markdown Authoring

Authentication Agent
  ├─ Neon Postgres
  └─ better-auth

Capstone & VLA Agent
  ├─ Whisper Voice Recognition
  ├─ OpenAI LLM Integration
  ├─ ROS 2 Robotics
  └─ FastAPI Backend (for action execution endpoints)

i18n Translation Agent
  ├─ Neon Postgres
  └─ i18next Framework
```

## Development Workflow

1. **Plan Phase** (`/sp.plan`): Architecture design per agent
2. **Task Generation** (`/sp.tasks`): Break into implementable tasks
3. **Implementation** (`/sp.implement`): Execute tasks with agent ownership
4. **Feature Branches**: All work on feature branches (e.g., `NNN-agent-name`)
5. **Pull Requests**: Each agent's work merged via PR to main

## Next Steps

1. Create detailed architecture plan (`/sp.plan`) for each agent
2. Generate sprint tasks (`/sp.tasks`)
3. Begin implementation with agent ownership assignments
4. Track progress via PHR (Prompt History Records)

---

**Last Updated**: 2025-12-09
**Version**: 1.0.0
