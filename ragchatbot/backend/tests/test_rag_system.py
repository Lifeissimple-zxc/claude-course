"""
Tests for rag_system.py - RAGSystem class.

These tests evaluate how the RAG system handles content-query related questions
and integrates all components together.
"""
import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add backend to path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))


class TestRAGSystemQuery:
    """Integration tests for RAGSystem.query() method."""

    @patch('rag_system.VectorStore')
    @patch('rag_system.AIGenerator')
    @patch('rag_system.ToolManager')
    @patch('rag_system.CourseSearchTool')
    @patch('rag_system.CourseOutlineTool')
    @patch('rag_system.SessionManager')
    def test_query_returns_response_and_sources(
        self,
        mock_session_manager_class,
        mock_outline_tool_class,
        mock_search_tool_class,
        mock_tool_manager_class,
        mock_ai_generator_class,
        mock_vector_store_class
    ):
        """Test full query flow returns response and sources."""
        # Setup mocks
        mock_ai_generator = Mock()
        mock_ai_generator.generate_response.return_value = "Python is a programming language."
        mock_ai_generator_class.return_value = mock_ai_generator

        mock_tool_manager = Mock()
        mock_tool_manager.get_tool_definitions.return_value = []
        mock_tool_manager.get_last_sources.return_value = [
            {"title": "Python Course", "link": "https://example.com"}
        ]
        mock_tool_manager_class.return_value = mock_tool_manager

        mock_session_manager = Mock()
        mock_session_manager.get_conversation_history.return_value = None
        mock_session_manager_class.return_value = mock_session_manager

        # Import and create RAGSystem
        from rag_system import RAGSystem
        with patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test_key'}):
            rag = RAGSystem.__new__(RAGSystem)
            rag.ai_generator = mock_ai_generator
            rag.tool_manager = mock_tool_manager
            rag.session_manager = mock_session_manager

            response, sources = rag.query("What is Python?", session_id="test_session")

        assert response == "Python is a programming language."
        assert len(sources) == 1
        assert sources[0]["title"] == "Python Course"

    @patch('rag_system.VectorStore')
    @patch('rag_system.AIGenerator')
    @patch('rag_system.ToolManager')
    @patch('rag_system.CourseSearchTool')
    @patch('rag_system.CourseOutlineTool')
    @patch('rag_system.SessionManager')
    def test_query_includes_conversation_history(
        self,
        mock_session_manager_class,
        mock_outline_tool_class,
        mock_search_tool_class,
        mock_tool_manager_class,
        mock_ai_generator_class,
        mock_vector_store_class
    ):
        """Test query includes conversation history when session exists."""
        mock_ai_generator = Mock()
        mock_ai_generator.generate_response.return_value = "Follow-up answer."
        mock_ai_generator_class.return_value = mock_ai_generator

        mock_tool_manager = Mock()
        mock_tool_manager.get_tool_definitions.return_value = []
        mock_tool_manager.get_last_sources.return_value = []
        mock_tool_manager_class.return_value = mock_tool_manager

        mock_session_manager = Mock()
        mock_session_manager.get_conversation_history.return_value = "User: Previous question\nAssistant: Previous answer"
        mock_session_manager_class.return_value = mock_session_manager

        from rag_system import RAGSystem
        with patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test_key'}):
            rag = RAGSystem.__new__(RAGSystem)
            rag.ai_generator = mock_ai_generator
            rag.tool_manager = mock_tool_manager
            rag.session_manager = mock_session_manager

            rag.query("Follow-up question", session_id="existing_session")

        # Verify get_conversation_history was called with session_id
        mock_session_manager.get_conversation_history.assert_called_once_with("existing_session")

        # Verify history was passed to generate_response
        call_kwargs = mock_ai_generator.generate_response.call_args[1]
        assert call_kwargs.get("conversation_history") == "User: Previous question\nAssistant: Previous answer"

    @patch('rag_system.VectorStore')
    @patch('rag_system.AIGenerator')
    @patch('rag_system.ToolManager')
    @patch('rag_system.CourseSearchTool')
    @patch('rag_system.CourseOutlineTool')
    @patch('rag_system.SessionManager')
    def test_query_resets_sources_after_retrieval(
        self,
        mock_session_manager_class,
        mock_outline_tool_class,
        mock_search_tool_class,
        mock_tool_manager_class,
        mock_ai_generator_class,
        mock_vector_store_class
    ):
        """Test sources are reset after being retrieved."""
        mock_ai_generator = Mock()
        mock_ai_generator.generate_response.return_value = "Answer"
        mock_ai_generator_class.return_value = mock_ai_generator

        mock_tool_manager = Mock()
        mock_tool_manager.get_tool_definitions.return_value = []
        mock_tool_manager.get_last_sources.return_value = []
        mock_tool_manager_class.return_value = mock_tool_manager

        mock_session_manager = Mock()
        mock_session_manager.get_conversation_history.return_value = None
        mock_session_manager_class.return_value = mock_session_manager

        from rag_system import RAGSystem
        with patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test_key'}):
            rag = RAGSystem.__new__(RAGSystem)
            rag.ai_generator = mock_ai_generator
            rag.tool_manager = mock_tool_manager
            rag.session_manager = mock_session_manager

            rag.query("Question", session_id="test")

        mock_tool_manager.reset_sources.assert_called_once()

    @patch('rag_system.VectorStore')
    @patch('rag_system.AIGenerator')
    @patch('rag_system.ToolManager')
    @patch('rag_system.CourseSearchTool')
    @patch('rag_system.CourseOutlineTool')
    @patch('rag_system.SessionManager')
    def test_query_handles_ai_generator_exception(
        self,
        mock_session_manager_class,
        mock_outline_tool_class,
        mock_search_tool_class,
        mock_tool_manager_class,
        mock_ai_generator_class,
        mock_vector_store_class
    ):
        """
        BUG DETECTOR: Test behavior when AI generator raises exception.

        This tests whether exceptions from ai_generator propagate up
        (they currently do, which causes "query failed").
        """
        mock_ai_generator = Mock()
        mock_ai_generator.generate_response.side_effect = Exception("API Error")
        mock_ai_generator_class.return_value = mock_ai_generator

        mock_tool_manager = Mock()
        mock_tool_manager.get_tool_definitions.return_value = []
        mock_tool_manager_class.return_value = mock_tool_manager

        mock_session_manager = Mock()
        mock_session_manager.get_conversation_history.return_value = None
        mock_session_manager_class.return_value = mock_session_manager

        from rag_system import RAGSystem
        with patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test_key'}):
            rag = RAGSystem.__new__(RAGSystem)
            rag.ai_generator = mock_ai_generator
            rag.tool_manager = mock_tool_manager
            rag.session_manager = mock_session_manager

            # Exception should propagate (current behavior)
            with pytest.raises(Exception, match="API Error"):
                rag.query("Question", session_id="test")


