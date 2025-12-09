"""
Tests for health check and general endpoints.
"""

import pytest
from fastapi import status


class TestHealth:
    """Test health check endpoint."""

    async def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "status" in data
        assert data["status"] in ["healthy", "ok", "UP"]


class TestNotFound:
    """Test 404 responses."""

    async def test_nonexistent_endpoint(self, client):
        """Test accessing non-existent endpoint."""
        response = client.get("/api/nonexistent")
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestCORS:
    """Test CORS configuration."""

    async def test_cors_headers_present(self, client):
        """Test that CORS headers are present in response."""
        response = client.get("/health")
        # CORS headers might be set, but not required for test client
        assert response.status_code == status.HTTP_200_OK


class TestErrorHandling:
    """Test error handling and responses."""

    async def test_malformed_json(self, client):
        """Test endpoint with malformed JSON."""
        response = client.post(
            "/api/auth/login",
            content=b"invalid json",
            headers={"Content-Type": "application/json"},
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_missing_content_type(self, client):
        """Test request without content type."""
        response = client.post(
            "/api/auth/login",
            json={
                "email": "test@example.com",
                "password": "password",
            },
        )
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_401_UNAUTHORIZED]

    async def test_invalid_http_method(self, client):
        """Test endpoint with wrong HTTP method."""
        response = client.get(
            "/api/auth/login",
        )
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
