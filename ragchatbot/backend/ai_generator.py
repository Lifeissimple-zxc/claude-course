import anthropic
from typing import List, Optional, Dict, Any

class AIGenerator:
    """Handles interactions with Anthropic's Claude API for generating responses"""
    
    # Static system prompt to avoid rebuilding on each call
    SYSTEM_PROMPT = """ You are an AI assistant specialized in course materials and educational content with access to tools for course information.

Tool Usage:
- **search_course_content**: Search course materials for specific content or detailed educational materials
- **get_course_outline**: Get course structure - use when users ask about:
  - What lessons are in a course
  - Course outline or structure
  - What topics a course covers
  - Links to specific lessons or courses
- **Up to 2 sequential tool calls per query**:
  - You may call a second tool after seeing the first result if needed
  - Example: Get course outline first, then search for specific content
  - Example: Search one course, then search another for comparison
- Synthesize tool results into accurate, fact-based responses
- If tool yields no results, state this clearly without offering alternatives

Response Protocol:
- **General knowledge questions**: Answer using existing knowledge without tools
- **Course-specific content questions**: Use search_course_content first
- **Course structure/outline questions**: Use get_course_outline first
- **No meta-commentary**:
 - Provide direct answers only — no reasoning process, search explanations, or question-type analysis
 - Do not mention "based on the search results" or "based on the outline"

When presenting course outlines, include:
- Course title and link
- All lesson numbers and titles with their links

All responses must be:
1. **Brief, Concise and focused** - Get to the point quickly
2. **Educational** - Maintain instructional value
3. **Clear** - Use accessible language
4. **Example-supported** - Include relevant examples when they aid understanding
Provide only the direct answer to what was asked.
"""
    
    def __init__(self, api_key: str, model: str):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model
        
        # Pre-build base API parameters
        self.base_params = {
            "model": self.model,
            "temperature": 0,
            "max_tokens": 800
        }
    
    def generate_response(self, query: str,
                         conversation_history: Optional[str] = None,
                         tools: Optional[List] = None,
                         tool_manager=None,
                         max_tool_rounds: int = 2) -> str:
        """
        Generate AI response with optional tool usage and conversation context.
        Supports up to max_tool_rounds sequential tool calls.

        Args:
            query: The user's question or request
            conversation_history: Previous messages for context
            tools: Available tools the AI can use
            tool_manager: Manager to execute tools
            max_tool_rounds: Maximum number of tool calling rounds (default: 2)

        Returns:
            Generated response as string
        """
        # Build system content efficiently
        system_content = (
            f"{self.SYSTEM_PROMPT}\n\nPrevious conversation:\n{conversation_history}"
            if conversation_history
            else self.SYSTEM_PROMPT
        )

        # Initialize messages with user query
        messages = [{"role": "user", "content": query}]

        round_count = 0

        while round_count < max_tool_rounds:
            # Prepare API call parameters with tools
            api_params = {
                **self.base_params,
                "messages": messages,
                "system": system_content
            }

            if tools:
                api_params["tools"] = tools
                api_params["tool_choice"] = {"type": "auto"}

            # Get response from Claude
            response = self.client.messages.create(**api_params)

            # Termination condition (b): No tool_use blocks
            if response.stop_reason != "tool_use":
                return response.content[0].text

            # No tool_manager to execute tools
            if not tool_manager:
                return response.content[0].text

            # Execute tools and accumulate messages
            tool_results = self._execute_tools(response, tool_manager)

            # Add assistant's tool use response and tool results to messages
            messages.append({"role": "assistant", "content": response.content})
            messages.append({"role": "user", "content": tool_results})

            round_count += 1

        # Termination condition (a): Max rounds reached
        # Make final call WITHOUT tools to force text response
        final_params = {
            **self.base_params,
            "messages": messages,
            "system": system_content
        }

        final_response = self.client.messages.create(**final_params)
        return final_response.content[0].text

    def _execute_tools(self, response, tool_manager) -> List[Dict[str, Any]]:
        """
        Execute all tool calls in a response and return results.

        Args:
            response: The response containing tool use requests
            tool_manager: Manager to execute tools

        Returns:
            List of tool result dictionaries
        """
        tool_results = []

        for content_block in response.content:
            if content_block.type == "tool_use":
                try:
                    tool_result = tool_manager.execute_tool(
                        content_block.name,
                        **content_block.input
                    )
                except Exception as e:
                    # Return error as tool result so Claude can handle gracefully
                    tool_result = f"Error executing tool '{content_block.name}': {str(e)}"

                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": content_block.id,
                    "content": tool_result
                })

        return tool_results