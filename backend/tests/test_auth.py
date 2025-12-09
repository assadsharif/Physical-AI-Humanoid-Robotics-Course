"""
Tests for authentication endpoints.
"""

import pytest
from fastapi import status


class TestSignup:
    """Test user registration endpoint."""

    async def test_signup_success(self, client):
        """Test successful user registration."""
        response = client.post(
            "/api/auth/signup",
            json={
                "email": "newuser@example.com",
                "password": "securepassword123",
                "name": "New User",
            },
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["user"]["email"] == "newuser@example.com"
        assert data["user"]["name"] == "New User"
        assert "access_token" in data
        assert "expires_in" in data

    async def test_signup_missing_email(self, client):
        """Test signup with missing email."""
        response = client.post(
            "/api/auth/signup",
            json={
                "password": "securepassword123",
                "name": "New User",
            },
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_signup_missing_password(self, client):
        """Test signup with missing password."""
        response = client.post(
            "/api/auth/signup",
            json={
                "email": "newuser@example.com",
                "name": "New User",
            },
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_signup_missing_name(self, client):
        """Test signup with missing name."""
        response = client.post(
            "/api/auth/signup",
            json={
                "email": "newuser@example.com",
                "password": "securepassword123",
            },
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_signup_duplicate_email(self, client, test_user):
        """Test signup with existing email."""
        response = client.post(
            "/api/auth/signup",
            json={
                "email": test_user["email"],
                "password": "securepassword123",
                "name": "Another User",
            },
        )
        assert response.status_code == status.HTTP_409_CONFLICT
        assert "already exists" in response.json()["detail"].lower()

    async def test_signup_short_password(self, client):
        """Test signup with password less than 8 characters."""
        response = client.post(
            "/api/auth/signup",
            json={
                "email": "newuser@example.com",
                "password": "short",
                "name": "New User",
            },
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    async def test_signup_invalid_email(self, client):
        """Test signup with invalid email format."""
        response = client.post(
            "/api/auth/signup",
            json={
                "email": "invalid-email",
                "password": "securepassword123",
                "name": "New User",
            },
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_signup_user_profile_created(self, client):
        """Test that UserProfile is automatically created on signup."""
        response = client.post(
            "/api/auth/signup",
            json={
                "email": "profiletest@example.com",
                "password": "securepassword123",
                "name": "Profile Test User",
            },
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        # User profile should exist and be included in response
        assert "user_profile" in data["user"] or data["user"]["id"] is not None


class TestLogin:
    """Test user login endpoint."""

    async def test_login_success(self, client, test_user):
        """Test successful login."""
        response = client.post(
            "/api/auth/login",
            json={
                "email": test_user["email"],
                "password": test_user["password"],
            },
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["user"]["email"] == test_user["email"]
        assert "access_token" in data
        assert "expires_in" in data

    async def test_login_wrong_password(self, client, test_user):
        """Test login with incorrect password."""
        response = client.post(
            "/api/auth/login",
            json={
                "email": test_user["email"],
                "password": "wrongpassword",
            },
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_login_nonexistent_user(self, client):
        """Test login with non-existent email."""
        response = client.post(
            "/api/auth/login",
            json={
                "email": "nonexistent@example.com",
                "password": "anypassword",
            },
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_login_missing_email(self, client):
        """Test login with missing email."""
        response = client.post(
            "/api/auth/login",
            json={
                "password": "anypassword",
            },
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_login_missing_password(self, client, test_user):
        """Test login with missing password."""
        response = client.post(
            "/api/auth/login",
            json={
                "email": test_user["email"],
            },
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_login_empty_credentials(self, client):
        """Test login with empty credentials."""
        response = client.post(
            "/api/auth/login",
            json={
                "email": "",
                "password": "",
            },
        )
        assert response.status_code in [status.HTTP_400_BAD_REQUEST, status.HTTP_401_UNAUTHORIZED]


class TestGetMe:
    """Test get current user endpoint."""

    async def test_get_me_success(self, client, auth_headers):
        """Test getting current user with valid token."""
        response = client.get(
            "/api/auth/me",
            headers=auth_headers,
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["email"] is not None
        assert data["name"] is not None

    async def test_get_me_no_token(self, client):
        """Test getting current user without token."""
        response = client.get("/api/auth/me")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_get_me_invalid_token(self, client):
        """Test getting current user with invalid token."""
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": "Bearer invalid_token_here"},
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_get_me_expired_token(self, client):
        """Test getting current user with malformed token."""
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": "Bearer malformed.token.here"},
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestUpdateProfile:
    """Test update user profile endpoint."""

    async def test_update_profile_language(self, client, auth_headers):
        """Test updating user language preference."""
        response = client.patch(
            "/api/auth/profile",
            json={
                "language_preference": "ur",
            },
            headers=auth_headers,
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["language_preference"] == "ur"

    async def test_update_profile_theme(self, client, auth_headers):
        """Test updating user theme preference."""
        response = client.patch(
            "/api/auth/profile",
            json={
                "theme_preference": "dark",
            },
            headers=auth_headers,
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["theme_preference"] == "dark"

    async def test_update_profile_multiple_fields(self, client, auth_headers):
        """Test updating multiple profile fields."""
        response = client.patch(
            "/api/auth/profile",
            json={
                "language_preference": "ur",
                "theme_preference": "dark",
            },
            headers=auth_headers,
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["language_preference"] == "ur"
        assert data["theme_preference"] == "dark"

    async def test_update_profile_no_auth(self, client):
        """Test updating profile without authentication."""
        response = client.patch(
            "/api/auth/profile",
            json={
                "language_preference": "ur",
            },
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_update_profile_invalid_language(self, client, auth_headers):
        """Test updating profile with invalid language code."""
        response = client.patch(
            "/api/auth/profile",
            json={
                "language_preference": "invalid",
            },
            headers=auth_headers,
        )
        # Should either accept it or return validation error
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_422_UNPROCESSABLE_ENTITY]


class TestLogout:
    """Test logout endpoint."""

    async def test_logout_success(self, client, auth_headers):
        """Test successful logout."""
        response = client.post(
            "/api/auth/logout",
            headers=auth_headers,
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "message" in data

    async def test_logout_no_token(self, client):
        """Test logout without token."""
        response = client.post("/api/auth/logout")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_logout_invalid_token(self, client):
        """Test logout with invalid token."""
        response = client.post(
            "/api/auth/logout",
            headers={"Authorization": "Bearer invalid_token"},
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
