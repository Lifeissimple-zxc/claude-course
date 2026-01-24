# Claude Course

This repo follows a course on Claude Code: [link](https://learn.deeplearning.ai/courses/claude-code-a-highly-agentic-coding-assistant).

## Notes and Learnings (DeepLearning Course)
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
- `claude --resume` can be used to continue with a prev. convo.
- Claude hooks provide a way to inject arbitrary logic into the Claude's workflow.
- Initial data analysis performed by claude can be a good idea.
- Exitting a conversation does not erase it's progress. Keep that in mind for cases where last-minute changes are required.

### Worktrees.
A worktree is a repo copy living on disk in a dedicated folder. We can have multiple worktrees for a single repo. This allows agents to edit files without conflicts in parallel. How do create:
- create a `.worktrees` folder in.
- run `git worktree add .worktrees/my_feature` to create worktree entitues in git.


## Notes and Learnings (Anthropic)
- First start of claude in a project should be the `init` command. What it does:
    - scans the codebase.
    - creates a summary.
    - writes the summary to the CLAUDE.md file.
    - The file is then included in every request.
- `CLAUDE.md` contents are included into EVERY REQUEST sent to Claude.
- When in chat mode, `#` adds a claude memory. This is useful when Claude makes the same mistake over and over again.
- Double `ESC` allows to enter the rewind mode and revisit the messages sent to Claude.
- `claude mcp add playwright npx @playwright/mcp@latest` installs playwright to enable claude to control browser.

### Hooks
- A hook is a custom piece of logic that can be injected into the Claude's workflow. The biggest examples are `PreToolUse` and `PostToolUse`.
- Hook locations
    - Global: `~/.claude/settings.json`.
    - Project: `.claude/settings.json`. (can be pushed to git)
    - Project (not committed): `.claude/settings.local.json`.
- `PreToolUse` can block tool usage. It's useful for preventing Claude from reading specific files (ie .env files).
- Hooks communicate with Claude using exit codes. Code `0` means that everything is good. `2` blocks the tool and sends feedback to Claude (stderror).
Config for a command preventing claude from reading stuff from .env.
```json
{
    "hooks": {
        "PreToolUse": [
            {
                "matcher": "Read|Grep",
                "hooks": [
                    {
                        "type": "command",
                        "command": "node myscript.js" // this script needs to parse the command claude is trying to execute
                    }
                ]
            }
        ]
    }
    // .....
}
```
myscript.js:
```js
async function main() {
  const chunks = [];
  for await (const chunk of process.stdin) {
    chunks.push(chunk);
  }
  
  const toolArgs = JSON.parse(Buffer.concat(chunks).toString());
  
  // Extract the file path Claude is trying to read
  const readPath = 
    toolArgs.tool_input?.file_path || toolArgs.tool_input?.path || "";
  
  // Check if Claude is trying to read the .env file
  if (readPath.includes('.env')) {
    console.error("You cannot read the .env file");
    process.exit(2); // this is how we block Claude from proceeding with the command!
  }
}

main()
```

