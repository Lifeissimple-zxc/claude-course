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