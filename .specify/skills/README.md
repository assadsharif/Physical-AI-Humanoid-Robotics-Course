# Technical Skills Library

This directory contains technical skill definitions used across the Physical AI & Humanoid Robotics Textbook project.

Each skill file defines:
- **Purpose**: What this skill covers
- **Scope**: Breadth of knowledge
- **Key Technologies**: Tools and libraries
- **Code Standards**: Implementation patterns and best practices
- **Performance Targets**: Non-functional requirements
- **Owner**: Which agent(s) use this skill
- **Related**: Links to dependent skills and agents

## Skills by Category

### Backend & Infrastructure

- **FastAPI Backend** - Async Python web services
- **Neon Postgres** - Serverless database management
- **OpenAI LLM Integration** - LLM API usage and prompt engineering

### Search & AI

- **Qdrant Vector Search** - Semantic search and embeddings
- **Whisper Voice Recognition** - Speech-to-text transcription

### Frontend & Content

- **Docusaurus & React** - Static site generation with interactive components

### Robotics

- **ROS 2 Robotics** - Robot Operating System 2 for control and simulation

## Skill Dependencies

```
FastAPI Backend
  ├─ depends on: Neon Postgres (database layer)
  ├─ depends on: OpenAI LLM Integration (AI features)
  └─ depends on: Qdrant Vector Search (search layer)

OpenAI LLM Integration
  ├─ used by: RAG Chatbot Agent
  ├─ used by: Capstone VLA Agent
  └─ requires: Proper prompt engineering and error handling

Whisper Voice Recognition
  ├─ used by: Capstone VLA Agent
  ├─ requires: OpenAI API credentials
  └─ outputs to: OpenAI LLM Integration (for action planning)

ROS 2 Robotics
  ├─ used by: Capstone VLA Agent
  ├─ requires: ROS 2 Humble or Iron installation
  └─ integrates with: Gazebo (simulation), Nav2 (navigation), MoveIt (manipulation)

Docusaurus & React
  ├─ used by: Docusaurus Content Agent
  ├─ embeds: Chatbot Widget (from RAG Chatbot Agent)
  └─ displays: Code examples validated by ROS 2 Robotics skill
```

## Adding New Skills

When adding a new skill:

1. Create `skill-name.md` file
2. Follow the template structure
3. Include:
   - Clear description of scope
   - Code examples and patterns
   - Performance targets
   - Testing strategies
   - Links to related agents/skills
4. Add to this README under appropriate category
5. Commit to feature branch

## Performance Baselines

Use these targets across all skills:

| Metric | Target |
|--------|--------|
| API Response Time (p95) | < 3 seconds |
| Database Query Latency | < 50ms |
| Vector Search Latency | < 100ms |
| Page Load Time | < 2 seconds |
| Code Example Compilation | 100% pass |
| Test Coverage | > 80% |

## Standards Across All Skills

- **Python**: Type hints everywhere, async preferred, Pydantic for validation
- **Error Handling**: Graceful degradation, clear error messages, retry logic
- **Testing**: Unit tests, integration tests, mock external services
- **Documentation**: Docstrings, examples, performance metrics
- **Security**: No secrets in code, environment variables for configs, input validation

---

**Last Updated**: 2025-12-09
**Version**: 1.0.0
**Total Skills**: 7
