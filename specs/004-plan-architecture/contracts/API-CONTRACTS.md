# Phase 1 Design: API Contracts & Endpoint Specifications

**Branch**: `005-phase1-design` | **Date**: 2025-12-09 | **Format**: OpenAPI 3.0.0-compatible

---

## Overview

This document defines the API contracts for Phase 1 of the Physical AI & Humanoid Robotics Textbook project. All endpoints follow RESTful conventions with async FastAPI implementation. Response times target < 3 seconds (p95) for chat, < 500ms for auth/progress.

**Base URL**: `https://api.textbook.example.com/api` (production)
**Local Dev**: `http://localhost:8000/api`

**Authentication**: Bearer token (JWT via better-auth)

---

## API Groups

1. **Chat API** (`/api/chat`) - RAG chatbot queries
2. **Auth API** (`/api/auth`) - Authentication & user management
3. **Progress API** (`/api/progress`) - User progress tracking
4. **Transcribe API** (`/api/transcribe`) - Voice transcription (Whisper)
5. **VLA Planning API** (`/api/vla`) - Action graph generation
6. **Health API** (`/api/health`) - System status

---

## 1. Chat API (`/api/chat`)

### 1.1 POST /api/chat/query

**Purpose**: Submit a query to RAG chatbot (global, chapter-specific, or highlight mode).

**Request**:
```json
{
  "query": "Explain ROS 2 publishers and subscribers",
  "mode": "global",
  "chapter_id": null,
  "highlighted_text": null
}
```

**Request Schema**:
```typescript
{
  query: string;              // Required. 1-2000 chars. User question.
  mode: "global" | "chapter-specific" | "highlight";  // Required. Query scope.
  chapter_id?: string;        // Optional. UUID. Required if mode="chapter-specific".
  highlighted_text?: string;  // Optional. Required if mode="highlight".
}
```

**Response** (200 OK):
```json
{
  "message_id": "550e8400-e29b-41d4-a716-446655440000",
  "response": "ROS 2 publishers send messages to named topics. Subscribers receive those messages...",
  "sources": [
    {
      "chapter_slug": "ros2-basics",
      "chapter_title": "ROS 2 Basics",
      "section": "Publishers & Subscribers",
      "relevance_score": 0.98
    },
    {
      "chapter_slug": "ros2-basics",
      "chapter_title": "ROS 2 Basics",
      "section": "Quality of Service (QoS)",
      "relevance_score": 0.82
    }
  ],
  "response_time_ms": 1200,
  "model": "gpt-4o"
}
```

**Response Schema**:
```typescript
{
  message_id: string;         // UUID of stored message
  response: string;           // Chatbot answer (1-5000 chars)
  sources: Array<{
    chapter_slug: string;
    chapter_title: string;
    section?: string;
    relevance_score: number;  // 0.0 - 1.0
  }>;
  response_time_ms: number;   // Milliseconds to generate response
  model: string;              // LLM model used (e.g., "gpt-4o")
}
```

**Error Responses**:
- **400 Bad Request**: Invalid mode, missing required fields, or query too long
  ```json
  {
    "error": "INVALID_REQUEST",
    "message": "Field 'mode' must be one of: global, chapter-specific, highlight",
    "code": 400
  }
  ```

- **401 Unauthorized**: Missing or invalid JWT token
  ```json
  {
    "error": "UNAUTHORIZED",
    "message": "Missing or invalid authentication token",
    "code": 401
  }
  ```

- **404 Not Found**: Chapter not found (if chapter_id provided)
  ```json
  {
    "error": "NOT_FOUND",
    "message": "Chapter with ID 550e8400-e29b-41d4-a716-446655440000 not found",
    "code": 404
  }
  ```

- **503 Service Unavailable**: Qdrant or OpenAI down
  ```json
  {
    "error": "SERVICE_UNAVAILABLE",
    "message": "Vector database temporarily unavailable. Please try again later.",
    "code": 503
  }
  ```

**Performance Targets**:
- Response time: < 3 seconds (p95)
- Accuracy: > 90% relevance
- Supports 100 concurrent requests

**Rate Limiting**:
- 30 requests per minute per user
- 1000 requests per minute globally

---

