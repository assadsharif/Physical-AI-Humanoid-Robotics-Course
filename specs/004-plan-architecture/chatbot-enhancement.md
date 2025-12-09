# Chatbot Enhancement: Conversation Context & Intelligence

**Version**: 1.0.0
**Created**: 2025-12-09
**Status**: Phase 1+ Enhancement Design
**Impact**: +4-6 hours to Phase 1, +10 hours Phase 2

---

## Overview

Enhance the RAG chatbot to support multi-turn conversations with context awareness. This transforms the chatbot from stateless Q&A to an intelligent conversational assistant.

---

## Current State vs Enhanced State

### **Current (Phase 1 MVP)**
```
User: "What is a ROS 2 topic?"
Chatbot: [searches embeddings, returns answer, no context]

User: "Explain simpler"
Chatbot: [treats as new query, doesn't understand follow-up]
```

### **Enhanced (Post-Phase 1)**
```
User: "What is a ROS 2 topic?"
Chatbot: [remembers: user on Chapter 2.1, difficulty=beginner]
         → Searches embeddings with context
         → Returns answer in beginner-friendly tone
         → Suggests: "Next: Publishers & Subscribers"

User: "Explain simpler"
Chatbot: [context: previous query was "ROS 2 topic", user=beginner]
         → Knows what "it" refers to
         → Rewrites explanation with simpler language
         → Adds code example if helpful
```

---

## Architecture

### **New Database Tables**

#### 1. `ConversationSession`
```sql
CREATE TABLE conversation_sessions (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id),
    created_at TIMESTAMP NOT NULL,
    last_message_at TIMESTAMP NOT NULL,
    context_chapter_id UUID REFERENCES chapters(id),
    context_module_slug VARCHAR(100),
    user_difficulty_level VARCHAR(50),  -- "beginner", "intermediate", "advanced"
    session_metadata JSONB,  -- {recent_topics: [...], preferences: {...}}
    is_active BOOLEAN DEFAULT TRUE,
    closed_at TIMESTAMP,

    UNIQUE(user_id, is_active)  -- Only 1 active session per user
);
```

#### 2. `ConversationMessage` (enhanced)
```sql
-- Extends existing ChatMessage table with context

ALTER TABLE chat_messages ADD COLUMN (
    conversation_session_id UUID REFERENCES conversation_sessions(id),
    parent_message_id UUID REFERENCES chat_messages(id),  -- For follow-ups
    intent VARCHAR(100),  -- "explain_concept", "show_code", "help_debug"
    context_chapter_id UUID REFERENCES chapters(id),
    context_module_slug VARCHAR(100),
    user_difficulty_level VARCHAR(50),

    -- Conversation metrics
    clarification_depth INT DEFAULT 0,  -- 0=first msg, 1=follow-up, 2=deeper
    sentiment_score FLOAT,  -- User satisfaction indicator
    was_follow_up BOOLEAN DEFAULT FALSE
);
```

#### 3. `ConversationContext` (new)
```sql
CREATE TABLE conversation_context (
    id UUID PRIMARY KEY,
    session_id UUID NOT NULL REFERENCES conversation_sessions(id),

    -- Current chapter/module context
    chapter_id UUID REFERENCES chapters(id),
    module_slug VARCHAR(100),

    -- Topics discussed
    topics JSONB,  -- ["ROS 2 topics", "publishers", "subscribers"]

    -- User state
    difficulty_level VARCHAR(50),
    expertise_score INT DEFAULT 0,  -- Inferred from interactions

    -- Recent messages (window)
    message_window INT DEFAULT 5,  -- Keep last 5 messages

    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
);
```

---

## API Changes

### **Existing Endpoint: POST /api/chat/query**

**Enhanced Request**:
```json
{
  "query": "Explain simpler",
  "mode": "global",
  "chapter_id": "550e8400-e29b-41d4-a716-446655440001",
  "conversation_session_id": "session-xyz",
  "parent_message_id": "msg-123",
  "intent": "clarification",
  "user_difficulty": "beginner"
}
```

