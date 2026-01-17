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
