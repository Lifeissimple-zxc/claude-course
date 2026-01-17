"""
Tests for FastAPI endpoints in app.py.

These tests validate the HTTP request/response handling for all API endpoints:
- POST /api/query
- GET /api/courses
- DELETE /api/session/{session_id}
- GET / (root endpoint)
"""
import pytest


class TestRootEndpoint:
    """Tests for GET / endpoint."""

    async def test_root_returns_ok_status(self, async_client):
        """Test root endpoint returns 200 with status message."""
        response = await async_client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "message" in data


class TestQueryEndpoint:
    """Tests for POST /api/query endpoint."""

    async def test_query_success_with_session_id(self, async_client):
        """Test successful query with provided session_id."""
        response = await async_client.post(
            "/api/query",
            json={"query": "What is Python?", "session_id": "existing-session"}
        )

        assert response.status_code == 200
        data = response.json()
        assert "answer" in data
        assert "sources" in data
        assert data["session_id"] == "existing-session"

    async def test_query_success_without_session_id(self, async_client):
        """Test successful query creates new session when none provided."""
        response = await async_client.post(
            "/api/query",
            json={"query": "Explain machine learning"}
        )

        assert response.status_code == 200
        data = response.json()
        assert "answer" in data
        assert "session_id" in data
        # Session should be created by mock
        assert data["session_id"] == "test-session-123"

    async def test_query_returns_sources(self, async_client):
        """Test query returns sources in response."""
        response = await async_client.post(
            "/api/query",
            json={"query": "Tell me about data structures"}
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data["sources"], list)
        assert len(data["sources"]) > 0
        # Verify source structure
        source = data["sources"][0]
        assert "title" in source
        assert "link" in source

    async def test_query_missing_query_field(self, async_client):
        """Test query endpoint returns 422 for missing query field."""
        response = await async_client.post(
            "/api/query",
            json={"session_id": "some-session"}
        )

        assert response.status_code == 422
        data = response.json()
        assert "detail" in data

    async def test_query_empty_query_string(self, async_client):
        """Test query with empty string still processes."""
        response = await async_client.post(
            "/api/query",
            json={"query": ""}
        )

        # Empty string is technically valid - endpoint should process it
        assert response.status_code == 200

    async def test_query_invalid_json(self, async_client):
        """Test query endpoint handles invalid JSON."""
        response = await async_client.post(
            "/api/query",
            content="not valid json",
            headers={"Content-Type": "application/json"}
        )

        assert response.status_code == 422

    async def test_query_wrong_content_type(self, async_client):
        """Test query endpoint rejects non-JSON content type."""
        response = await async_client.post(
            "/api/query",
            content="query=test",
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )

        assert response.status_code == 422

    async def test_query_error_returns_500(self, async_client_error):
        """Test query returns 500 when RAG system fails."""
        response = await async_client_error.post(
            "/api/query",
            json={"query": "This will fail"}
        )

        assert response.status_code == 500
        data = response.json()
        assert "detail" in data
        assert "RAG system error" in data["detail"]


class TestCoursesEndpoint:
    """Tests for GET /api/courses endpoint."""

    async def test_courses_success(self, async_client):
        """Test courses endpoint returns course statistics."""
        response = await async_client.get("/api/courses")

        assert response.status_code == 200
        data = response.json()
        assert "total_courses" in data
        assert "course_titles" in data
        assert data["total_courses"] == 3
        assert len(data["course_titles"]) == 3

    async def test_courses_returns_correct_structure(self, async_client):
        """Test courses endpoint returns properly typed data."""
        response = await async_client.get("/api/courses")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data["total_courses"], int)
        assert isinstance(data["course_titles"], list)
        for title in data["course_titles"]:
            assert isinstance(title, str)

    async def test_courses_error_returns_500(self, async_client_error):
        """Test courses returns 500 when analytics fails."""
        response = await async_client_error.get("/api/courses")

        assert response.status_code == 500
        data = response.json()
        assert "detail" in data


class TestSessionEndpoint:
    """Tests for DELETE /api/session/{session_id} endpoint."""

    async def test_session_clear_success(self, async_client):
        """Test successful session clearing."""
        response = await async_client.delete("/api/session/test-session-123")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "cleared"
        assert data["session_id"] == "test-session-123"

    async def test_session_clear_any_session_id(self, async_client):
        """Test clearing works with any session ID format."""
        response = await async_client.delete("/api/session/arbitrary-id-format-456")

        assert response.status_code == 200
        data = response.json()
        assert data["session_id"] == "arbitrary-id-format-456"

    async def test_session_clear_special_characters(self, async_client):
        """Test clearing session with URL-safe special characters."""
        # Session IDs might contain hyphens, underscores
        response = await async_client.delete("/api/session/session_with-mixed_chars-123")

        assert response.status_code == 200

    async def test_session_error_returns_500(self, async_client_error):
        """Test session clear returns 500 when session manager fails."""
        response = await async_client_error.delete("/api/session/nonexistent")

        assert response.status_code == 500
        data = response.json()
        assert "detail" in data


class TestRequestValidation:
    """Tests for request validation across endpoints."""

    async def test_query_extra_fields_ignored(self, async_client):
        """Test extra fields in request body are ignored."""
        response = await async_client.post(
            "/api/query",
            json={
                "query": "Test query",
                "extra_field": "should be ignored",
                "another_field": 123
            }
        )

        assert response.status_code == 200

    async def test_query_null_session_id(self, async_client):
        """Test null session_id is treated as not provided."""
        response = await async_client.post(
            "/api/query",
            json={"query": "Test", "session_id": None}
        )

        assert response.status_code == 200
        data = response.json()
        # Should create new session when session_id is null
        assert data["session_id"] == "test-session-123"


class TestResponseFormat:
    """Tests for response format and structure."""

    async def test_query_response_content_type(self, async_client):
        """Test query response has correct content type."""
        response = await async_client.post(
            "/api/query",
            json={"query": "Test"}
        )

        assert response.headers["content-type"] == "application/json"

    async def test_courses_response_content_type(self, async_client):
        """Test courses response has correct content type."""
        response = await async_client.get("/api/courses")

        assert response.headers["content-type"] == "application/json"

    async def test_error_response_format(self, async_client_error):
        """Test error responses follow FastAPI format."""
        response = await async_client_error.post(
            "/api/query",
            json={"query": "Will fail"}
        )

        assert response.status_code == 500
        data = response.json()
        # FastAPI HTTPException format
        assert "detail" in data


class TestConcurrentRequests:
    """Tests for handling concurrent/sequential requests."""

    async def test_multiple_queries_sequential(self, async_client):
        """Test multiple sequential queries work correctly."""
        queries = [
            "What is Python?",
            "Explain machine learning",
            "How do databases work?"
        ]

        for query in queries:
            response = await async_client.post(
                "/api/query",
                json={"query": query}
            )
            assert response.status_code == 200

    async def test_mixed_endpoint_calls(self, async_client):
        """Test calling different endpoints in sequence."""
        # Get courses
        response1 = await async_client.get("/api/courses")
        assert response1.status_code == 200

        # Make query
        response2 = await async_client.post(
            "/api/query",
            json={"query": "Test query"}
        )
        assert response2.status_code == 200
        session_id = response2.json()["session_id"]

        # Clear session
        response3 = await async_client.delete(f"/api/session/{session_id}")
        assert response3.status_code == 200

        # Check root
        response4 = await async_client.get("/")
        assert response4.status_code == 200