**New Features**:
- `conversation_session_id`: Maintains context across messages
- `parent_message_id`: Links follow-up questions to original query
- `intent`: Helps chatbot understand what user really wants
- `user_difficulty`: Adapts explanation complexity

**Enhanced Response**:
```json
{
  "message_id": "msg-456",
  "response": "A ROS 2 topic is like a message channel...",
  "sources": [...],
  "conversation_context": {
    "session_id": "session-xyz",
    "topics": ["ROS 2 topics", "publishers", "subscribers"],
    "next_suggestions": ["Want to see code example?", "Learn about publishers?"]
  },
  "follow_up_options": [
    "Show me code example",
    "Explain publish-subscribe pattern",
    "How is this used in practice?"
  ]
}
```

### **New Endpoint: GET /api/chat/sessions/{session_id}**

Get conversation history with context.

**Response**:
```json
{
  "session_id": "session-xyz",
  "user_id": "user-123",
  "created_at": "2025-12-09T10:00:00Z",
  "current_chapter": {
    "id": "ch-001",
    "title": "ROS 2 Basics",
    "module": "ros2"
  },
  "conversation_history": [
    {
      "message_id": "msg-1",
      "query": "What is a ROS 2 topic?",
      "response": "...",
      "intent": "learn_concept"
    },
    {
      "message_id": "msg-2",
      "query": "Explain simpler",
      "response": "...",
      "intent": "clarification",
      "parent_message_id": "msg-1"
    }
  ],
  "topics_discussed": ["ROS 2 topics", "publishers", "subscribers"],
  "session_insights": {
    "total_messages": 5,
    "difficulty_level": "beginner",
    "engagement_score": 0.85
  }
}
```

### **New Endpoint: POST /api/chat/sessions**

Create new conversation session.

**Request**:
```json
{
  "chapter_id": "ch-001",
  "initial_intent": "learn_chapter"
}
```

**Response**:
```json
{
  "session_id": "session-xyz",
  "created_at": "2025-12-09T10:00:00Z",
  "chapter": {...},
  "context": {...}
}
```

---

## Chatbot Intelligence Enhancement

### **Phase 1: Basic Context** (+4-6 hours)

**What's new**:
- Store conversation history (last 5 messages)
- Include chapter/module in system prompt
- Track user difficulty level

**System Prompt Enhancement**:
```
You are a helpful tutor for the Physical AI & Humanoid Robotics course.

CONTEXT:
- Student is currently on: Chapter 2.1 (ROS 2 Basics)
- Module: ros2
- Difficulty level: beginner
- Recent topics discussed: [ROS 2 topics, publishers]
- This is message #2 in conversation (follow-up to: "What is a ROS 2 topic?")

INSTRUCTIONS:
- Adapt explanations to student's level (beginner = simple, no jargon)
- If this is a follow-up, build on previous context
- Always provide code examples (student's level = beginner)
- Suggest next steps based on learning path
- If student seems stuck, ask clarifying questions
```

**Implementation**:
```python
# In ChatService

async def answer_query(query: str, session_id: str, parent_msg_id: str):
    # Get conversation context
    context = await get_conversation_context(session_id)

    # Get last 5 messages for context
    history = await get_message_history(session_id, limit=5)

    # Build system prompt with context
    system_prompt = build_context_aware_prompt(
        chapter=context.chapter,
        difficulty=context.difficulty_level,
        history=history,
        topics=context.topics
    )

    # Generate response with context
    response = await llm_service.chat(
        system_prompt=system_prompt,
        user_message=query,
        temperature=0.7
    )

    # Store with context
    await store_message(
        query=query,
        response=response,
        session_id=session_id,
        parent_message_id=parent_msg_id,
        context=context
    )

    return response
```

### **Phase 2: Intelligent Follow-ups** (+8-10 hours)

**What's new**:
- Detect intent (explain, code example, help debug, etc.)
- Track topics discussed
- Suggest relevant next steps
- Learn from user feedback (ratings)

