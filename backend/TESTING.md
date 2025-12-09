# Testing Guide

This document describes how to run and understand the test suite for the robotics learning platform backend.

## Quick Start

### Run All Tests

```bash
pytest
```

### Run Tests with Coverage

```bash
pytest --cov=src --cov-report=html
```

### Run Specific Test File

```bash
pytest tests/test_auth.py
```

### Run Tests by Marker

```bash
pytest -m auth          # Run only authentication tests
pytest -m chat          # Run only chat tests
pytest -m integration   # Run only integration tests
pytest -m health        # Run only health check tests
```

### Run Tests in Verbose Mode

```bash
pytest -v
```

## Test Organization

The test suite is organized into the following modules:

### `tests/test_auth.py` - Authentication Tests

Tests for user registration, login, profile management, and logout.

**Test Classes:**
- `TestSignup` - User registration endpoint tests
  - ✓ Successful signup with valid data
  - ✓ Error handling for missing fields
  - ✓ Duplicate email detection
  - ✓ Password validation
  - ✓ Email format validation

- `TestLogin` - User login endpoint tests
  - ✓ Successful login
  - ✓ Wrong password handling
  - ✓ Non-existent user handling
  - ✓ Invalid credentials handling

- `TestGetMe` - Get current user tests
  - ✓ Retrieve authenticated user info
  - ✓ Authorization checks
  - ✓ Invalid token handling

- `TestUpdateProfile` - Profile update tests
  - ✓ Update language preference
  - ✓ Update theme preference
  - ✓ Multiple field updates
  - ✓ Authorization checks

- `TestLogout` - Logout endpoint tests
  - ✓ Successful logout
  - ✓ Authorization checks

### `tests/test_chat.py` - Chat and RAG Tests

Tests for question answering, RAG pipeline, and response quality.

**Test Classes:**
- `TestChatQuery` - Chat query endpoint tests
  - ✓ Successful queries in all modes (learn, practice, explain, debug)
  - ✓ Difficulty level selection
  - ✓ Module/chapter scoping
  - ✓ Response structure validation
  - ✓ Authorization checks
  - ✓ Input validation

- `TestChatRating` - Message rating tests (Phase 2+)
  - ✓ Rating responses
  - ✓ Input validation
  - ✓ Authorization checks

### `tests/test_health.py` - Health and General Tests

Tests for health checks, error handling, and general API behavior.

**Test Classes:**
- `TestHealth` - Health check endpoint
  - ✓ Service status monitoring

- `TestNotFound` - 404 error handling
  - ✓ Non-existent endpoint responses

- `TestCORS` - CORS configuration
  - ✓ CORS header presence

- `TestErrorHandling` - General error handling
  - ✓ Malformed JSON handling
  - ✓ Invalid HTTP methods
  - ✓ Missing content types

### `tests/test_integration.py` - Integration Tests

End-to-end workflow tests simulating real user scenarios.

**Test Classes:**
- `TestSignupToChat` - Complete user journey tests
  - ✓ Signup → Login → Ask question → Logout
  - ✓ Multi-question workflows
  - ✓ User isolation verification

- `TestErrorRecovery` - Error recovery tests
  - ✓ API recovery after invalid requests
  - ✓ Auth state management

- `TestDifficultyLevels` - Difficulty level tests
  - ✓ All difficulty levels work correctly
  - ✓ All chat modes work correctly

## Test Fixtures

The `conftest.py` file provides shared fixtures:

### Database Fixtures
- `test_db` - In-memory SQLite database for testing
- `client` - FastAPI test client (synchronous)
- `async_client` - FastAPI async test client

### User Fixtures
- `test_user` - Pre-created test user with token
- `test_user_2` - Second test user for multi-user scenarios

### Course Data Fixtures
- `test_course_data` - Pre-populated course structure with modules, chapters, and embeddings

### Helper Fixtures
- `auth_headers` - Authorization headers with test user token
- `auth_headers_2` - Authorization headers with second test user token

## Test Database

Tests use SQLite in-memory database for fast execution:

```python
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
```

This means:
- ✓ No external dependencies
- ✓ Fast execution
- ✓ Clean state for each test
- ✓ Isolated from production database

## Running Tests

### Local Development

```bash
# Install test dependencies
pip install -r requirements.txt

# Run all tests
pytest

# Run with coverage report
pytest --cov=src --cov-report=term-missing

# Run specific test
pytest tests/test_auth.py::TestSignup::test_signup_success -v
```

### In CI/CD Pipeline

Tests run automatically on:
- Pull requests
- Commits to main branch
- Manual workflow dispatch

See `.github/workflows/test.yml` for CI configuration.

## Test Coverage Goals

- Authentication: 95%+ coverage
- Chat endpoints: 90%+ coverage
- Database operations: 90%+ coverage
- Error handling: 85%+ coverage
- Overall: 85%+ coverage

Current coverage can be checked with:

```bash
pytest --cov=src --cov-report=html
open htmlcov/index.html
```

## Common Test Issues

### Issue: `ModuleNotFoundError: No module named 'src'`

**Solution:** Ensure pytest is run from the `backend/` directory:

```bash
cd backend
pytest
```

### Issue: `RuntimeError: Event loop is closed`

**Solution:** This is common with pytest-asyncio. Update pytest.ini:

```ini
[pytest]
asyncio_mode = auto
```

### Issue: Tests timeout

**Solution:** Increase timeout in pytest.ini or specific tests:

```python
@pytest.mark.asyncio
async def test_slow_operation():
    # test code
    pass
```

## Writing New Tests

### Basic Test Structure

```python
async def test_feature_name(self, client, auth_headers):
    """Test description."""
    response = client.post(
        "/api/endpoint",
        json={"key": "value"},
        headers=auth_headers,
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["expected_field"] == "expected_value"
```

### Using Fixtures

```python
async def test_with_fixtures(self, client, test_user, test_course_data):
    """Test with pre-populated data."""
    module = test_course_data["module"]
    chapter = test_course_data["chapters"][0]

    # Use test data in your test
    response = client.post(
        f"/api/chat/query",
        json={"query": "Test", "mode": "learn"},
        headers={"Authorization": f"Bearer {test_user['token']}"},
    )
```

### Testing Error Cases

```python
async def test_invalid_input(self, client):
    """Test validation error handling."""
    response = client.post(
        "/api/auth/signup",
        json={"email": "invalid"},  # Missing required fields
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
```

## Continuous Integration

Tests run automatically on:

1. **Pull Requests** - All tests must pass before merging
2. **Main Branch** - Verify production readiness
3. **Manual Trigger** - Run full test suite on demand

See GitHub Actions workflows in `.github/workflows/` for details.

## Performance

Test execution times:
- Unit tests: ~2-5 seconds
- Integration tests: ~3-8 seconds
- Full suite: ~15-30 seconds

Monitor with:

```bash
pytest --durations=10  # Show 10 slowest tests
```

## Troubleshooting

### Debug failing test

```bash
pytest tests/test_auth.py::TestSignup::test_signup_success -vv -s
```

Options:
- `-vv` - Extra verbose output
- `-s` - Show print statements
- `-x` - Stop on first failure
- `--pdb` - Drop into debugger on failure

### Check test dependencies

```bash
pytest --collect-only  # Show all collected tests
```

## Best Practices

1. **Test isolation** - Each test should be independent
2. **Clear names** - Test names should describe what's being tested
3. **Arrange-Act-Assert** - Follow AAA pattern in tests
4. **DRY** - Use fixtures to avoid repetition
5. **Focus** - Test one thing per test function
6. **Speed** - Keep tests fast using in-memory database
7. **Clarity** - Use descriptive assertions

## Further Reading

- [FastAPI Testing Documentation](https://fastapi.tiangolo.com/advanced/testing-websockets/)
- [pytest Documentation](https://docs.pytest.org/)
- [pytest-asyncio Documentation](https://pytest-asyncio.readthedocs.io/)