### 1.2 GET /api/chat/history

**Purpose**: Retrieve user's chat message history (paginated).

**Query Parameters**:
```
?limit=20&offset=0&chapter_id=null&mode=all
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| limit | integer | 20 | Max 100 messages per page |
| offset | integer | 0 | Pagination offset |
| chapter_id | UUID (optional) | null | Filter by chapter |
| mode | string | "all" | Filter by mode: "global", "chapter-specific", "highlight", "all" |

**Response** (200 OK):
```json
{
  "total": 145,
  "offset": 0,
  "limit": 20,
  "messages": [
    {
      "message_id": "550e8400-e29b-41d4-a716-446655440000",
      "query": "Explain publishers",
      "response": "...",
      "mode": "global",
      "created_at": "2025-12-09T14:30:00Z",
      "was_helpful": true,
      "user_feedback": 5
    }
  ]
}
```

**Authentication**: Required (Bearer token)

---

### 1.3 POST /api/chat/feedback

**Purpose**: Submit feedback on a chatbot response.

**Request**:
```json
{
  "message_id": "550e8400-e29b-41d4-a716-446655440000",
  "was_helpful": true,
  "rating": 5,
  "comment": "Very clear explanation"
}
```

**Response** (200 OK):
```json
{
  "message_id": "550e8400-e29b-41d4-a716-446655440000",
  "feedback_recorded": true
}
```

**Authentication**: Required

---

## 2. Auth API (`/api/auth`)

### 2.1 POST /api/auth/signup

**Purpose**: Register a new user.

**Request**:
```json
{
  "email": "student@example.com",
  "password": "SecurePass123!",
  "name": "Ahmed Ali"
}
```

**Request Validation**:
- Email: Valid email format, unique
- Password: Minimum 8 characters (strong password recommended in docs)
- Name: 1-255 characters

**Response** (201 Created):
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "student@example.com",
  "name": "Ahmed Ali",
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer",
  "expires_in": 86400
}
```

**Error Responses**:
- **400 Bad Request**: Invalid input (bad email format, password too short)
- **409 Conflict**: Email already exists
  ```json
  {
    "error": "EMAIL_ALREADY_EXISTS",
    "message": "Email student@example.com is already registered",
    "code": 409
  }
  ```

**Performance Target**: < 500ms

---

### 2.2 POST /api/auth/login

**Purpose**: Authenticate user and receive JWT token.

**Request**:
```json
{
  "email": "student@example.com",
  "password": "SecurePass123!"
}
```

**Response** (200 OK):
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer",
  "expires_in": 86400
}
```

**Error Responses**:
- **401 Unauthorized**: Invalid email or password
  ```json
  {
    "error": "INVALID_CREDENTIALS",
    "message": "Invalid email or password",
    "code": 401
  }
  ```

**Performance Target**: < 500ms

---

### 2.3 POST /api/auth/logout

**Purpose**: Invalidate current session.

**Headers**:
```
Authorization: Bearer <token>
```

**Response** (200 OK):
```json
{
  "message": "Logged out successfully"
}
```

**Authentication**: Required

---

### 2.4 POST /api/auth/password-reset

**Purpose**: Request password reset link.

**Request**:
```json
{
  "email": "student@example.com"
}
```

**Response** (200 OK):
```json
{
  "message": "Password reset email sent",
  "email": "student@example.com"
}
```

**Note**: Always returns 200 even if email not found (security best practice).

---

### 2.5 GET /api/auth/me

**Purpose**: Get current authenticated user profile.

**Response** (200 OK):
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "student@example.com",
  "name": "Ahmed Ali",
  "language_preference": "en",
  "theme": "light",
  "profile": {
    "bio": "Robotics student",
    "avatar_url": "https://...",
    "organization": "FAST University"
  },
  "created_at": "2025-12-09T10:00:00Z",
  "last_login": "2025-12-09T14:00:00Z"
}
```

**Authentication**: Required

---

### 2.6 PATCH /api/auth/profile

**Purpose**: Update user profile and preferences.

**Request**:
```json
{
  "name": "Ahmed Ali",
  "bio": "Robotics student",
  "language_preference": "ur",
  "theme": "dark",
  "avatar_url": "https://..."
}
```

