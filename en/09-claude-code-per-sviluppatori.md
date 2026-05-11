# 9. Claude Code: Terminal-Based Agent for Developers

Claude Code is the product you're using now (probably). It's a **terminal-based AI agent** designed specifically for those who write code. For developers, it's currently one of the most productive tools on the market.

## 9.1 What Claude Code does

In one sentence: **a terminal-based agent that can read, modify and run code in your project, under your control**.

Unlike ChatGPT (chat) or GitHub Copilot (autocomplete), Claude Code:

- Has **real filesystem access** (reads and edits files in your repo).
- Can **execute shell commands** (test, build, git).
- Works in **autonomous loops**: you give a goal, it executes many steps, reports back to you.
- Asks for **confirmation** before potentially destructive actions.

Examples of prompts that work:

> "Find the bug where login fails with uppercase email and fix it, adding a test."

> "Refactor the `payments/` module to separate business logic from persistence."

> "Update dependencies to the next major, run tests, fix what breaks."

## 9.2 Installation and basic setup

```bash
# macOS / Linux
curl -fsSL https://claude.com/install.sh | sh

# or with npm
npm install -g @anthropic-ai/claude-code
```

Then in your project:

```bash
cd ~/my-project
claude
```

An interactive session opens. Write your prompt, press Enter, the agent works.

## 9.3 The CLAUDE.md file hierarchy

Claude Code automatically reads `CLAUDE.md` (and similar) files for persistent project instructions. Precedence order:

1. **`~/.claude/CLAUDE.md`** — global instructions (for all your projects).
2. **`<project>/CLAUDE.md`** — project instructions (versioned in git).
3. **`<project>/.claude/CLAUDE.local.md`** — your local instructions (gitignored).

What to put in:

```markdown
# Project conventions

- Stack: Python 3.12, FastAPI, PostgreSQL, pytest.
- Style: Black, isort, mandatory type hints.
- Tests: every new endpoint requires an integration test.

# Useful commands

- `make test` — runs unit + integration tests.
- `make lint` — runs black + ruff + mypy.
- `make migrate` — runs migrations.

# Things NOT to do

- Don't modify `legacy/` without asking.
- Don't add dependencies without evaluating alternatives.
```

The file is loaded at every startup. You save repeating the same context every session.

## 9.4 Slash commands

Commands starting with `/` for special actions. The main ones:

- `/help` — see all available commands.
- `/init` — generates a `CLAUDE.md` analyzing the project.
- `/clear` — reset the conversation (keeps the working directory).
- `/compact` — compresses the history (useful when approaching the limit).
- `/review` — review of the current PR.
- `/security-review` — review specific to security issues.
- `/model` — change model (e.g. from Sonnet to Opus for difficult tasks).

You can also **define your own slash commands** by placing `.md` files in `.claude/commands/` with instructions:

```markdown
# .claude/commands/deploy.md

Run the deploy in staging:
1. Verify `main` is clean.
2. Tag the current version.
3. Run `./scripts/deploy.sh staging`.
4. Smoke test on https://staging.example.com.
5. Report results.
```

Then in chat: `/deploy` → the agent follows the procedure.

## 9.5 Hooks

Hooks are **shell scripts** that the system runs in response to events (e.g. "after every file edit", "before a commit"). Configured in `~/.claude/settings.json` or `<project>/.claude/settings.json`:

```json
{
  "hooks": {
    "PostToolUse:Edit": [
      {
        "command": "make lint",
        "matcher": {"path_regex": "src/.*\\.py$"}
      }
    ],
    "Stop": [
      {"command": "say 'Claude finished'"}
    ]
  }
}
```

Useful examples:
- Post-edit Python file: runs `ruff` automatically.
- Post-edit test: runs only the affected tests.
- Stop: desktop or Slack notification when the agent finishes a long task.

Hooks are powerful because they **automate checks that would otherwise depend on the model**.

## 9.6 MCP server: extending tools

Seen in Ch. 6: MCP servers expose tools that Claude Code can consume.

