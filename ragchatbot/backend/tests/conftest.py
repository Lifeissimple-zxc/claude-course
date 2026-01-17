"""
Shared fixtures for RAG chatbot backend tests.
"""
import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch
from dataclasses import dataclass
from typing import List, Dict, Any, Optional

# Add backend to path for imports
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from vector_store import SearchResults


# ===== API Test Fixtures =====

@pytest.fixture
def mock_rag_system():
    """Mock RAGSystem for API testing."""
    mock = Mock()
    mock.query.return_value = (
        "This is a test answer about Python programming.",
        [{"title": "Python Course - Lesson 1", "link": "https://example.com/python/1"}]
    )
    mock.get_course_analytics.return_value = {
        "total_courses": 3,
        "course_titles": ["Python Basics", "Advanced Python", "Data Science"]
    }
    mock.session_manager = Mock()
    mock.session_manager.create_session.return_value = "test-session-123"
    mock.session_manager.clear_session.return_value = None
    return mock


@pytest.fixture
def mock_rag_system_empty():
    """Mock RAGSystem that returns empty results."""
    mock = Mock()
    mock.query.return_value = ("No information found.", [])
    mock.get_course_analytics.return_value = {
        "total_courses": 0,
        "course_titles": []
    }
    mock.session_manager = Mock()
    mock.session_manager.create_session.return_value = "empty-session-456"
    return mock


@pytest.fixture
def mock_rag_system_error():
    """Mock RAGSystem that raises exceptions."""
    mock = Mock()
    mock.query.side_effect = Exception("RAG system error: database unavailable")
    mock.get_course_analytics.side_effect = Exception("Analytics error")
    mock.session_manager = Mock()
    mock.session_manager.clear_session.side_effect = Exception("Session not found")
    return mock


