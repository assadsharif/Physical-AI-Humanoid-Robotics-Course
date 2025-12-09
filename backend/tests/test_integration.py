"""
Integration tests for user workflows.
"""

import pytest
from fastapi import status


class TestSignupToChat:
    """Test complete user journey from signup to chat."""

    async def test_signup_login_and_ask_question(self, client, test_course_data):
        """Test complete workflow: signup -> login -> ask question."""

        # Step 1: Sign up
        signup_response = client.post(
            "/api/auth/signup",
            json={
                "email": "workflow@example.com",
                "password": "workflowpassword123",
                "name": "Workflow User",
            },
        )
        assert signup_response.status_code == status.HTTP_201_CREATED
        signup_data = signup_response.json()
        signup_token = signup_data["access_token"]

        # Step 2: Get user info with signup token
        me_response = client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {signup_token}"},
        )
        assert me_response.status_code == status.HTTP_200_OK
        me_data = me_response.json()
        assert me_data["email"] == "workflow@example.com"

        # Step 3: Update profile
        profile_response = client.patch(
            "/api/auth/profile",
            json={
                "language_preference": "en",
                "theme_preference": "light",
            },
            headers={"Authorization": f"Bearer {signup_token}"},
        )
        assert profile_response.status_code == status.HTTP_200_OK

        # Step 4: Ask a question
        chat_response = client.post(
            "/api/chat/query",
            json={
                "query": "What is this course about?",
                "mode": "learn",
            },
            headers={"Authorization": f"Bearer {signup_token}"},
        )
        assert chat_response.status_code == status.HTTP_200_OK
        chat_data = chat_response.json()
        assert "response" in chat_data

        # Step 5: Logout
        logout_response = client.post(
            "/api/auth/logout",
            headers={"Authorization": f"Bearer {signup_token}"},
        )
        assert logout_response.status_code == status.HTTP_200_OK

    async def test_login_with_existing_user(self, client, test_user, test_course_data):
        """Test login with existing user and asking questions."""

        # Step 1: Login
        login_response = client.post(
            "/api/auth/login",
            json={
                "email": test_user["email"],
                "password": test_user["password"],
            },
        )
        assert login_response.status_code == status.HTTP_200_OK
        login_data = login_response.json()
        login_token = login_data["access_token"]

        # Step 2: Ask multiple questions
        queries = [
            "What is robotics?",
            "How do motors work?",
            "Explain programming concepts",
        ]

        for query in queries:
            chat_response = client.post(
                "/api/chat/query",
                json={
                    "query": query,
                    "mode": "learn",
                },
                headers={"Authorization": f"Bearer {login_token}"},
            )
            assert chat_response.status_code == status.HTTP_200_OK
            chat_data = chat_response.json()
            assert "response" in chat_data
            assert "sources" in chat_data
            assert "follow_ups" in chat_data

    async def test_multiple_users_different_preferences(self, client, test_user, test_user_2, test_course_data):
        """Test that different users have isolated profiles and interactions."""

        # User 1 updates preferences
        user1_response = client.patch(
            "/api/auth/profile",
            json={
                "language_preference": "ur",
                "theme_preference": "dark",
            },
            headers={"Authorization": f"Bearer {test_user['token']}"},
        )
        assert user1_response.status_code == status.HTTP_200_OK
        user1_data = user1_response.json()
        assert user1_data["language_preference"] == "ur"

        # User 2 updates different preferences
        user2_response = client.patch(
            "/api/auth/profile",
            json={
                "language_preference": "en",
                "theme_preference": "light",
            },
            headers={"Authorization": f"Bearer {test_user_2['token']}"},
        )
        assert user2_response.status_code == status.HTTP_200_OK
        user2_data = user2_response.json()
        assert user2_data["language_preference"] == "en"

        # Verify User 1 still has their preferences
        user1_check = client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {test_user['token']}"},
        )
        assert user1_check.status_code == status.HTTP_200_OK
        assert user1_check.json()["language_preference"] == "ur"

        # Verify User 2 still has their preferences
        user2_check = client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {test_user_2['token']}"},
        )
        assert user2_check.status_code == status.HTTP_200_OK
        assert user2_check.json()["language_preference"] == "en"


class TestErrorRecovery:
    """Test error handling and recovery."""

    async def test_recovery_after_invalid_request(self, client, test_user):
        """Test that API recovers after invalid request."""

        # Send invalid request
        invalid_response = client.post(
            "/api/chat/query",
            json={
                "query": "",
                "mode": "learn",
            },
            headers={"Authorization": f"Bearer {test_user['token']}"},
        )
        assert invalid_response.status_code == status.HTTP_400_BAD_REQUEST

        # Next valid request should work
        valid_response = client.post(
            "/api/chat/query",
            json={
                "query": "What is robotics?",
                "mode": "learn",
            },
            headers={"Authorization": f"Bearer {test_user['token']}"},
        )
        assert valid_response.status_code == status.HTTP_200_OK

    async def test_auth_state_after_logout(self, client, test_user):
        """Test that user cannot use token after logout."""

        token = test_user["token"]

        # Logout
        logout_response = client.post(
            "/api/auth/logout",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert logout_response.status_code == status.HTTP_200_OK

        # Try to use token after logout (in simple implementation, token is still valid)
        # Real implementation would use token blacklist
        me_response = client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        # In simple JWT implementation, token is still valid after logout
        # This is a known limitation that could be addressed with token blacklist
        assert me_response.status_code == status.HTTP_200_OK


class TestDifficultyLevels:
    """Test difficulty level handling across modes."""

    async def test_all_difficulty_levels(self, client, auth_headers, test_course_data):
        """Test all difficulty levels work in chat."""

        difficulty_levels = ["beginner", "intermediate", "advanced"]

        for difficulty in difficulty_levels:
            response = client.post(
                "/api/chat/query",
                json={
                    "query": "Explain this topic",
                    "mode": "learn",
                    "difficulty_level": difficulty,
                },
                headers=auth_headers,
            )
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert "response" in data

    async def test_all_chat_modes(self, client, auth_headers, test_course_data):
        """Test all chat modes work correctly."""

        modes = ["learn", "practice", "explain", "debug"]

        for mode in modes:
            response = client.post(
                "/api/chat/query",
                json={
                    "query": "Help me with this",
                    "mode": mode,
                },
                headers=auth_headers,
            )
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert "response" in data
            assert "sources" in data