**Intent Detection**:
```python
INTENTS = {
    "explain": "User wants more explanation",
    "code_example": "User wants code",
    "debug": "User needs help debugging",
    "clarify": "User asking for simpler explanation",
    "extend": "User wants more advanced info",
    "compare": "User wants to compare concepts",
    "practice": "User wants exercises"
}

# Classifier (could use simple keyword matching or LLM)
def detect_intent(query: str, context: ConversationContext) -> str:
    keywords = {
        "explain": ["explain", "what", "how", "why"],
        "code_example": ["code", "example", "show", "write"],
        "debug": ["error", "bug", "not working", "problem"],
        "clarify": ["simpler", "easier", "again", "understand"],
        "extend": ["more", "advanced", "deeper"],
    }

    # Returns highest probability intent
    return detect_from_keywords(query, keywords)
```

**Follow-up Suggestions**:
```python
async def get_follow_up_suggestions(
    message_id: str,
    intent: str,
    topics: List[str],
    difficulty: str
) -> List[str]:
    """Suggest 3-4 follow-up directions based on context"""

    suggestions = {
        "explain": [
            "Show me code example",
            "Explain with a diagram",
            "How is this used in practice?",
        ],
        "code_example": [
            "Explain this code",
            "How do I run this?",
            "What if I want to modify it?",
        ],
        "clarify": [
            "Can you show a diagram?",
            "I want to practice this",
            "Compare with X concept",
        ]
    }

    # Return suggestions relevant to current intent
    return suggestions.get(intent, [])
```

**Feedback Loop (Learning)**:
```python
# Track response quality
async def record_user_rating(message_id: str, rating: int, comment: str = ""):
    """Store user rating to improve future responses"""

    # Update message with rating
    await update_message_rating(message_id, rating, comment)

    # If rating low (1-2), trigger analysis
    if rating <= 2:
        # Analyze what went wrong
        msg = await get_message(message_id)

        # Log for improvement
        await log_poor_response(
            message_id=message_id,
            intent=msg.intent,
            topic=msg.context.topics[-1],
            difficulty=msg.difficulty_level,
            reason=comment
        )

        # Could trigger prompt refinement in Phase 3
```

### **Phase 3: Personalization** (+6-8 hours - optional)

**What's new**:
- Infer user's expertise level
- Adapt response style to learning preferences
- Suggest personalized learning path
- Remember past topics for better suggestions

**User Profile Updates**:
```python
async def update_user_profile(user_id: str, session_insights: dict):
    """Update inferred user expertise based on interactions"""

    # Infer difficulty level from quiz scores
    avg_score = calculate_avg_quiz_score(user_id)
    if avg_score >= 90:
        difficulty = "advanced"
    elif avg_score >= 80:
        difficulty = "intermediate"
    else:
        difficulty = "beginner"

    # Track learning velocity
    chapters_per_week = calculate_completion_rate(user_id)

    # Update user profile
    await update_profile(user_id, {
        "inferred_difficulty": difficulty,
        "learning_velocity": chapters_per_week,
        "preferred_explanation_style": infer_style(user_id),
        "successful_topics": extract_successful_topics(user_id),
    })
```

---

## Implementation Timeline

### **Phase 1** (2-3 weeks, +4-6 hours)
- [ ] Add `conversation_sessions` table
- [ ] Enhance `chat_messages` with context fields
- [ ] Implement context-aware system prompt
- [ ] Store/retrieve conversation history
- [ ] Test multi-turn conversations

**Deliverable**: Chatbot remembers conversation context, provides follow-ups

### **Phase 2** (3-4 weeks, +8-10 hours)
- [ ] Implement intent detection
- [ ] Add follow-up suggestion generation
- [ ] Implement feedback loop / rating system
- [ ] Add session analytics
- [ ] Test with real users

**Deliverable**: Intelligent chatbot with follow-up suggestions

### **Phase 3** (optional, +6-8 hours)
- [ ] Implement user expertise inference
- [ ] Personalized learning path suggestions
- [ ] Response style adaptation
- [ ] Topic-based learning recommendations