class TestRAGSystemToolIntegration:
    """Tests for RAG system tool integration."""

    @patch('rag_system.VectorStore')
    @patch('rag_system.AIGenerator')
    @patch('rag_system.ToolManager')
    @patch('rag_system.CourseSearchTool')
    @patch('rag_system.CourseOutlineTool')
    @patch('rag_system.SessionManager')
    def test_query_passes_tools_to_generator(
        self,
        mock_session_manager_class,
        mock_outline_tool_class,
        mock_search_tool_class,
        mock_tool_manager_class,
        mock_ai_generator_class,
        mock_vector_store_class
    ):
        """Test query passes tool definitions to AI generator."""
        mock_ai_generator = Mock()
        mock_ai_generator.generate_response.return_value = "Answer"
        mock_ai_generator_class.return_value = mock_ai_generator

        mock_tool_manager = Mock()
        tool_defs = [{"name": "search_course_content"}]
        mock_tool_manager.get_tool_definitions.return_value = tool_defs
        mock_tool_manager.get_last_sources.return_value = []
        mock_tool_manager_class.return_value = mock_tool_manager

        mock_session_manager = Mock()
        mock_session_manager.get_conversation_history.return_value = None
        mock_session_manager_class.return_value = mock_session_manager

        from rag_system import RAGSystem
        with patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test_key'}):
            rag = RAGSystem.__new__(RAGSystem)
            rag.ai_generator = mock_ai_generator
            rag.tool_manager = mock_tool_manager
            rag.session_manager = mock_session_manager

            rag.query("Search for Python", session_id="test")

        call_kwargs = mock_ai_generator.generate_response.call_args[1]
        assert call_kwargs["tools"] == tool_defs
        assert call_kwargs["tool_manager"] == mock_tool_manager