Configuration in `.claude/settings.json`:

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path"]
    },
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {"GITHUB_TOKEN": "ghp_..."}
    }
  }
}
```

Once enabled, Claude Code sees them as additional available tools. You can ask "open PR #123 and read the comments" and the agent will use the GitHub MCP tool.

## 9.7 Permissions and security

Claude Code asks for confirmation before risky actions. You can:

- **Approve once** (default).
- **Approve for the session**.
- **Add a permanent rule** in `settings.json`:

```json
{
  "permissions": {
    "allow": [
      "Bash(npm test)",
      "Bash(git status)",
      "Edit(src/**)",
      "Read(**)"
    ],
    "deny": [
      "Bash(rm -rf*)",
      "Edit(.env*)"
    ]
  }
}
```

Recommended pattern:
- **Free read**, **Edit limited to code folders**, **Bash with whitelist** of non-destructive commands.
- Never `allow: ["*"]` in global settings.

The `fewer-permission-prompts` skill analyzes your logs and suggests sensible permissions.

## 9.8 Subagents: parallelize and specialize

Claude Code can launch **subagents** for delegated tasks. Typical types:

- **Explore** — explores the codebase to find patterns, definitions.
- **Plan** — designs an implementation plan.
- **claude-code-guide** — answers questions about Claude Code itself.

When to launch a subagent:
- For broad codebase searches (avoids "consuming" your context with grep and tree).
- For independent tasks that can run in parallel.
- To delegate external research while you work on the main task.

Example in chat:

> "Explore the codebase and find me all places where date parsing is done, report the patterns used."

The main agent will launch an `Explore` subagent for the search work, receiving only the final summary (and saving context).

## 9.9 Typical development workflows with Claude Code

### Developing a feature
1. Write a brief spec in chat: what, why, constraints.
2. Ask Claude to **create a plan** (`/plan` or "make me a plan before writing").
3. Review the plan, correct if needed.
4. "Proceed". The agent implements, runs tests, iterates.
5. You do code review of the diff (`git diff`).
6. Commit (manually or asking Claude).

### Bug fix
1. Describe the bug + how to reproduce.
2. "Find the cause, propose a fix with a test."
3. Claude explores, proposes, writes test, runs.
4. You evaluate the diff and commit.

### Refactor
1. "Refactor X to Y. Constraints: don't break tests, keep public API."
2. Let the agent do the heavy work.
3. Verify the diff is minimal and targeted. If bloated, ask to restart with stricter constraints.

### Onboarding a new repo
1. `/init` to generate a base `CLAUDE.md`.
2. "Explain this repo's architecture: main modules, dataflow, dependencies."
3. "Where do I look to understand X?"
4. Save discoveries in `CLAUDE.md`.

## 9.10 Operational tips

- **One session = one task.** Don't use the same session for refactor + new feature + bug fix. Create separate sessions, or use `/clear`.
- **Give narrative context, not curt orders.** "We're migrating from X to Y, today's the Z module, watch out for test E that's flaky" → much more effective than "modify file W".
- **Verify diffs before committing.** The agent is good, not perfect. `git diff` is your friend.
- **Use plan mode (`/plan`)** for tasks >30 minutes of work: see what it will do before it does.
- **When stuck, give it more context, not more orders.** If it doesn't get it, info is usually missing.
- **Write `CLAUDE.md` as you go**: every time you explain a convention once, write it there. You save time forever.
- **Iteration limits**: for long tasks, auto-compaction compresses history. Works well but on surgical tasks can lose details — prefer focused sessions.

## 9.11 Differences with Cursor, Aider, Copilot

| Tool | Model | Pattern |
|---|---|---|
| **Claude Code** | Loop agent, in terminal | You give goals, it acts |
| **Cursor** | IDE-first with built-in AI | Mix of autocomplete + chat in IDE |
| **Aider** | Agent CLI similar to Claude Code | Pre-Claude Code, model-agnostic |
| **Copilot** | Autocomplete in editor | Suggests as you write |

They are not mutually exclusive. Many devs use Claude Code for big tasks and Copilot/Cursor for daily typing flow.

## 9.12 Practice: the first real task

Open one of your projects in Claude Code and try this:

> "Analyze the project and tell me: 1) what it does in 3 sentences, 2) the 3 areas with the most technical debt, 3) a quick win you could do today."

In 5 minutes you'll have an analysis that would take hours from a new dev. From there, decide if you want to be helped fixing one of the points.

## 9.13 Key takeaways

- **Claude Code = terminal-based agent for devs.** Reads, edits, runs code in your repo, with confirmation.
- **CLAUDE.md** saves project conventions: write once, reuse always.
- **Slash commands** automate repeated procedures.
- **Hooks** run scripts in response to events (lint after edit, notify at end of task).
- **MCP** extends available tools.
- **Subagents** for delegable tasks without saturating main context.
- **Whitelist permissions**, never "allow everything".

## 9.14 Common mistakes

- **Using it like ChatGPT in chat.** Without giving it file access, you waste 90% of the value.
- **Skipping the plan** for tasks >30 minutes. Result: work that goes out of scope.
- **Not writing `CLAUDE.md`.** You repeat the same instructions every session.
- **Giving too-broad permissions.** "Allow Bash" = the agent can `rm -rf` without asking.
- **Not reviewing diffs.** The commit is your responsibility, not its.
- **Sessions too long and mixed.** One task = one session, reopen when changing goal.

---

You've learned to use ready-made agents. Now let's move on to **building**: how to make an agent from scratch, with your own code.

→ [Chapter 10 — Building agents with API and SDK](10-costruire-agenti-con-api-sdk.md)
