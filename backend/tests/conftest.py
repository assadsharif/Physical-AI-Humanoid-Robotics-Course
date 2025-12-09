"""
Pytest configuration and fixtures for API testing.
"""

import pytest
import os
import sys
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import StaticPool

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from fastapi.testclient import TestClient
from httpx import AsyncClient

from main import app
from db import get_db, Base
from db.models import User, UserProfile, Module, Chapter, Embedding
from services.auth_service import AuthService


# Test database URL using SQLite in-memory
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture
async def test_db():
    """Create a test database and yield session."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async def override_get_db():
        async with async_session() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db

    yield async_session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.fixture
def client(test_db):
    """Create a test client."""
    return TestClient(app)


@pytest.fixture
async def async_client(test_db):
    """Create an async test client."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture
async def test_user(test_db):
    """Create a test user."""
    async_session = test_db

    async with async_session() as session:
        auth_service = AuthService()
        user, token, expires_in = await auth_service.register_user(
            user_data={
                "email": "test@example.com",
                "password": "testpassword123",
                "name": "Test User",
            },
            session=session,
        )
        await session.commit()
        return {
            "user": user,
            "token": token,
            "email": "test@example.com",
            "password": "testpassword123",
        }


@pytest.fixture
async def test_user_2(test_db):
    """Create a second test user for multi-user scenarios."""
    async_session = test_db

    async with async_session() as session:
        auth_service = AuthService()
        user, token, expires_in = await auth_service.register_user(
            user_data={
                "email": "test2@example.com",
                "password": "testpassword456",
                "name": "Test User 2",
            },
            session=session,
        )
        await session.commit()
        return {
            "user": user,
            "token": token,
            "email": "test2@example.com",
            "password": "testpassword456",
        }


@pytest.fixture
async def test_course_data(test_db):
    """Create test course structure with modules and chapters."""
    async_session = test_db

    async with async_session() as session:
        # Create module
        module = Module(
            title="Introduction to Robotics",
            slug="intro-robotics",
            description="Basic robotics concepts",
            order=1,
        )
        session.add(module)
        await session.flush()

        # Create chapters
        chapters = []
        for i in range(3):
            chapter = Chapter(
                title=f"Chapter {i + 1}",
                slug=f"chapter-{i + 1}",
                content=f"Content for chapter {i + 1}",
                difficulty_level="beginner",
                module_id=module.id,
                order=i + 1,
            )
            session.add(chapter)
            chapters.append(chapter)

        await session.flush()

        # Create embeddings
        embeddings = []
        for i, chapter in enumerate(chapters):
            for j in range(3):
                embedding = Embedding(
                    chapter_id=chapter.id,
                    module_slug=module.slug,
                    content=f"Embedding {j + 1} for chapter {i + 1}",
                    vector=[0.1] * 1536,  # Dummy vector
                    qdrant_id=f"{chapter.id}_{j}",
                )
                session.add(embedding)
                embeddings.append(embedding)

        await session.commit()

        return {
            "module": module,
            "chapters": chapters,
            "embeddings": embeddings,
        }


@pytest.fixture
def auth_headers(test_user):
    """Generate authorization headers with test user token."""
    return {"Authorization": f"Bearer {test_user['token']}"}


@pytest.fixture
def auth_headers_2(test_user_2):
    """Generate authorization headers with second test user token."""
    return {"Authorization": f"Bearer {test_user_2['token']}"}
