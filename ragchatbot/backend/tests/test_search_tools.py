"""
Tests for search_tools.py - CourseSearchTool, CourseOutlineTool, and ToolManager.

These tests evaluate the execute method in CourseSearchTool and tool management.
"""
import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch

# Add backend to path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from search_tools import CourseSearchTool, CourseOutlineTool, ToolManager, Tool
from vector_store import SearchResults


class TestCourseSearchToolExecute:
    """Tests for CourseSearchTool.execute() method."""

    def test_execute_successful_search(self, mock_vector_store, sample_search_results):
        """Test execute returns formatted results when search succeeds."""
        tool = CourseSearchTool(mock_vector_store)

        result = tool.execute(query="Python basics")

        # Verify search was called
        mock_vector_store.search.assert_called_once_with(
            query="Python basics",
            course_name=None,
            lesson_number=None
        )

        # Verify result contains course info
        assert "Introduction to Python" in result
        assert "Lesson 1" in result
        assert "Sample content about Python programming" in result

    def test_execute_with_error_in_results(self, mock_vector_store_error):
        """Test execute returns error message when SearchResults has error."""
        tool = CourseSearchTool(mock_vector_store_error)

        result = tool.execute(query="nonexistent topic")

        # Should return the error message from SearchResults
        assert "No course found matching" in result

    def test_execute_with_empty_results(self, mock_vector_store_empty):
        """Test execute returns 'no content found' for empty results."""
        tool = CourseSearchTool(mock_vector_store_empty)

        result = tool.execute(query="obscure topic")

        assert "No relevant content found" in result

    def test_execute_with_empty_results_and_filters(self, mock_vector_store_empty):
        """Test empty results message includes filter info."""
        tool = CourseSearchTool(mock_vector_store_empty)

        result = tool.execute(
            query="obscure topic",
            course_name="Python Course",
            lesson_number=5
        )

        assert "No relevant content found" in result
        assert "Python Course" in result
        assert "lesson 5" in result

    def test_execute_with_course_filter(self, mock_vector_store):
        """Test execute passes course_name filter to vector store."""
        tool = CourseSearchTool(mock_vector_store)

        tool.execute(query="variables", course_name="Python 101")

        mock_vector_store.search.assert_called_once_with(
            query="variables",
            course_name="Python 101",
            lesson_number=None
        )

    def test_execute_with_lesson_filter(self, mock_vector_store):
        """Test execute passes lesson_number filter to vector store."""
        tool = CourseSearchTool(mock_vector_store)

        tool.execute(query="functions", lesson_number=3)

        mock_vector_store.search.assert_called_once_with(
            query="functions",
            course_name=None,
            lesson_number=3
        )

    def test_execute_with_all_filters(self, mock_vector_store):
        """Test execute passes all filters to vector store."""
        tool = CourseSearchTool(mock_vector_store)

        tool.execute(query="classes", course_name="Advanced Python", lesson_number=2)

        mock_vector_store.search.assert_called_once_with(
            query="classes",
            course_name="Advanced Python",
            lesson_number=2
        )

    def test_execute_stores_sources(self, mock_vector_store, sample_search_results):
        """Test execute populates last_sources correctly."""
        tool = CourseSearchTool(mock_vector_store)

        # Initially empty
        assert tool.last_sources == []

        tool.execute(query="Python basics")

        # Should have sources after execution
        assert len(tool.last_sources) == 1
        assert tool.last_sources[0]["title"] == "Introduction to Python - Lesson 1"
        assert tool.last_sources[0]["link"] == "https://example.com/course/lesson/1"

    def test_execute_handles_none_lesson_link(self, mock_vector_store, sample_search_results):
        """Test execute handles None from get_lesson_link gracefully."""
        mock_vector_store.get_lesson_link.return_value = None
        tool = CourseSearchTool(mock_vector_store)

        result = tool.execute(query="Python basics")

        # Should not crash, source link should be None
        assert len(tool.last_sources) == 1
        assert tool.last_sources[0]["link"] is None

    def test_execute_uses_course_link_when_no_lesson(self, mock_vector_store):
        """Test uses course link when metadata has no lesson_number."""
        # Modify search results to have no lesson_number
        mock_vector_store.search.return_value = SearchResults(
            documents=["Content without lesson"],
            metadata=[{"course_title": "Standalone Course"}],  # No lesson_number
            distances=[0.1]
        )
        tool = CourseSearchTool(mock_vector_store)

        tool.execute(query="test")

        # Should call get_course_link instead of get_lesson_link
        mock_vector_store.get_course_link.assert_called_once_with("Standalone Course")

    def test_execute_multiple_results(self, mock_vector_store, multi_result_search_results):
        """Test execute formats multiple results correctly."""
        mock_vector_store.search.return_value = multi_result_search_results
        tool = CourseSearchTool(mock_vector_store)

        result = tool.execute(query="Python")

        # Should have all three results
        assert "Introduction to Python" in result
        assert "Advanced Python" in result
        assert len(tool.last_sources) == 3


class TestCourseSearchToolDefinition:
    """Tests for CourseSearchTool.get_tool_definition()."""

    def test_tool_definition_structure(self, mock_vector_store):
        """Test tool definition has correct structure."""
        tool = CourseSearchTool(mock_vector_store)
        definition = tool.get_tool_definition()

        assert definition["name"] == "search_course_content"
        assert "description" in definition
        assert "input_schema" in definition
        assert definition["input_schema"]["required"] == ["query"]

    def test_tool_definition_properties(self, mock_vector_store):
        """Test tool definition has all expected properties."""
        tool = CourseSearchTool(mock_vector_store)
        definition = tool.get_tool_definition()

        props = definition["input_schema"]["properties"]
        assert "query" in props
        assert "course_name" in props
        assert "lesson_number" in props


