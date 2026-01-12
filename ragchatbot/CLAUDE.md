# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Build & Run Commands

**Listen to me. You use `uv` for everything - running Python, installing packages, all of it. You touch `pip` or bare `python`, we're gonna have a problem. Capisce?**

```bash
# Start the server (from ragchatbot/ directory)
./run.sh

# Or manually
cd backend && uv run uvicorn app:app --reload --port 8000

# Install dependencies
uv sync

# Run any Python script
uv run python script.py
```

The app runs at http://localhost:8000. Requires `ANTHROPIC_API_KEY` in `backend/.env`.

## Architecture

This is a RAG (Retrieval-Augmented Generation) system with a FastAPI backend and vanilla JS frontend.

### Request Flow

```
User Query → Frontend (script.js)
           → FastAPI (app.py) POST /api/query
           → RAGSystem (rag_system.py) orchestrates
           → AIGenerator (ai_generator.py) calls Claude API
           → Claude decides to use search tool
           → ToolManager (search_tools.py) executes tool
           → CourseSearchTool → VectorStore (vector_store.py)
           → ChromaDB performs semantic search
           → Results bubble back up
```

### Key Components

**backend/rag_system.py** - Main orchestrator. Coordinates document processing, vector storage, AI generation, and session management. Entry point for all queries.

**backend/ai_generator.py** - Claude API client with tool-calling loop. Sends query to Claude, handles `tool_use` responses, executes tools via ToolManager, sends results back to Claude for final answer.

**backend/vector_store.py** - ChromaDB wrapper. Manages two collections:
- `course_catalog`: Course metadata (titles, instructors)
- `course_content`: Text chunks with embeddings

**backend/search_tools.py** - Tool definitions for Claude. `CourseSearchTool` implements the `search_course_content` tool that Claude can invoke. `ToolManager` routes tool calls.

**backend/document_processor.py** - Parses course text files, extracts metadata from headers, chunks content into ~800 char segments with overlap.

### Data Storage

ChromaDB runs embedded (no separate server) using `PersistentClient`. Data stored in `backend/chroma_db/`:
- SQLite for metadata/IDs
- Parquet files for vector embeddings

Embedding model: `all-MiniLM-L6-v2` (384 dimensions)

### Frontend

Vanilla JS in `frontend/`. Calls `/api/query` with `{query, session_id}`, renders markdown responses with `marked.js`, displays sources in collapsible details.

## Configuration

All settings in `backend/config.py`:
- `CHUNK_SIZE`: 800 chars
- `CHUNK_OVERLAP`: 100 chars
- `MAX_RESULTS`: 5 search results
- `MAX_HISTORY`: 2 conversation exchanges
- `ANTHROPIC_MODEL`: claude-sonnet-4-20250514
