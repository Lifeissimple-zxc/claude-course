"""
Tests for ai_generator.py - AIGenerator class.

These tests evaluate if AIGenerator correctly calls CourseSearchTool
and handles tool execution properly.
"""
import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add backend to path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from ai_generator import AIGenerator


class TestAIGeneratorInit:
    """Tests for AIGenerator initialization."""

    @patch('ai_generator.anthropic.Anthropic')
    def test_init_creates_client(self, mock_anthropic_class):
        """Test AIGenerator creates Anthropic client."""
        generator = AIGenerator(api_key="test_key", model="claude-3-sonnet")

        mock_anthropic_class.assert_called_once_with(api_key="test_key")

    @patch('ai_generator.anthropic.Anthropic')
    def test_init_stores_model(self, mock_anthropic_class):
        """Test AIGenerator stores model name."""
        generator = AIGenerator(api_key="test_key", model="claude-3-sonnet")

        assert generator.model == "claude-3-sonnet"


class TestAIGeneratorGenerateResponse:
    """Tests for AIGenerator.generate_response() method."""

    @patch('ai_generator.anthropic.Anthropic')
    def test_generate_direct_response(self, mock_anthropic_class, mock_anthropic_response_text):
        """Test returns text when Claude gives direct answer (no tools)."""
        mock_client = Mock()
        mock_client.messages.create.return_value = mock_anthropic_response_text
        mock_anthropic_class.return_value = mock_client

        generator = AIGenerator(api_key="test_key", model="claude-3-sonnet")
        result = generator.generate_response("What is Python?")

        assert result == "This is a direct answer about Python programming."
        mock_client.messages.create.assert_called_once()

    @patch('ai_generator.anthropic.Anthropic')
    def test_generate_includes_system_prompt(self, mock_anthropic_class, mock_anthropic_response_text):
        """Test generate_response includes system prompt."""
        mock_client = Mock()
        mock_client.messages.create.return_value = mock_anthropic_response_text
        mock_anthropic_class.return_value = mock_client

        generator = AIGenerator(api_key="test_key", model="claude-3-sonnet")
        generator.generate_response("Test query")

        call_kwargs = mock_client.messages.create.call_args[1]
        assert "system" in call_kwargs
        assert "course materials" in call_kwargs["system"].lower()

    @patch('ai_generator.anthropic.Anthropic')
    def test_generate_includes_conversation_history(self, mock_anthropic_class, mock_anthropic_response_text):
        """Test generate_response includes conversation history when provided."""
        mock_client = Mock()
        mock_client.messages.create.return_value = mock_anthropic_response_text
        mock_anthropic_class.return_value = mock_client

        generator = AIGenerator(api_key="test_key", model="claude-3-sonnet")
        generator.generate_response(
            "Follow-up question",
            conversation_history="User: Hi\nAssistant: Hello!"
        )

        call_kwargs = mock_client.messages.create.call_args[1]
        assert "Previous conversation" in call_kwargs["system"]
        assert "User: Hi" in call_kwargs["system"]

    @patch('ai_generator.anthropic.Anthropic')
    def test_generate_includes_tools_when_provided(self, mock_anthropic_class, mock_anthropic_response_text):
        """Test generate_response includes tools when provided."""
        mock_client = Mock()
        mock_client.messages.create.return_value = mock_anthropic_response_text
        mock_anthropic_class.return_value = mock_client

        tools = [{"name": "test_tool", "description": "Test"}]

        generator = AIGenerator(api_key="test_key", model="claude-3-sonnet")
        generator.generate_response("Query", tools=tools)

        call_kwargs = mock_client.messages.create.call_args[1]
        assert call_kwargs["tools"] == tools
        assert call_kwargs["tool_choice"] == {"type": "auto"}

    @patch('ai_generator.anthropic.Anthropic')
    def test_generate_with_tool_use_calls_tool_manager(
        self,
        mock_anthropic_class,
        mock_anthropic_response_tool_use,
        mock_anthropic_response_final,
        mock_tool_manager
    ):
        """Test handles tool_use stop_reason correctly."""
        mock_client = Mock()
        # First call returns tool_use, second returns final response
        mock_client.messages.create.side_effect = [
            mock_anthropic_response_tool_use,
            mock_anthropic_response_final
        ]
        mock_anthropic_class.return_value = mock_client

        tools = [{"name": "search_course_content", "description": "Search"}]

        generator = AIGenerator(api_key="test_key", model="claude-3-sonnet")
        result = generator.generate_response(
            "Search for Python",
            tools=tools,
            tool_manager=mock_tool_manager
        )

        # Verify tool was executed
        mock_tool_manager.execute_tool.assert_called_once_with(
            "search_course_content",
            query="Python basics",
            course_name=None,
            lesson_number=None
        )

        # Verify final response returned
        assert "Based on the course content" in result

    @patch('ai_generator.anthropic.Anthropic')
    def test_generate_without_tool_manager_returns_direct(
        self,
        mock_anthropic_class
    ):
        """Test handles tool_use when tool_manager is None - falls back to content[0].text."""
        # Create a tool_use response without .text attribute on first content block
        tool_use_response = Mock()
        tool_use_response.stop_reason = "tool_use"

        tool_block = Mock(spec=['type', 'name', 'id', 'input'])  # No 'text' attribute
        tool_block.type = "tool_use"
        tool_block.name = "search_course_content"
        tool_use_response.content = [tool_block]

        mock_client = Mock()
        mock_client.messages.create.return_value = tool_use_response
        mock_anthropic_class.return_value = mock_client

        generator = AIGenerator(api_key="test_key", model="claude-3-sonnet")

        # Without tool_manager, code tries response.content[0].text which doesn't exist
        with pytest.raises(AttributeError):
            generator.generate_response("Search for Python", tools=[])