**Response** (200 OK):
```json
{
  "message": "Profile updated successfully",
  "user": { /* updated user object */ }
}
```

**Authentication**: Required

---

## 3. Progress API (`/api/progress`)

### 3.1 GET /api/progress/dashboard

**Purpose**: Retrieve user's full progress dashboard across all modules.

**Response** (200 OK):
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "user_name": "Ahmed Ali",
  "total_completion_percentage": 35,
  "modules": [
    {
      "module_slug": "ros2",
      "module_title": "ROS 2 Fundamentals",
      "completion_percentage": 70,
      "chapters_completed": 3,
      "chapters_total": 5,
      "chapters": [
        {
          "chapter_id": "550e8400-e29b-41d4-a716-446655440001",
          "chapter_slug": "ros2-basics",
          "title": "ROS 2 Basics",
          "is_completed": true,
          "completion_percentage": 100,
          "quiz_score": 85,
          "exercises_completed": 3,
          "exercises_total": 3,
          "last_accessed_at": "2025-12-09T14:00:00Z"
        },
        {
          "chapter_id": "550e8400-e29b-41d4-a716-446655440002",
          "chapter_slug": "ros2-publishers",
          "title": "Publishers & Subscribers",
          "is_completed": true,
          "completion_percentage": 100,
          "quiz_score": 92,
          "exercises_completed": 5,
          "exercises_total": 5,
          "last_accessed_at": "2025-12-08T10:00:00Z"
        }
      ]
    },
    {
      "module_slug": "digital-twin",
      "module_title": "Digital Twin & Simulation",
      "completion_percentage": 0,
      "chapters_completed": 0,
      "chapters_total": 4,
      "chapters": []
    }
  ]
}
```

**Authentication**: Required

**Performance Target**: < 500ms

---

### 3.2 PUT /api/progress/chapters/{chapter_id}

**Purpose**: Update progress for a specific chapter.

**Path Parameter**:
- `chapter_id` (UUID): Chapter to update

**Request**:
```json
{
  "is_completed": true,
  "quiz_score": 85,
  "exercises_completed": 3
}
```

**Response** (200 OK):
```json
{
  "chapter_id": "550e8400-e29b-41d4-a716-446655440001",
  "is_completed": true,
  "completion_percentage": 100,
  "quiz_score": 85,
  "exercises_completed": 3,
  "updated_at": "2025-12-09T14:30:00Z"
}
```

**Error Responses**:
- **404 Not Found**: Chapter not found
- **400 Bad Request**: Invalid quiz_score (not 0-100)

**Authentication**: Required

**Performance Target**: < 500ms

---

### 3.3 GET /api/progress/chapters/{chapter_id}

**Purpose**: Get progress for a single chapter.

**Response** (200 OK):
```json
{
  "chapter_id": "550e8400-e29b-41d4-a716-446655440001",
  "chapter_slug": "ros2-basics",
  "title": "ROS 2 Basics",
  "module_slug": "ros2",
  "is_completed": true,
  "completion_percentage": 100,
  "quiz_score": 85,
  "exercises_completed": 3,
  "exercises_total": 3,
  "last_accessed_at": "2025-12-09T14:00:00Z"
}
```

**Authentication**: Required

---

## 4. Transcribe API (`/api/transcribe`)

### 4.1 POST /api/transcribe

**Purpose**: Transcribe audio to text using Whisper.

**Request** (Multipart Form Data):
```
Content-Type: multipart/form-data