**Deliverable**: Fully personalized learning experience

---

## Database Migration

```sql
-- Phase 1 additions

CREATE TABLE conversation_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    last_message_at TIMESTAMP NOT NULL DEFAULT NOW(),
    context_chapter_id UUID REFERENCES chapters(id),
    context_module_slug VARCHAR(100),
    user_difficulty_level VARCHAR(50),
    session_metadata JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT TRUE,
    closed_at TIMESTAMP,

    UNIQUE(user_id, is_active),
    INDEX idx_user_active (user_id, is_active),
    INDEX idx_last_message (last_message_at)
);

ALTER TABLE chat_messages ADD COLUMN (
    conversation_session_id UUID REFERENCES conversation_sessions(id) ON DELETE CASCADE,
    parent_message_id UUID REFERENCES chat_messages(id),
    intent VARCHAR(100),
    context_chapter_id UUID REFERENCES chapters(id),
    context_module_slug VARCHAR(100),
    user_difficulty_level VARCHAR(50),
    clarification_depth INT DEFAULT 0,
    sentiment_score FLOAT,
    was_follow_up BOOLEAN DEFAULT FALSE
);

CREATE INDEX idx_chat_session ON chat_messages(conversation_session_id);
CREATE INDEX idx_chat_parent ON chat_messages(parent_message_id);
```

---

## Testing & Validation

### **Phase 1 Tests**

```python
# Test context preservation
async def test_conversation_context():
    # Create session
    session = await create_session(user_id, chapter_id)

    # First message
    response1 = await chat_service.answer(
        query="What is a topic?",
        session_id=session.id
    )
    assert response1.sources  # Has sources

    # Second message (follow-up)
    response2 = await chat_service.answer(
        query="Explain simpler",
        session_id=session.id,
        parent_message_id=response1.message_id
    )
    assert response2.was_follow_up == True
    assert response2.context.chapter_id == chapter_id

    # Verify history
    history = await chat_service.get_history(session.id)
    assert len(history) == 2
    assert history[1].parent_message_id == history[0].message_id
```

### **Phase 2 Tests**

```python
# Test intent detection
def test_intent_detection():
    assert detect_intent("What is a topic?") == "explain"
    assert detect_intent("Show me code") == "code_example"
    assert detect_intent("This doesn't work") == "debug"
    assert detect_intent("Explain simpler") == "clarify"

# Test follow-up suggestions
async def test_follow_up_suggestions():
    suggestions = await get_follow_up_suggestions(
        intent="explain",
        difficulty="beginner"
    )
    assert len(suggestions) >= 3
    assert any("code" in s.lower() for s in suggestions)
```

---

## Success Criteria

- ✅ Multi-turn conversations work (user can ask follow-ups)
- ✅ Context preserved across messages (chatbot remembers chapter/topic)
- ✅ Chapter context included in responses (adaptive to student's location)
- ✅ Difficulty level affects explanation (beginner gets simpler text)
- ✅ Follow-up suggestions help guide learning
- ✅ User ratings tracked for improvement
- ✅ Conversation history retrievable
- ✅ Performance: conversation lookup < 100ms

---

## User Experience

### **Before Enhancement**
```
User: What is a topic?
Bot: A topic is a named bus...

User: Explain simpler
Bot: A topic is a named communication channel...
```

### **After Enhancement**
```
User: What is a topic?
Bot: A topic is like a message channel in ROS 2. Think of it as a newspaper:
     - Publishers "write" to a topic (like journalists)
     - Subscribers "read" from a topic (like readers)
     → See code example? Learn about publishers?

User: Explain simpler
Bot: Great question! Here's an even simpler way to think about it:
     - Topic = Message Channel
     - Publisher = Sender
     - Subscriber = Receiver
     Example: Robot broadcasts "I'm moving!" on /status topic

     Code: [shows simple example]

     → Want to see a full example? Try an exercise?
```

---

**Status**: Ready for Phase 1+ implementation
**Next**: Begin Phase 1 implementation with basic context support, extend in Phase 2