class TestAIGeneratorToolExecution:
    """Tests for AIGenerator._handle_tool_execution() method."""

    @patch('ai_generator.anthropic.Anthropic')
    def test_tool_execution_success(
        self,
        mock_anthropic_class,
        mock_anthropic_response_tool_use,
        mock_anthropic_response_final,
        mock_tool_manager
    ):
        """Test successful tool execution flow."""
        mock_client = Mock()
        mock_client.messages.create.side_effect = [
            mock_anthropic_response_tool_use,
            mock_anthropic_response_final
        ]
        mock_anthropic_class.return_value = mock_client

        generator = AIGenerator(api_key="test_key", model="claude-3-sonnet")
        result = generator.generate_response(
            "Query",
            tools=[{"name": "search_course_content"}],
            tool_manager=mock_tool_manager
        )

        # Should return final response text
        assert "Based on the course content" in result

    @patch('ai_generator.anthropic.Anthropic')
    def test_tool_execution_error_string_handled(
        self,
        mock_anthropic_class,
        mock_anthropic_response_tool_use,
        mock_anthropic_response_final,
        mock_tool_manager_error
    ):
        """Test when tool returns error string, flow continues."""
        mock_client = Mock()
        mock_client.messages.create.side_effect = [
            mock_anthropic_response_tool_use,
            mock_anthropic_response_final
        ]
        mock_anthropic_class.return_value = mock_client

        generator = AIGenerator(api_key="test_key", model="claude-3-sonnet")
        result = generator.generate_response(
            "Query",
            tools=[{"name": "search_course_content"}],
            tool_manager=mock_tool_manager_error
        )

        # Should still return final response (Claude handles error message)
        assert result is not None

    @patch('ai_generator.anthropic.Anthropic')
    def test_tool_execution_exception_handled(
        self,
        mock_anthropic_class,
        mock_anthropic_response_tool_use,
        mock_anthropic_response_final,
        mock_tool_manager_exception
    ):
        """
        Test that tool exceptions are caught and handled gracefully.

        After the fix, exceptions from tool execution are caught in
        _handle_tool_execution() and returned as error strings to Claude,
        preventing "query failed" errors.
        """
        mock_client = Mock()
        # First call returns tool_use, second returns final response
        mock_client.messages.create.side_effect = [
            mock_anthropic_response_tool_use,
            mock_anthropic_response_final
        ]
        mock_anthropic_class.return_value = mock_client

        generator = AIGenerator(api_key="test_key", model="claude-3-sonnet")

        # After fix: exception is caught and handled - no longer raises
        result = generator.generate_response(
            "Query",
            tools=[{"name": "search_course_content"}],
            tool_manager=mock_tool_manager_exception
        )

        # Should return final response without raising
        assert "Based on the course content" in result

        # Verify the error was passed to Claude as tool result
        second_call = mock_client.messages.create.call_args_list[1]
        messages = second_call[1]["messages"]
        tool_result_msg = messages[2]["content"][0]
        assert "Error executing tool" in tool_result_msg["content"]

    @patch('ai_generator.anthropic.Anthropic')
    def test_tool_execution_builds_correct_messages(
        self,
        mock_anthropic_class,
        mock_anthropic_response_tool_use,
        mock_anthropic_response_final,
        mock_tool_manager
    ):
        """Test _handle_tool_execution builds correct message structure."""
        mock_client = Mock()
        mock_client.messages.create.side_effect = [
            mock_anthropic_response_tool_use,
            mock_anthropic_response_final
        ]
        mock_anthropic_class.return_value = mock_client

        generator = AIGenerator(api_key="test_key", model="claude-3-sonnet")
        generator.generate_response(
            "Query",
            tools=[{"name": "search_course_content"}],
            tool_manager=mock_tool_manager
        )

        # Check second API call (final response)
        final_call = mock_client.messages.create.call_args_list[1]
        final_kwargs = final_call[1]

        # Should have 3 messages: user, assistant (tool_use), user (tool_result)
        messages = final_kwargs["messages"]
        assert len(messages) == 3
        assert messages[0]["role"] == "user"
        assert messages[1]["role"] == "assistant"
        assert messages[2]["role"] == "user"

        # Tool result should be in last message
        tool_results = messages[2]["content"]
        assert tool_results[0]["type"] == "tool_result"
        assert tool_results[0]["tool_use_id"] == "tool_call_123"


