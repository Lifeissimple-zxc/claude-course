# Claude Course

This repo follows a course on Claude Code: [link](https://learn.deeplearning.ai/courses/claude-code-a-highly-agentic-coding-assistant).

## Notes and Learnings
- `claude.md` is a file with instructions loaded into the model's context automatically.
- Claude does not index the code, it uses tools to navigate it and the model to reason.
- `uv run` both installs deps and runs the application.
- `init` command creates a `clade.md`. The course recommends starting with it. This file is like long-term memory for Claude code. There are different flavours of these files:
    1. `CLAUDE.md`: shared config to be committed to the repo.
    2. `CLAUDE.local.md`: not shared with other eng, personal instructions and customizations for Claude. Location: project directory.
    3. `~/.claude/CLAUDE.md`: a global file, used by all projects. Instructions are thus global.
- `ide` command connects to vscode (experience then becomes similar to the extension?)
- `clear` prunes the convo history and frees context.
- the right context can make or break working with Claude.
    - files are mentioned with `@a`.
    - `shift + tab` to enter plan mode (works in both CLI and terminal).
- Claude supports screenshots. They can be added to context by copy pasting them to the terminal. Vs code extension does not support the shortcut.
- `claude mcp add` adds an MCP server.
- Plan mode is a read-only mode where Claude reads and "understands" things.
- `Think a lot` is a special instruction that makes Claude spend more tokens and evaluate the problem statement deeper (tbd if it indeed works).
- Spawning subagents is smart to get multiple approaches to solving a problem evaluated.
- Multiple Claude sessions can be started simultaneously. This requires git worktrees.
- Custom commands for claude can be added to the `.claude/commands` dir. Permissions are also stored in `.claude`.

### Worktrees.
A worktree is a repo copy living on disk in a dedicated folder. We can have multiple worktrees for a single repo. This allows agents to edit files without conflicts in parallel. How do create:
- create a `.worktrees` folder in.
- run `git worktree add .worktrees/my_feature` to create worktree entitues in git.
- `claude --resume` can be used to continue with a prev. convo.
- Claude hooks provide a way to inject arbitrary logic into the Claude's workflow.