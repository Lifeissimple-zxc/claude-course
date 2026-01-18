# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

UIGen is an AI-powered React component generator with live preview. It uses Claude AI (via Anthropic SDK and Vercel AI SDK) to generate React components through a chat interface, displaying them in real-time without writing files to disk.

## Development Commands

### Setup
```bash
npm run setup  # Install dependencies, generate Prisma client, run migrations
```

### Development
```bash
npm run dev  # Start Next.js dev server with Turbopack
npm run dev:daemon  # Start dev server in background, logs to logs.txt
```

### Build and Deploy
```bash
npm run build  # Production build
npm start  # Start production server
```

### Testing and Quality
```bash
npm test  # Run Vitest tests
npm run lint  # Run ESLint
```

### Database
```bash
npx prisma generate  # Generate Prisma client (output: src/generated/prisma)
npx prisma migrate dev  # Run database migrations
npm run db:reset  # Reset database (WARNING: deletes all data)
```

## Architecture Overview

### Core System: Virtual File System

The application operates on a **virtual file system** that keeps generated code in memory rather than writing to disk. This is critical to understand:

- **VirtualFileSystem** (`src/lib/file-system.ts`): In-memory file system that supports all standard operations (create, read, update, delete, rename)
- Files are persisted to the database as JSON in the `Project.data` field
- The VFS is reconstructed on each request via `deserializeFromNodes()`

### AI Code Generation Flow

1. User sends chat message to `/api/chat/route.ts`
2. API route:
   - Adds system prompt from `src/lib/prompts/generation.ts`
   - Reconstructs VirtualFileSystem from serialized project data
   - Calls Vercel AI SDK's `streamText()` with Claude model
   - Provides two AI tools: `str_replace_editor` and `file_manager`
3. Claude uses tools to create/modify files in the virtual file system
4. On completion, updated VFS and messages are saved back to database

### AI Tools

The AI has access to these tools for code manipulation:

- **str_replace_editor** (`src/lib/tools/str-replace.ts`):
  - Commands: `view`, `create`, `str_replace`, `insert`
  - Operates on VirtualFileSystem
  - Pattern: exact string matching for replacements

- **file_manager** (`src/lib/tools/file-manager.ts`):
  - Commands: `rename`, `delete`
  - Handles file/directory operations in VFS

### Preview System

Generated code is previewed through client-side JSX transformation:

1. **JSX Transformer** (`src/lib/transform/jsx-transformer.ts`):
   - Uses Babel standalone to transform JSX/TSX to executable JavaScript
   - Creates browser-compatible import maps using blob URLs
   - Resolves imports: local files (from VFS), third-party packages (from esm.sh), React (from esm.sh)
   - Handles `@/` path alias (maps to VFS root)
   - Collects and injects CSS imports

2. **Preview HTML Generation** (`createPreviewHTML` function):
   - Creates standalone HTML with import maps
   - Includes Tailwind CSS CDN
   - Wraps app in React ErrorBoundary
   - Displays syntax errors in styled UI if transformation fails

### Authentication

- JWT-based sessions using `jose` library
- Session cookies: 7-day expiration, httpOnly, sameSite=lax
- Middleware (`src/middleware.ts`) protects `/api/projects` and `/api/filesystem` routes
- Anonymous users: can create projects but cannot persist them
- Registered users: projects saved to database with userId association

### Database Schema

Prisma with SQLite (Prisma client generated to `src/generated/prisma`):

- **User**: id, email, password (bcrypt), timestamps
- **Project**: id, name, userId (nullable for anonymous), messages (JSON), data (JSON serialized VFS), timestamps

### Mock Provider

When `ANTHROPIC_API_KEY` is not set, the app uses a **MockLanguageModel** (`src/lib/provider.ts`):
- Returns static component code (Counter, ContactForm, or Card)
- Simulates multi-step tool calling with delays for realistic streaming
- Limited to 4 steps to prevent repetition

### Component Architecture

- **Next.js 15** with App Router
- **UI Components**: Radix UI primitives in `src/components/ui/`
- **Feature Components**:
  - `src/components/chat/`: Chat interface
  - `src/components/preview/`: Live preview iframe
  - `src/components/editor/`: Code editor (Monaco)
  - `src/components/auth/`: Login/signup forms
- **Path Alias**: `@/` maps to `src/`

### State Management

- Chat state: Managed by Vercel AI SDK's `useChat` hook
- Project state: Loaded from database, synced on AI completion
- VFS state: Serialized/deserialized between client and server
- Anonymous work: Tracked via `src/lib/anon-work-tracker.ts`

## Key Implementation Details

### Working with the Virtual File System

When reading or modifying generated code:
- VFS paths start with `/` (e.g., `/App.jsx`, `/components/Button.tsx`)
- Files only exist in memory until persisted to database
- To view generated code, read from `Project.data` JSON field

### Path Resolution in Preview

The preview system resolves imports in this order:
1. Exact path match in import map
2. Path without extension (tries .jsx, .tsx, .js, .ts)
3. `@/` alias converted to `/` and searched
4. Third-party packages fetched from esm.sh
5. Missing imports get placeholder modules

### Adding New AI Tools

To add tools for Claude:
1. Create tool builder in `src/lib/tools/`
2. Accept `VirtualFileSystem` instance
3. Use Vercel AI SDK's `tool()` helper with Zod schema
4. Register in `/api/chat/route.ts` tools object

### Tailwind CSS

- Using Tailwind CSS v4
- Preview uses Tailwind CDN for simplicity
- Main app uses PostCSS with `@tailwindcss/postcss`

### Testing

Vitest with:
- React Testing Library
- jsdom environment
- Path aliases resolved via vite-tsconfig-paths
- Tests in `__tests__/` directories or `.test.ts` files