class TestCourseOutlineTool:
    """Tests for CourseOutlineTool.execute() method."""

    def test_execute_course_not_found(self, mock_vector_store):
        """Test returns error when course name doesn't resolve."""
        mock_vector_store._resolve_course_name.return_value = None
        tool = CourseOutlineTool(mock_vector_store)

        result = tool.execute(course_name="NonExistent Course")

        assert "No course found matching" in result
        assert "NonExistent Course" in result

    def test_execute_successful_outline(self, mock_vector_store):
        """Test returns formatted outline with lessons."""
        tool = CourseOutlineTool(mock_vector_store)

        result = tool.execute(course_name="Python")

        assert "Introduction to Python" in result
        assert "Basics" in result
        assert "https://example.com/course" in result

    def test_execute_stores_sources(self, mock_vector_store):
        """Test execute populates last_sources."""
        tool = CourseOutlineTool(mock_vector_store)

        tool.execute(course_name="Python")

        assert len(tool.last_sources) == 1
        assert tool.last_sources[0]["title"] == "Introduction to Python"

    def test_execute_metadata_retrieval_error(self, mock_vector_store):
        """Test handles metadata retrieval errors."""
        mock_vector_store.course_catalog.get.side_effect = Exception("DB Error")
        tool = CourseOutlineTool(mock_vector_store)

        result = tool.execute(course_name="Python")

        assert "Error retrieving course" in result


class TestToolManager:
    """Tests for ToolManager class."""

    def test_register_tool(self, mock_vector_store):
        """Test registering a tool."""
        manager = ToolManager()
        tool = CourseSearchTool(mock_vector_store)

        manager.register_tool(tool)

        assert "search_course_content" in manager.tools

    def test_register_tool_without_name_raises(self):
        """Test registering tool without name raises ValueError."""
        manager = ToolManager()

        mock_tool = Mock(spec=Tool)
        mock_tool.get_tool_definition.return_value = {}  # No name

        with pytest.raises(ValueError, match="must have a 'name'"):
            manager.register_tool(mock_tool)

    def test_get_tool_definitions(self, mock_vector_store):
        """Test getting all tool definitions."""
        manager = ToolManager()
        tool1 = CourseSearchTool(mock_vector_store)
        tool2 = CourseOutlineTool(mock_vector_store)

        manager.register_tool(tool1)
        manager.register_tool(tool2)

        definitions = manager.get_tool_definitions()

        assert len(definitions) == 2
        names = [d["name"] for d in definitions]
        assert "search_course_content" in names
        assert "get_course_outline" in names

    def test_execute_unknown_tool(self):
        """Test returns error for non-existent tool."""
        manager = ToolManager()

        result = manager.execute_tool("nonexistent_tool", query="test")

        assert "Tool 'nonexistent_tool' not found" in result

    def test_execute_tool_success(self, mock_vector_store):
        """Test successful tool execution."""
        manager = ToolManager()
        tool = CourseSearchTool(mock_vector_store)
        manager.register_tool(tool)

        result = manager.execute_tool("search_course_content", query="Python")

        assert "Introduction to Python" in result

    def test_execute_tool_exception_handled(self, mock_vector_store_exception):
        """
        Test that tool exceptions are caught and returned as error strings.

        After the fix, exceptions from tools are caught by ToolManager.execute_tool()
        and returned as error messages instead of propagating.
        """
        manager = ToolManager()
        tool = CourseSearchTool(mock_vector_store_exception)
        manager.register_tool(tool)

        # After fix: exceptions are caught and returned as error strings
        result = manager.execute_tool("search_course_content", query="test")
        assert "Tool execution error" in result
        assert "Database connection failed" in result

    def test_get_last_sources(self, mock_vector_store):
        """Test getting sources from last search."""
        manager = ToolManager()
        tool = CourseSearchTool(mock_vector_store)
        manager.register_tool(tool)

        manager.execute_tool("search_course_content", query="Python")
        sources = manager.get_last_sources()

        assert len(sources) == 1
        assert "Introduction to Python" in sources[0]["title"]

    def test_reset_sources(self, mock_vector_store):
        """Test resetting sources."""
        manager = ToolManager()
        tool = CourseSearchTool(mock_vector_store)
        manager.register_tool(tool)

        manager.execute_tool("search_course_content", query="Python")
        assert len(manager.get_last_sources()) == 1

        manager.reset_sources()
        assert len(manager.get_last_sources()) == 0


class TestToolManagerEdgeCases:
    """Edge case tests for ToolManager."""

    def test_execute_tool_with_wrong_kwargs(self, mock_vector_store):
        """Test tool execution with incorrect kwargs returns error string."""
        manager = ToolManager()
        tool = CourseSearchTool(mock_vector_store)
        manager.register_tool(tool)

        # Missing required 'query' parameter - now caught and returned as error
        result = manager.execute_tool("search_course_content", wrong_param="test")
        assert "Tool execution error" in result

    def test_multiple_tools_sources(self, mock_vector_store):
        """Test sources work correctly with multiple tools registered."""
        manager = ToolManager()
        search_tool = CourseSearchTool(mock_vector_store)
        outline_tool = CourseOutlineTool(mock_vector_store)

        manager.register_tool(search_tool)
        manager.register_tool(outline_tool)

        # Execute search tool
        manager.execute_tool("search_course_content", query="Python")
        sources = manager.get_last_sources()
        assert len(sources) > 0
