# Skill: Neon Postgres Database Management

**Description**: Using Neon Postgres for scalable, serverless relational database with migration and connection management.

**Scope**:
- Database schema design
- SQL queries and optimization
- Connection pooling
- Migration management
- Backup and recovery
- Performance monitoring

**Key Technologies**:
- Neon Postgres (serverless)
- SQLAlchemy (ORM)
- Alembic (migrations)
- psycopg2-binary (driver)
- Connection pooling (PgBouncer)

**Schema Design**:
```sql
CREATE TABLE users (
  id UUID PRIMARY KEY,
  email VARCHAR UNIQUE NOT NULL,
  password_hash VARCHAR NOT NULL,
  name VARCHAR,
  language_preference VARCHAR(2) DEFAULT 'EN',
  theme_preference VARCHAR(10) DEFAULT 'light',
  created_at TIMESTAMP DEFAULT NOW(),
  last_login TIMESTAMP
);

CREATE TABLE chapters (
  id UUID PRIMARY KEY,
  module_id UUID NOT NULL REFERENCES modules(id),
  slug VARCHAR UNIQUE NOT NULL,
  title VARCHAR NOT NULL,
  content_markdown TEXT,
  order_index INT,
  created_at TIMESTAMP,
  updated_at TIMESTAMP
);

CREATE TABLE chapter_progress (
  user_id UUID NOT NULL REFERENCES users(id),
  chapter_id UUID NOT NULL REFERENCES chapters(id),
  completed_at TIMESTAMP,
  quiz_score FLOAT,
  exercises_completed INT,
  PRIMARY KEY (user_id, chapter_id)
);

CREATE TABLE embeddings (
  id UUID PRIMARY KEY,
  chapter_id UUID REFERENCES chapters(id),
  chunk_text TEXT NOT NULL,
  embedding_model VARCHAR NOT NULL,
  created_at TIMESTAMP
);
```

**Connection String**:
```
postgresql://user:password@ep-cold-lake-123456.us-east-1.postgres.vercel-storage.com/verceldb
```

**SQLAlchemy Models**:
```python
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(UUID, primary_key=True)
    email = Column(String, unique=True)
    password_hash = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
```

**Alembic Migration**:
```bash
alembic init migrations
alembic revision --autogenerate -m "Add users table"
alembic upgrade head
```

**Query Optimization**:
- Use indexes on frequently filtered columns (email, chapter_id)
- Batch operations for inserts/updates
- Connection pooling (10-20 connections)
- Avoid N+1 queries (use joins)

**Performance Targets**:
- Query latency < 50ms (p95)
- Connection pool utilization < 80%
- Backup retention: 7 days

**Monitoring**:
- Query logs (Neon dashboard)
- Slow query identification
- Connection pool monitoring
- Storage usage alerts

**Owner**: Authentication Agent, RAG Chatbot Agent

**Related**: authentication-agent.md, rag-chatbot-agent.md