class TestAIGeneratorMultipleToolCalls:
    """Tests for handling multiple tool calls in single response."""

    @patch('ai_generator.anthropic.Anthropic')
    def test_multiple_tool_calls_executed(
        self,
        mock_anthropic_class,
        mock_anthropic_response_final,
        mock_tool_manager
    ):
        """Test handling multiple tool_use blocks."""
        # Create response with multiple tool calls
        multi_tool_response = Mock()
        multi_tool_response.stop_reason = "tool_use"

        tool1 = Mock()
        tool1.type = "tool_use"
        tool1.name = "search_course_content"
        tool1.id = "tool_1"
        tool1.input = {"query": "Python"}

        tool2 = Mock()
        tool2.type = "tool_use"
        tool2.name = "get_course_outline"
        tool2.id = "tool_2"
        tool2.input = {"course_name": "Python 101"}

        multi_tool_response.content = [tool1, tool2]

        mock_client = Mock()
        mock_client.messages.create.side_effect = [
            multi_tool_response,
            mock_anthropic_response_final
        ]
        mock_anthropic_class.return_value = mock_client

        generator = AIGenerator(api_key="test_key", model="claude-3-sonnet")
        generator.generate_response(
            "Query",
            tools=[],
            tool_manager=mock_tool_manager
        )

        # Both tools should be executed
        assert mock_tool_manager.execute_tool.call_count == 2


class TestAIGeneratorAPIParameters:
    """Tests for API parameter handling."""

    @patch('ai_generator.anthropic.Anthropic')
    def test_uses_configured_parameters(self, mock_anthropic_class, mock_anthropic_response_text):
        """Test uses correct base parameters."""
        mock_client = Mock()
        mock_client.messages.create.return_value = mock_anthropic_response_text
        mock_anthropic_class.return_value = mock_client

        generator = AIGenerator(api_key="test_key", model="claude-3-sonnet")
        generator.generate_response("Test")

        call_kwargs = mock_client.messages.create.call_args[1]
        assert call_kwargs["model"] == "claude-3-sonnet"
        assert call_kwargs["temperature"] == 0
        assert call_kwargs["max_tokens"] == 800