@pytest.fixture
def test_app(mock_rag_system):
    """
    Create a test FastAPI app without static file mounting.

    This avoids the issue of static files not existing in the test environment
    by creating the API endpoints inline without importing from app.py.
    """
    from fastapi import FastAPI, HTTPException
    from pydantic import BaseModel
    from typing import List, Optional

    app = FastAPI(title="Test Course Materials RAG System")

    # Pydantic models matching app.py
    class QueryRequest(BaseModel):
        query: str
        session_id: Optional[str] = None

    class Source(BaseModel):
        title: str
        link: Optional[str] = None

    class QueryResponse(BaseModel):
        answer: str
        sources: List[Source]
        session_id: str

    class CourseStats(BaseModel):
        total_courses: int
        course_titles: List[str]

    # Use the mock_rag_system fixture
    rag_system = mock_rag_system

    @app.post("/api/query", response_model=QueryResponse)
    async def query_documents(request: QueryRequest):
        try:
            session_id = request.session_id
            if not session_id:
                session_id = rag_system.session_manager.create_session()

            answer, sources = rag_system.query(request.query, session_id)

            return QueryResponse(
                answer=answer,
                sources=sources,
                session_id=session_id
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/api/courses", response_model=CourseStats)
    async def get_course_stats():
        try:
            analytics = rag_system.get_course_analytics()
            return CourseStats(
                total_courses=analytics["total_courses"],
                course_titles=analytics["course_titles"]
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.delete("/api/session/{session_id}")
    async def clear_session(session_id: str):
        try:
            rag_system.session_manager.clear_session(session_id)
            return {"status": "cleared", "session_id": session_id}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/")
    async def root():
        return {"status": "ok", "message": "RAG API is running"}

    return app


@pytest.fixture
def test_app_error(mock_rag_system_error):
    """Test app configured with error-throwing RAG system."""
    from fastapi import FastAPI, HTTPException
    from pydantic import BaseModel
    from typing import List, Optional

    app = FastAPI(title="Test Course Materials RAG System - Error Mode")

    class QueryRequest(BaseModel):
        query: str
        session_id: Optional[str] = None

    class Source(BaseModel):
        title: str
        link: Optional[str] = None

    class QueryResponse(BaseModel):
        answer: str
        sources: List[Source]
        session_id: str

    class CourseStats(BaseModel):
        total_courses: int
        course_titles: List[str]

    rag_system = mock_rag_system_error

    @app.post("/api/query", response_model=QueryResponse)
    async def query_documents(request: QueryRequest):
        try:
            session_id = request.session_id or "default"
            answer, sources = rag_system.query(request.query, session_id)
            return QueryResponse(answer=answer, sources=sources, session_id=session_id)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/api/courses", response_model=CourseStats)
    async def get_course_stats():
        try:
            analytics = rag_system.get_course_analytics()
            return CourseStats(
                total_courses=analytics["total_courses"],
                course_titles=analytics["course_titles"]
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.delete("/api/session/{session_id}")
    async def clear_session(session_id: str):
        try:
            rag_system.session_manager.clear_session(session_id)
            return {"status": "cleared", "session_id": session_id}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    return app


@pytest.fixture
async def async_client(test_app):
    """Async HTTP client for testing FastAPI endpoints."""
    from httpx import AsyncClient, ASGITransport

    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.fixture
async def async_client_error(test_app_error):
    """Async HTTP client configured with error-throwing RAG system."""
    from httpx import AsyncClient, ASGITransport

    transport = ASGITransport(app=test_app_error)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


# ===== Sample Data Fixtures =====

@pytest.fixture
def sample_search_results():
    """Valid SearchResults with documents for testing."""
    return SearchResults(
        documents=["Sample content about Python programming basics."],
        metadata=[{
            "course_title": "Introduction to Python",
            "lesson_number": 1,
            "chunk_index": 0
        }],
        distances=[0.15]
    )


@pytest.fixture
def multi_result_search_results():
    """SearchResults with multiple documents."""
    return SearchResults(
        documents=[
            "First chunk about Python variables.",
            "Second chunk about Python functions.",
            "Third chunk about Python classes."
        ],
        metadata=[
            {"course_title": "Introduction to Python", "lesson_number": 1, "chunk_index": 0},
            {"course_title": "Introduction to Python", "lesson_number": 2, "chunk_index": 1},
            {"course_title": "Advanced Python", "lesson_number": 1, "chunk_index": 0}
        ],
        distances=[0.1, 0.2, 0.3]
    )


@pytest.fixture
def empty_search_results():
    """Empty SearchResults (no documents found)."""
    return SearchResults(
        documents=[],
        metadata=[],
        distances=[]
    )


@pytest.fixture
def error_search_results():
    """SearchResults with error message."""
    return SearchResults.empty("No course found matching 'NonExistent'")


# ===== Mock VectorStore Fixtures =====

@pytest.fixture
def mock_vector_store(sample_search_results):
    """Mock VectorStore with successful search behavior."""
    mock = Mock()
    mock.search.return_value = sample_search_results
    mock.get_lesson_link.return_value = "https://example.com/course/lesson/1"
    mock.get_course_link.return_value = "https://example.com/course"
    mock._resolve_course_name.return_value = "Introduction to Python"

    # Mock course_catalog for CourseOutlineTool
    mock.course_catalog = Mock()
    mock.course_catalog.get.return_value = {
        'metadatas': [{
            'title': 'Introduction to Python',
            'course_link': 'https://example.com/course',
            'lessons_json': '[{"lesson_number": 1, "lesson_title": "Basics", "lesson_link": "https://example.com/course/1"}]'
        }]
    }

    return mock


@pytest.fixture
def mock_vector_store_empty(empty_search_results):
    """Mock VectorStore that returns empty results."""
    mock = Mock()
    mock.search.return_value = empty_search_results
    mock.get_lesson_link.return_value = None
    mock.get_course_link.return_value = None
    return mock


@pytest.fixture
def mock_vector_store_error(error_search_results):
    """Mock VectorStore that returns error results."""
    mock = Mock()
    mock.search.return_value = error_search_results
    return mock


@pytest.fixture
def mock_vector_store_exception():
    """Mock VectorStore that raises exceptions."""
    mock = Mock()
    mock.search.side_effect = Exception("Database connection failed")
    return mock


# ===== Mock Anthropic Response Fixtures =====

@pytest.fixture
def mock_anthropic_response_text():
    """Mock Claude response with direct text (no tool use)."""
    response = Mock()
    response.stop_reason = "end_turn"

    text_block = Mock()
    text_block.type = "text"
    text_block.text = "This is a direct answer about Python programming."

    response.content = [text_block]
    return response


@pytest.fixture
def mock_anthropic_response_tool_use():
    """Mock Claude response requesting tool use."""
    response = Mock()
    response.stop_reason = "tool_use"

    tool_block = Mock()
    tool_block.type = "tool_use"
    tool_block.name = "search_course_content"
    tool_block.id = "tool_call_123"
    tool_block.input = {"query": "Python basics", "course_name": None, "lesson_number": None}

    response.content = [tool_block]
    return response


@pytest.fixture
def mock_anthropic_response_final():
    """Mock Claude final response after tool execution."""
    response = Mock()
    response.stop_reason = "end_turn"

    text_block = Mock()
    text_block.type = "text"
    text_block.text = "Based on the course content, Python basics include variables and functions."

    response.content = [text_block]
    return response


# ===== Mock Anthropic Client Fixtures =====

@pytest.fixture
def mock_anthropic_client(mock_anthropic_response_text):
    """Mock Anthropic client that returns direct text response."""
    mock_client = Mock()
    mock_client.messages.create.return_value = mock_anthropic_response_text
    return mock_client


@pytest.fixture
def mock_anthropic_client_tool_use(mock_anthropic_response_tool_use, mock_anthropic_response_final):
    """Mock Anthropic client that simulates tool use flow."""
    mock_client = Mock()
    # First call returns tool_use, second call returns final text
    mock_client.messages.create.side_effect = [
        mock_anthropic_response_tool_use,
        mock_anthropic_response_final
    ]
    return mock_client


# ===== Mock ToolManager Fixtures =====

@pytest.fixture
def mock_tool_manager():
    """Mock ToolManager with successful execution."""
    mock = Mock()
    mock.execute_tool.return_value = "[Introduction to Python - Lesson 1]\nPython basics content here."
    mock.get_tool_definitions.return_value = [
        {
            "name": "search_course_content",
            "description": "Search course materials",
            "input_schema": {"type": "object", "properties": {"query": {"type": "string"}}}
        }
    ]
    mock.get_last_sources.return_value = [
        {"title": "Introduction to Python - Lesson 1", "link": "https://example.com/course/1"}
    ]
    mock.reset_sources.return_value = None
    return mock


@pytest.fixture
def mock_tool_manager_error():
    """Mock ToolManager that returns error string."""
    mock = Mock()
    mock.execute_tool.return_value = "No relevant content found."
    mock.get_tool_definitions.return_value = []
    mock.get_last_sources.return_value = []
    return mock


@pytest.fixture
def mock_tool_manager_exception():
    """Mock ToolManager that raises exception - tests bug in ai_generator."""
    mock = Mock()
    mock.execute_tool.side_effect = Exception("Tool execution crashed!")
    mock.get_tool_definitions.return_value = []
    return mock


# ===== Sequential Tool Calling Fixtures =====

@pytest.fixture
def mock_anthropic_response_tool_use_outline():
    """Mock Claude response requesting get_course_outline tool (for second round)."""
    response = Mock()
    response.stop_reason = "tool_use"

    tool_block = Mock()
    tool_block.type = "tool_use"
    tool_block.name = "get_course_outline"
    tool_block.id = "tool_call_456"
    tool_block.input = {"course_name": "Introduction to Python"}

    response.content = [tool_block]
    return response


@pytest.fixture
def mock_tool_manager_sequential():
    """Mock ToolManager that returns different results for sequential calls."""
    mock = Mock()
    mock.execute_tool.side_effect = [
        "[Search Result] Python basics content about variables...",
        "[Outline Result] Course: Intro to Python\nLessons: 1. Basics, 2. Functions"
    ]
    mock.get_tool_definitions.return_value = [
        {"name": "search_course_content", "description": "Search course materials"},
        {"name": "get_course_outline", "description": "Get course structure"}
    ]
    mock.get_last_sources.return_value = []
    return mock


# ===== Helper Functions =====

def create_mock_tool_use_response(tool_name: str, tool_input: dict, tool_id: str = "tool_123"):
    """Helper to create mock tool_use response."""
    response = Mock()
    response.stop_reason = "tool_use"

    tool_block = Mock()
    tool_block.type = "tool_use"
    tool_block.name = tool_name
    tool_block.id = tool_id
    tool_block.input = tool_input

    response.content = [tool_block]
    return response
