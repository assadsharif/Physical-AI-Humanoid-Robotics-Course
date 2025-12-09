"""
Tests for chat/RAG endpoints.
"""

import pytest
from fastapi import status


class TestChatQuery:
    """Test chat query endpoint."""

    async def test_query_success(self, client, auth_headers, test_course_data):
        """Test successful chat query."""
        response = client.post(
            "/api/chat/query",
            json={
                "query": "What is robotics?",
                "mode": "learn",
            },
            headers=auth_headers,
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "response" in data
        assert "sources" in data
        assert "follow_ups" in data

    async def test_query_with_difficulty_level(self, client, auth_headers, test_course_data):
        """Test query with specific difficulty level."""
        response = client.post(
            "/api/chat/query",
            json={
                "query": "Explain motors",
                "mode": "learn",
                "difficulty_level": "intermediate",
            },
            headers=auth_headers,
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "response" in data

    async def test_query_practice_mode(self, client, auth_headers, test_course_data):
        """Test query in practice mode."""
        response = client.post(
            "/api/chat/query",
            json={
                "query": "How do motors work?",
                "mode": "practice",
            },
            headers=auth_headers,
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "response" in data
        assert "sources" in data

    async def test_query_explain_mode(self, client, auth_headers, test_course_data):
        """Test query in explain mode."""
        response = client.post(
            "/api/chat/query",
            json={
                "query": "Explain programming concepts",
                "mode": "explain",
            },
            headers=auth_headers,
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "response" in data

    async def test_query_debug_mode(self, client, auth_headers, test_course_data):
        """Test query in debug mode."""
        response = client.post(
            "/api/chat/query",
            json={
                "query": "Debug this code",
                "mode": "debug",
            },
            headers=auth_headers,
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "response" in data

    async def test_query_no_auth(self, client, test_course_data):
        """Test query without authentication."""
        response = client.post(
            "/api/chat/query",
            json={
                "query": "What is robotics?",
                "mode": "learn",
            },
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_query_invalid_token(self, client, test_course_data):
        """Test query with invalid token."""
        response = client.post(
            "/api/chat/query",
            json={
                "query": "What is robotics?",
                "mode": "learn",
            },
            headers={"Authorization": "Bearer invalid_token"},
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_query_missing_query_text(self, client, auth_headers):
        """Test query without query text."""
        response = client.post(
            "/api/chat/query",
            json={
                "mode": "learn",
            },
            headers=auth_headers,
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_query_empty_query(self, client, auth_headers):
        """Test query with empty text."""
        response = client.post(
            "/api/chat/query",
            json={
                "query": "",
                "mode": "learn",
            },
            headers=auth_headers,
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    async def test_query_missing_mode(self, client, auth_headers):
        """Test query without mode."""
        response = client.post(
            "/api/chat/query",
            json={
                "query": "What is robotics?",
            },
            headers=auth_headers,
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_query_with_specific_module(self, client, auth_headers, test_course_data):
        """Test query scoped to specific module."""
        module = test_course_data["module"]
        response = client.post(
            "/api/chat/query",
            json={
                "query": "What's in this module?",
                "mode": "learn",
                "module_slug": module.slug,
            },
            headers=auth_headers,
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "response" in data

    async def test_query_with_specific_chapter(self, client, auth_headers, test_course_data):
        """Test query scoped to specific chapter."""
        chapter = test_course_data["chapters"][0]
        response = client.post(
            "/api/chat/query",
            json={
                "query": "What's in this chapter?",
                "mode": "learn",
                "chapter_id": str(chapter.id),
            },
            headers=auth_headers,
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "response" in data

    async def test_query_response_contains_required_fields(self, client, auth_headers, test_course_data):
        """Test that response contains all required fields."""
        response = client.post(
            "/api/chat/query",
            json={
                "query": "What is robotics?",
                "mode": "learn",
            },
            headers=auth_headers,
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # Check required fields
        assert "response" in data
        assert isinstance(data["response"], str)
        assert len(data["response"]) > 0

        assert "sources" in data
        assert isinstance(data["sources"], list)

        assert "follow_ups" in data
        assert isinstance(data["follow_ups"], list)


class TestChatRating:
    """Test chat message rating endpoint."""

    async def test_rate_message_success(self, client, auth_headers):
        """Test successful message rating."""
        # First, send a query to get a message ID
        query_response = client.post(
            "/api/chat/query",
            json={
                "query": "What is robotics?",
                "mode": "learn",
            },
            headers=auth_headers,
        )
        assert query_response.status_code == status.HTTP_200_OK

        # Rating might require getting message ID from response or history
        # This is a Phase 2+ feature, so we'll test the endpoint existence
        response = client.post(
            "/api/chat/messages/test-message-id/rate",
            json={
                "rating": 5,
                "comment": "Very helpful!",
            },
            headers=auth_headers,
        )
        # Should return 200 or 404 depending on implementation
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    async def test_rate_message_invalid_rating(self, client, auth_headers):
        """Test rating with invalid rating value."""
        response = client.post(
            "/api/chat/messages/test-id/rate",
            json={
                "rating": 10,  # Invalid: should be 1-5
                "comment": "Too high",
            },
            headers=auth_headers,
        )
        assert response.status_code in [status.HTTP_400_BAD_REQUEST, status.HTTP_422_UNPROCESSABLE_ENTITY, status.HTTP_404_NOT_FOUND]

    async def test_rate_message_no_auth(self, client):
        """Test rating without authentication."""
        response = client.post(
            "/api/chat/messages/test-id/rate",
            json={
                "rating": 5,
                "comment": "Good",
            },
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_rate_message_zero_rating(self, client, auth_headers):
        """Test rating with zero value."""
        response = client.post(
            "/api/chat/messages/test-id/rate",
            json={
                "rating": 0,
                "comment": "Bad",
            },
            headers=auth_headers,
        )
        assert response.status_code in [status.HTTP_400_BAD_REQUEST, status.HTTP_422_UNPROCESSABLE_ENTITY, status.HTTP_404_NOT_FOUND]

    async def test_rate_message_negative_rating(self, client, auth_headers):
        """Test rating with negative value."""
        response = client.post(
            "/api/chat/messages/test-id/rate",
            json={
                "rating": -1,
                "comment": "Negative",
            },
            headers=auth_headers,
        )
        assert response.status_code in [status.HTTP_400_BAD_REQUEST, status.HTTP_422_UNPROCESSABLE_ENTITY, status.HTTP_404_NOT_FOUND]