audio: <binary audio file>
language: "en" (optional)
```

**Supported Formats**: MP3, WAV, OPUS, FLAC, M4A
**Max File Size**: 25 MB
**Max Audio Duration**: 300 seconds

**Response** (200 OK):
```json
{
  "transcription_id": "550e8400-e29b-41d4-a716-446655440000",
  "text": "Pick up the blue cube from the table",
  "language": "en",
  "confidence": 0.96,
  "duration_seconds": 3.5,
  "processing_time_ms": 800
}
```

**Error Responses**:
- **400 Bad Request**: Invalid audio format or file too large
- **413 Payload Too Large**: Audio > 25 MB
- **422 Unprocessable Entity**: Audio too long (> 300 seconds)
- **503 Service Unavailable**: Whisper API unavailable

**Authentication**: Required

**Performance Target**: < 2 seconds for typical 5-10 second audio

**Rate Limiting**: 100 requests per minute per user

---

## 5. VLA Planning API (`/api/vla`)

### 5.1 POST /api/vla/plan

**Purpose**: Generate action graph from transcribed voice command.

**Request**:
```json
{
  "transcribed_text": "Pick up the blue cube from the table",
  "robot_state": {
    "pose": [0.0, 0.0, 0.0],
    "gripper_open": true
  }
}
```

**Request Schema**:
```typescript
{
  transcribed_text: string;      // 1-2000 chars. Parsed voice command.
  robot_state?: {
    pose?: [number, number, number];  // [x, y, theta] in meters/radians
    gripper_open?: boolean;
    current_task?: string;
  };
}
```

**Response** (200 OK):
```json
{
  "action_graph_id": "550e8400-e29b-41d4-a716-446655440000",
  "task_description": "Pick up the blue cube from the table",
  "actions": [
    {
      "type": "navigate",
      "parameters": {
        "goal": [1.5, 2.0, 0.0],
        "tolerance_distance": 0.1
      },
      "safety_checks": ["collision_check"],
      "estimated_duration_seconds": 10
    },
    {
      "type": "perceive",
      "parameters": {
        "sensor": "camera",
        "target_class": "cube"
      },
      "safety_checks": [],
      "estimated_duration_seconds": 2
    },
    {
      "type": "grasp",
      "parameters": {
        "object_id": "blue_cube_001",
        "grasp_quality": 0.95
      },
      "safety_checks": ["grasp_stability", "collision_check"],
      "estimated_duration_seconds": 3
    }
  ],
  "estimated_total_duration_seconds": 15,
  "safety_warnings": [],
  "validation_passed": true,
  "validation_errors": []
}
```

**Action Types**:
- `navigate`: Move robot to goal position (uses Nav2)
- `perceive`: Capture and process sensor data (camera, lidar)
- `grasp`: Grasp/manipulate object (uses MoveIt)
- `move_arm`: Move arm to joint angles
- `release`: Release gripper
- `wait`: Wait for specified duration

**Safety Validation**:
- ✅ Check all actions valid in ROS 2 vocabulary
- ✅ Check collision-free paths (Gazebo integration)
- ✅ Check grasp stability (CNN model)
- ✅ Check kinematic feasibility (IK solver)
- ❌ Reject unrecognized actions
- ❌ Flag if success probability < 60%

**Error Responses**:
- **400 Bad Request**: Invalid transcribed text
- **422 Unprocessable Entity**: Action graph validation failed
  ```json
  {
    "error": "VALIDATION_FAILED",
    "message": "Generated action graph failed safety checks",
    "validation_errors": [
      "Action 'teleport' not in ROS 2 vocabulary",
      "Grasp stability too low (0.45 < 0.60 threshold)"
    ],
    "code": 422
  }
  ```
- **503 Service Unavailable**: LLM or validation service down

**Authentication**: Required

**Performance Target**: < 2 seconds for planning, < 1 second for validation

**Rate Limiting**: 20 requests per minute per user

---

### 5.2 POST /api/vla/execute

**Purpose**: Execute action graph on ROS 2 robot (simulation only).

**Request**:
```json
{
  "action_graph_id": "550e8400-e29b-41d4-a716-446655440000",
  "execute_synchronously": true,
  "timeout_seconds": 60
}
```

**Response** (200 OK - async):
```json
{
  "execution_id": "550e8400-e29b-41d4-a716-446655440001",
  "status": "in_progress",
  "action_graph_id": "550e8400-e29b-41d4-a716-446655440000",
  "started_at": "2025-12-09T14:30:00Z",
  "status_url": "/api/vla/execution/550e8400-e29b-41d4-a716-446655440001"
}
```

**Execution States**:
- `pending`: Queued
- `in_progress`: Running
- `success`: Completed successfully
- `failed`: Failed with error
- `timeout`: Exceeded time limit

**Authentication**: Required

---

### 5.3 GET /api/vla/execution/{execution_id}

**Purpose**: Poll execution status.

**Response** (200 OK):
```json
{
  "execution_id": "550e8400-e29b-41d4-a716-446655440001",
  "status": "success",
  "action_graph_id": "550e8400-e29b-41d4-a716-446655440000",
  "started_at": "2025-12-09T14:30:00Z",
  "completed_at": "2025-12-09T14:30:45Z",
  "duration_seconds": 45,
  "success_rate": 0.95,
  "metrics": {
    "navigation_error_meters": 0.05,
    "grasp_success": true,
    "total_actions_executed": 3,
    "total_actions_planned": 3
  },
  "errors": []
}
```

**Authentication**: Required

---

## 6. Health API (`/api/health`)

### 6.1 GET /api/health

**Purpose**: System health check (no auth required, for load balancers).

**Response** (200 OK):
```json
{
  "status": "healthy",
  "timestamp": "2025-12-09T14:30:00Z",
  "services": {
    "database": "healthy",
    "qdrant": "healthy",
    "openai": "healthy",
    "ros2": "healthy"
  },
  "response_time_ms": 45,
  "version": "1.0.0"
}
```

**Service States**:
- `healthy`: Service responding, latency < SLA
- `degraded`: Service responding with latency > SLA
- `unavailable`: Service not responding
- `unknown`: Service status not checked yet

**No Authentication Required**

**Performance Target**: < 100ms

---

## Error Response Format (Standard)

All error responses follow this structure:

```json
{
  "error": "ERROR_CODE",
  "message": "Human-readable description",
  "code": 400,
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2025-12-09T14:30:00Z",
  "details": {
    "field": "query",
    "reason": "Must be 1-2000 characters"
  }
}
```

**HTTP Status Codes**:
| Code | Meaning |
|------|---------|
| 200 | OK |
| 201 | Created |
| 204 | No Content |
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 409 | Conflict |
| 422 | Unprocessable Entity |
| 429 | Too Many Requests |
| 500 | Internal Server Error |
| 503 | Service Unavailable |

---

## Authentication & Authorization

### JWT Token Format
```
Authorization: Bearer <JWT_TOKEN>
```

**Token Payload**:
```json
{
  "sub": "550e8400-e29b-41d4-a716-446655440000",
  "email": "student@example.com",
  "iat": 1702200600,
  "exp": 1702287000,
  "iss": "textbook-api",
  "aud": "textbook-app"
}
```

**Token Expiration**: 24 hours (can be refreshed)

### Scopes (Future)
- `read:chapters` - Read chapter content
- `write:progress` - Update progress
- `read:progress` - Read own progress only
- `admin:translate` - Submit translations

---

## Rate Limiting

| Endpoint | Limit | Window | Note |
|----------|-------|--------|------|
| POST /api/chat/query | 30/min | Per user | Protects LLM cost |
| POST /api/transcribe | 100/min | Per user | Whisper API limit |
| POST /api/vla/plan | 20/min | Per user | Expensive operation |
| POST /api/auth/login | 5/min | Per IP | Brute force protection |
| POST /api/chat/query | 1000/min | Global | System capacity |

**Response on Rate Limit**:
```json
{
  "error": "RATE_LIMIT_EXCEEDED",
  "message": "Too many requests. Try again in 60 seconds.",
  "code": 429,
  "retry_after": 60
}
```

**Response Headers**:
```
X-RateLimit-Limit: 30
X-RateLimit-Remaining: 15
X-RateLimit-Reset: 1702201260
```

---

## Success Criteria (Phase 1 Gate)

- [ ] All endpoints implemented in FastAPI
- [ ] Request/response schemas validated with Pydantic
- [ ] Error handling with proper HTTP status codes
- [ ] Rate limiting middleware active
- [ ] JWT authentication working
- [ ] All endpoints tested with pytest (unit + integration)
- [ ] OpenAPI documentation auto-generated
- [ ] Response times meet targets:
  - Chat queries: < 3 seconds (p95)
  - Auth endpoints: < 500ms
  - Progress endpoints: < 500ms
  - Transcribe: < 2 seconds
  - VLA planning: < 2 seconds
- [ ] Load testing with 100+ concurrent users passes

---

**Next**: Quickstart guide and implementation