class TestRAGSystemSessionManagement:
    """Tests for session management in RAG system."""

    @patch('rag_system.VectorStore')
    @patch('rag_system.AIGenerator')
    @patch('rag_system.ToolManager')
    @patch('rag_system.CourseSearchTool')
    @patch('rag_system.CourseOutlineTool')
    @patch('rag_system.SessionManager')
    def test_query_updates_session_history(
        self,
        mock_session_manager_class,
        mock_outline_tool_class,
        mock_search_tool_class,
        mock_tool_manager_class,
        mock_ai_generator_class,
        mock_vector_store_class
    ):
        """Test query updates session history after response."""
        mock_ai_generator = Mock()
        mock_ai_generator.generate_response.return_value = "The answer is 42."
        mock_ai_generator_class.return_value = mock_ai_generator

        mock_tool_manager = Mock()
        mock_tool_manager.get_tool_definitions.return_value = []
        mock_tool_manager.get_last_sources.return_value = []
        mock_tool_manager_class.return_value = mock_tool_manager

        mock_session_manager = Mock()
        mock_session_manager.get_conversation_history.return_value = None
        mock_session_manager_class.return_value = mock_session_manager

        from rag_system import RAGSystem
        with patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test_key'}):
            rag = RAGSystem.__new__(RAGSystem)
            rag.ai_generator = mock_ai_generator
            rag.tool_manager = mock_tool_manager
            rag.session_manager = mock_session_manager

            rag.query("What is the answer?", session_id="test_session")

        # Verify session was updated with Q&A
        mock_session_manager.add_exchange.assert_called_once()
        call_args = mock_session_manager.add_exchange.call_args[0]
        assert call_args[0] == "test_session"
        assert "What is the answer?" in call_args[1]
        assert "The answer is 42." in call_args[2]


class TestRAGSystemEdgeCases:
    """Edge case tests for RAG system."""

    @patch('rag_system.VectorStore')
    @patch('rag_system.AIGenerator')
    @patch('rag_system.ToolManager')
    @patch('rag_system.CourseSearchTool')
    @patch('rag_system.CourseOutlineTool')
    @patch('rag_system.SessionManager')
    def test_query_without_session_id(
        self,
        mock_session_manager_class,
        mock_outline_tool_class,
        mock_search_tool_class,
        mock_tool_manager_class,
        mock_ai_generator_class,
        mock_vector_store_class
    ):
        """Test query works without session ID (no history)."""
        mock_ai_generator = Mock()
        mock_ai_generator.generate_response.return_value = "Answer"
        mock_ai_generator_class.return_value = mock_ai_generator

        mock_tool_manager = Mock()
        mock_tool_manager.get_tool_definitions.return_value = []
        mock_tool_manager.get_last_sources.return_value = []
        mock_tool_manager_class.return_value = mock_tool_manager

        mock_session_manager = Mock()
        mock_session_manager.get_conversation_history.return_value = None
        mock_session_manager_class.return_value = mock_session_manager

        from rag_system import RAGSystem
        with patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test_key'}):
            rag = RAGSystem.__new__(RAGSystem)
            rag.ai_generator = mock_ai_generator
            rag.tool_manager = mock_tool_manager
            rag.session_manager = mock_session_manager

            response, sources = rag.query("Question", session_id=None)

        assert response == "Answer"
        # Should not call add_exchange when no session_id
        # (depending on implementation)

    @patch('rag_system.VectorStore')
    @patch('rag_system.AIGenerator')
    @patch('rag_system.ToolManager')
    @patch('rag_system.CourseSearchTool')
    @patch('rag_system.CourseOutlineTool')
    @patch('rag_system.SessionManager')
    def test_query_with_empty_response(
        self,
        mock_session_manager_class,
        mock_outline_tool_class,
        mock_search_tool_class,
        mock_tool_manager_class,
        mock_ai_generator_class,
        mock_vector_store_class
    ):
        """Test handling of empty AI response."""
        mock_ai_generator = Mock()
        mock_ai_generator.generate_response.return_value = ""
        mock_ai_generator_class.return_value = mock_ai_generator

        mock_tool_manager = Mock()
        mock_tool_manager.get_tool_definitions.return_value = []
        mock_tool_manager.get_last_sources.return_value = []
        mock_tool_manager_class.return_value = mock_tool_manager

        mock_session_manager = Mock()
        mock_session_manager.get_conversation_history.return_value = None
        mock_session_manager_class.return_value = mock_session_manager

        from rag_system import RAGSystem
        with patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test_key'}):
            rag = RAGSystem.__new__(RAGSystem)
            rag.ai_generator = mock_ai_generator
            rag.tool_manager = mock_tool_manager
            rag.session_manager = mock_session_manager

            response, sources = rag.query("Question", session_id="test")

        # Should return empty string, not crash
        assert response == ""