class TestAIGeneratorSequentialToolCalling:
    """Tests for sequential tool calling (up to 2 rounds)."""

    @patch('ai_generator.anthropic.Anthropic')
    def test_two_sequential_tool_calls_success(
        self,
        mock_anthropic_class,
        mock_anthropic_response_tool_use,
        mock_anthropic_response_tool_use_outline,
        mock_anthropic_response_final,
        mock_tool_manager_sequential
    ):
        """Test Claude can make two sequential tool calls."""
        mock_client = Mock()
        mock_client.messages.create.side_effect = [
            mock_anthropic_response_tool_use,         # Round 1: search
            mock_anthropic_response_tool_use_outline, # Round 2: outline
            mock_anthropic_response_final             # Final text response
        ]
        mock_anthropic_class.return_value = mock_client

        tools = [{"name": "search_course_content"}, {"name": "get_course_outline"}]

        generator = AIGenerator(api_key="test_key", model="claude-3-sonnet")
        result = generator.generate_response(
            "Compare Python basics with the course outline",
            tools=tools,
            tool_manager=mock_tool_manager_sequential
        )

        # Verify 3 API calls made
        assert mock_client.messages.create.call_count == 3

        # Verify both tools executed
        assert mock_tool_manager_sequential.execute_tool.call_count == 2

        # Verify final response returned
        assert "Based on the course content" in result

    @patch('ai_generator.anthropic.Anthropic')
    def test_terminates_after_max_rounds(
        self,
        mock_anthropic_class,
        mock_anthropic_response_tool_use,
        mock_anthropic_response_final,
        mock_tool_manager
    ):
        """Test loop terminates after max_tool_rounds even if Claude wants more tools."""
        mock_client = Mock()
        # Claude keeps requesting tools, but we force-stop after 2 rounds
        mock_client.messages.create.side_effect = [
            mock_anthropic_response_tool_use,  # Round 1
            mock_anthropic_response_tool_use,  # Round 2
            mock_anthropic_response_final      # Final (forced, no tools)
        ]
        mock_anthropic_class.return_value = mock_client

        generator = AIGenerator(api_key="test_key", model="claude-3-sonnet")
        result = generator.generate_response(
            "Query",
            tools=[{"name": "search_course_content"}],
            tool_manager=mock_tool_manager
        )

        # Verify exactly 3 API calls (2 tool rounds + 1 final)
        assert mock_client.messages.create.call_count == 3

        # Verify last call has NO tools parameter (forces text response)
        final_call = mock_client.messages.create.call_args_list[2]
        final_kwargs = final_call[1]
        assert "tools" not in final_kwargs

    @patch('ai_generator.anthropic.Anthropic')
    def test_early_termination_on_text_response(
        self,
        mock_anthropic_class,
        mock_anthropic_response_tool_use,
        mock_anthropic_response_final,
        mock_tool_manager
    ):
        """Test loop ends early when Claude returns text (no more tool calls needed)."""
        mock_client = Mock()
        # Claude uses one tool then returns text
        mock_client.messages.create.side_effect = [
            mock_anthropic_response_tool_use,
            mock_anthropic_response_final  # Text response, not tool_use
        ]
        mock_anthropic_class.return_value = mock_client

        generator = AIGenerator(api_key="test_key", model="claude-3-sonnet")
        result = generator.generate_response(
            "Query",
            tools=[{"name": "search_course_content"}],
            tool_manager=mock_tool_manager
        )

        # Verify only 2 API calls (1 tool round + early exit)
        assert mock_client.messages.create.call_count == 2

        # Verify only 1 tool execution
        assert mock_tool_manager.execute_tool.call_count == 1

    @patch('ai_generator.anthropic.Anthropic')
    def test_message_accumulation_across_rounds(
        self,
        mock_anthropic_class,
        mock_anthropic_response_tool_use,
        mock_anthropic_response_tool_use_outline,
        mock_anthropic_response_final,
        mock_tool_manager_sequential
    ):
        """Test messages accumulate correctly across tool rounds."""
        mock_client = Mock()
        captured_messages = []

        def capture_messages(**kwargs):
            # Capture a copy of messages at call time
            captured_messages.append([m.copy() if isinstance(m, dict) else m for m in kwargs["messages"]])
            responses = [
                mock_anthropic_response_tool_use,
                mock_anthropic_response_tool_use_outline,
                mock_anthropic_response_final
            ]
            return responses[len(captured_messages) - 1]

        mock_client.messages.create.side_effect = capture_messages
        mock_anthropic_class.return_value = mock_client

        generator = AIGenerator(api_key="test_key", model="claude-3-sonnet")
        generator.generate_response(
            "Original query",
            tools=[{"name": "search_course_content"}, {"name": "get_course_outline"}],
            tool_manager=mock_tool_manager_sequential
        )

        # Verify 3 API calls made
        assert len(captured_messages) == 3

        # First call: just the user query
        assert len(captured_messages[0]) == 1
        assert captured_messages[0][0]["role"] == "user"

        # Second call: user + assistant(tool_use) + user(tool_result)
        assert len(captured_messages[1]) == 3
        assert captured_messages[1][0]["role"] == "user"
        assert captured_messages[1][1]["role"] == "assistant"
        assert captured_messages[1][2]["role"] == "user"

        # Third call: 5 messages after 2 tool rounds
        assert len(captured_messages[2]) == 5
        assert captured_messages[2][0]["role"] == "user"
        assert captured_messages[2][1]["role"] == "assistant"
        assert captured_messages[2][2]["role"] == "user"
        assert captured_messages[2][3]["role"] == "assistant"
        assert captured_messages[2][4]["role"] == "user"

    @patch('ai_generator.anthropic.Anthropic')
    def test_tool_failure_continues_flow(
        self,
        mock_anthropic_class,
        mock_anthropic_response_tool_use,
        mock_anthropic_response_final,
        mock_tool_manager_exception
    ):
        """Test that tool failure doesn't break the chain - error passed to Claude."""
        mock_client = Mock()
        mock_client.messages.create.side_effect = [
            mock_anthropic_response_tool_use,
            mock_anthropic_response_final
        ]
        mock_anthropic_class.return_value = mock_client

        generator = AIGenerator(api_key="test_key", model="claude-3-sonnet")
        result = generator.generate_response(
            "Query",
            tools=[{"name": "search_course_content"}],
            tool_manager=mock_tool_manager_exception
        )

        # Should still return final response
        assert result is not None

        # Verify error message was sent as tool result
        second_call = mock_client.messages.create.call_args_list[1]
        messages = second_call[1]["messages"]
        tool_result_content = messages[2]["content"][0]["content"]
        assert "Error executing tool" in tool_result_content

    @patch('ai_generator.anthropic.Anthropic')
    def test_custom_max_rounds(
        self,
        mock_anthropic_class,
        mock_anthropic_response_tool_use,
        mock_anthropic_response_final,
        mock_tool_manager
    ):
        """Test max_tool_rounds parameter can be customized."""
        mock_client = Mock()
        mock_client.messages.create.side_effect = [
            mock_anthropic_response_tool_use,  # Round 1
            mock_anthropic_response_final      # Final (forced after 1 round)
        ]
        mock_anthropic_class.return_value = mock_client

        generator = AIGenerator(api_key="test_key", model="claude-3-sonnet")
        result = generator.generate_response(
            "Query",
            tools=[{"name": "search_course_content"}],
            tool_manager=mock_tool_manager,
            max_tool_rounds=1  # Only allow 1 round
        )

        # Verify exactly 2 API calls (1 tool round + 1 final)
        assert mock_client.messages.create.call_count == 2

        # Verify final call has no tools
        final_call = mock_client.messages.create.call_args_list[1]
        assert "tools" not in final_call[1]
