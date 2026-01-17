Refactor @backend/ai_generator.py to support sequential tool calling where Claude can make up to 2 tools calls in separate API rounds.

Current behaviour:
- Claude makes 1 tool call -> tools are removed from API params -> final response.
- If Claude wants another tool call after seeing the results, it can't (gets an empty response).

Desired behaviour
- Each tool call should be a separate API request where Claude can REASON about previous results.
- Support for compex queries requiring multiple searches for comparisons, multi-part questions, or when information from different courses/lessons is needed.

Example flow:
1. User: "search for a course that discusses the same topic as lesson 4 of course X".
2. Claude: get course outline for course X -> get title of lesson 4.
3. Claude: uses the title to search for a course discussing the same topic -> returns course info.
4. Claude: provides complete answer.

Requirements
- Maximum 2 sequential rounds per user query.
- Terminate when: (a) 2 rounds completed, (b) Claude's response has no tool_use blocks or (c) tool call fails.
- Preserve conversation context between rounds.
- Handle tool execution errors gracefully.

Notes:
- update the system prompt in @backend/ai_generator.py
- update the test in @backend/test/test_ai_generator.py
- write tests that verify the external behaviour (API calls made, tools executed, results returned) rather than internal state details.

Use two parallel subagents to brainstorm possible plans. Do not implement any code.