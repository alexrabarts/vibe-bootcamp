# Vibe Bootcamp — Engineering Teams Guide

This guide is for engineering teams adopting Claude Code in existing repositories. It covers install, agents, and the day-to-day workflow. For greenfield projects with hosting and deployment, see [hackathon.md](./hackathon.md).

---

## This Is Just One Setup

The configuration in this repo is my personal opinionated take — the agents, slash commands, and workflows I use day-to-day. I'm not pitching it as the right answer. The point is that you should be running **something like this**, not nothing.

If you point Claude Code at a production codebase with no agents, no planning workflow, and no review loop, you'll get output that looks plausible and breaks in subtle ways. The scaffolding (specialist agents, plan-before-implement, automated review) is what gets you from "AI generated some code" to "AI generated code I'd ship." Pick a setup, learn its patterns, and stick with it long enough to internalize the workflow.

If this one doesn't fit, here are the most-starred Claude Code repos on GitHub. Their approaches differ from this one in distinct ways — read the right column to see how:

| # | Repo | Stars | What it is | Differs from this guide |
|---|------|-------|------------|-------------------------|
| 1 | [affaan-m/everything-claude-code](https://github.com/affaan-m/everything-claude-code) | 171k | Cross-harness performance library: 48 agents, 182 skills, 68 commands, 34 rules, hooks | Massive generic skills/rules library across Claude/Codex/Cursor/OpenCode — no named-agent personas and no opinionated plan-then-review-loop tying them together |
| 2 | [anthropics/claude-code](https://github.com/anthropics/claude-code) | 120k | The official Claude Code CLI itself | The underlying tool this guide configures — ships zero personas, slash commands, or planning workflow out of the box |
| 3 | [forrestchang/andrej-karpathy-skills](https://github.com/forrestchang/andrej-karpathy-skills) | 104k | Single CLAUDE.md with four Karpathy-derived coding-behavior principles | One drop-in guideline file — no named agents, no commands, no review loop; tunes behavior via principles rather than orchestrating specialists |
| 4 | [garrytan/gstack](https://github.com/garrytan/gstack) | 88k | 23 role-based slash skills plus 8 power tools (CEO, Designer, Eng Manager, Release Manager, Doc Engineer, QA) | Closest analogue — also role-based and workflow-driven (Think-Plan-Build-Review-Ship-Reflect), but built around slash-command roles rather than named-personality subagents |
| 5 | [thedotmack/claude-mem](https://github.com/thedotmack/claude-mem) | 71k | Plugin that captures session context, compresses it, and injects it into future sessions | A persistent-memory plugin, not a workflow setup — complements something like this guide rather than replacing it |

---

## Get Claude Running

Once you have a Claude.ai account (Pro or Team plan), this is all it takes to get started.

All of the commands below are run in a **terminal** (also called a command line or shell). If you've never opened one before:

- **macOS** — press `Cmd+Space`, type `Terminal`, press Enter
- **Windows** — press `Win`, type `PowerShell`, press Enter (or use Windows Terminal if you have it)

**macOS / Linux:**

```bash
# Install git and just (skip if already installed)
brew install git just

# Install Claude Code
curl -fsSL https://claude.ai/install.sh | bash

# Clone this repo
git clone https://github.com/alexrabarts/vibe-bootcamp.git
cd vibe-bootcamp

# Copy the agent configuration to your home directory
cp -r claude ~/.claude

# Now cd into your actual project repo and launch Claude there
cd /path/to/your/project
claude
```

**Windows** — see [Local Setup](#local-setup) for platform-specific install instructions, then come back here.

Once Claude is running inside your project, kick off the agent setup with:

```
/setup-agents
```

This activates the right specialist agents for your codebase. The rest of this guide documents the workflow that follows.

### A Note on Permissions

By default, Claude Code asks for permission before running shell commands, editing files, etc. For faster iteration on lower-risk work, you can skip these prompts:

```bash
claude --dangerously-skip-permissions
```

**A word of caution:** This lets Claude execute any command without asking first — including destructive ones like deleting files or overwriting work. Only use it when you trust the context, and switch back to normal mode for anything production-adjacent.

Add an alias to save typing:

**macOS / Linux** — add to `~/.bashrc` or `~/.zshrc`:

```bash
alias cc='claude --dangerously-skip-permissions'
```

Then reload your shell (`source ~/.zshrc` or open a new terminal) and use:

```bash
cc
```

**Windows (PowerShell)** — add to your PowerShell profile (`notepad $PROFILE`):

```powershell
function cc { claude --dangerously-skip-permissions @args }
```

---

## Local Setup

Full setup details for all platforms. If you followed the quick start above, most of this is already done.

### Prerequisites

#### macOS

Install [Homebrew](https://brew.sh) first if you don't have it - it's the standard package manager for macOS and makes installing everything else easy:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

Then install the tools you'll need:

```bash
brew install git just
```

#### Windows

Install [Git for Windows](https://git-scm.com/download/win) - choose the default options during installation. This also gives you Git Bash, which you'll use for terminal commands below.

Install [just](https://github.com/casey/just#installation) (task runner):

```bash
winget install Git.Git Casey.Just
```

### Clone This Repo

```bash
git clone git@github.com:alexrabarts/vibe-bootcamp.git
cd vibe-bootcamp
```

If you don't have SSH keys set up with GitHub, use HTTPS instead:

```bash
git clone https://github.com/alexrabarts/vibe-bootcamp.git
cd vibe-bootcamp
```

### Install Claude Code

Claude Code has a standalone installer - no Node.js or npm required.

**macOS / Linux:**

```bash
curl -fsSL https://claude.ai/install.sh | bash
```

Or via Homebrew:

```bash
brew install --cask claude-code
```

**Windows (PowerShell):**

```powershell
irm https://claude.ai/install.ps1 | iex
```

Or via WinGet:

```powershell
winget install Anthropic.ClaudeCode
```

Verify it's working:

```bash
claude --version
```

Native installations auto-update in the background. Homebrew/WinGet installations need manual updates (`brew upgrade claude-code` or `winget upgrade Anthropic.ClaudeCode`).

See the [official setup guide](https://code.claude.com/docs/en/getting-started) for more details.

### Copy the Agent Configuration

The repo contains a pre-configured set of AI agents and workflows in the `claude` directory. You need to copy these to your home directory:

**macOS / Linux / Git Bash:**

```bash
cp -r claude ~/.claude
```

**Windows (PowerShell):**

```powershell
Copy-Item -Recurse -Force claude $env:USERPROFILE\.claude
```

### Codex Setup

If you prefer to use OpenAI Codex instead of Claude Code, equivalent configurations are provided in the `codex/` directory.

**Install Codex:**

Codex requires Node.js 18+. Install it from [nodejs.org](https://nodejs.org) or via your package manager if you don't have it.

```bash
npm install -g @openai/codex
```

**Copy the Codex skills:**

```bash
# Create the codex config directory
mkdir -p ~/.codex/skills

# Copy skills (equivalent to Claude Code's slash commands)
cp -r codex/skills/* ~/.codex/skills/
```

Codex uses a "Skills" system that's functionally similar to Claude Code's slash commands. Each skill is a directory with a `SKILL.md` file that contains the prompt and instructions. See the `codex/` directory for the full set.

**Note:** Codex skills are invoked differently from Claude Code commands. In Codex, you can reference a skill with `$skill-name` in your prompt, or Codex may automatically select an appropriate skill based on your task description.

### Codex App (GUI) Setup

If you prefer a GUI over the CLI, the [Codex app](https://chatgpt.com/codex) (available to ChatGPT Pro/Plus users) runs tasks in a cloud sandbox VM preloaded with your repository. It can read and edit files, run commands, and commit changes - similar to the CLI but through a web interface.

The Codex app doesn't support custom user-installed skills yet, so instead of invoking skills by name, you paste the workflow instructions directly into the task description. Prompt templates for this are provided in `chatgpt/prompts/`:

- `chatgpt/prompts/create-plan.md` - Paste when starting a planning task
- `chatgpt/prompts/implement-plan.md` - Paste when ready to implement
- `chatgpt/prompts/code-review.md` - Paste when you want a review before committing

You can also set up custom instructions (Settings > Personalization > Custom Instructions) using the contents of `chatgpt/custom-instructions.md` to give the model baseline context about your preferred workflow.

---

## The Workflow

This section walks through what a typical session looks like once you're set up.

### Start a Session in Your Project

From the root of your existing project repo, launch Claude:

```bash
claude
```

### Set Up Agents for Your Project

Inside Claude Code, run:

```
/setup-agents
```

This command analyzes your project and activates the relevant specialist agents. For an existing project, it inspects the codebase and proposes a sensible set.

You can also auto-detect based on project files:

```
/setup-agents auto
```

Or manually pick agents:

```
/setup-agents go-backend-dev shadcn-ui-builder database-expert
```

**Available agents include:**

| Agent | Specialty |
|-------|-----------|
| Shane | Go backend development |
| Monty | Python backend development, APIs, data pipelines |
| Oliver | React/Next.js frontend with shadcn/ui |
| Amber | UX design and prototyping |
| DBA Dan | Database design and optimization |
| Scott | System administration and deployment |
| Eric | Strategic architecture and design |
| David | Product requirements and planning |
| Wigsy | Code review and quality (always available) |
| Paige | Technical documentation (always available) |

Run `/setup-agents list` to see all available agents.

**Renaming agents:** These names are just our defaults - feel free to rename any agent to whatever you like. Each agent is a markdown file in `~/.claude/agents-library/`. Rename the file and update the name inside it to make it your own.

### Plan Your Feature

Both Claude Code and Codex have a **plan mode** - a mode where the AI thinks through the problem, explores your codebase, and proposes an approach *without actually writing or modifying any files*. This is one of the most important habits to build: always plan before you implement. It prevents the AI from charging off in the wrong direction, and it gives you a chance to course-correct before any code is written.

To enter plan mode, press **Shift+Tab** to toggle it on (works in both Claude Code and Codex). You can also type `/plan` in Codex.

Describe what you want to build:

```
I want to build [describe your feature/app]. Let's plan this out.
```

For a more structured planning process, use the `/create-plan` command (Claude Code) or the `$create-plan` skill (Codex).

The `/create-plan` command triggers a thorough multi-phase planning process:

1. **Exploration** - Agents investigate your codebase to understand the current state
2. **Multi-hypothesis analysis** - At least 3 different approaches are generated and compared
3. **Detailed design** - The chosen approach is fleshed out into phases with specific file changes
4. **Review** - Architecture and security reviewers check the plan before implementation

The result is a structured plan file saved to `.claude/plans/` that's ready for automated implementation.

### Implement the Plan

Once you're happy with the plan, run:

```
/implement-plan
```

This kicks off fully automated implementation:

1. **Agent detection** - Figures out which specialists are needed
2. **Plan review** - Eric (architecture) and Wigsy (security) review the plan
3. **Parallel implementation** - Multiple agents work simultaneously where possible, using git worktrees
4. **Automated testing** - Tests are run after each integration
5. **Code review loop** - Wigsy reviews the code, agents fix issues, repeat (up to 5 iterations)
6. **Documentation** - Paige updates docs if new user-facing features were added

You don't need to intervene between steps. When it's done, review the changes with `git diff` and commit when you're satisfied.

### Review and Iterate

If you want a manual code review at any point:

```
/code-review
```

This invokes Wigsy to review your uncommitted changes, including automatically running the test suite.

To document learnings or issues as you go:

```
/update-doc I learned that X requires Y
/update-doc Issue: Z is broken when W happens
```

---

## Troubleshooting

### Claude Code can't find agents

Make sure you copied the files to the right location:

```bash
ls ~/.claude/agents-library/  # Should list .md files
ls ~/.claude/commands/         # Should list .md files
```

### /setup-agents says agent not found

The agents are stored in `~/.claude/agents-library/`. Run `/setup-agents list` to see what's available. If the library is empty, re-run the copy step from [Copy the Agent Configuration](#copy-the-agent-configuration).

---

## Reference

### Claude Code Slash Commands

| Command | Purpose |
|---------|---------|
| `/setup-agents` | Activate specialist agents for your project |
| `/create-plan` | Generate a thorough implementation plan |
| `/implement-plan` | Automatically implement a plan with review loops |
| `/code-review` | Get a comprehensive code review from Wigsy |
| `/update-doc` | Add learnings, issues, or ideas to project docs |

### Useful Links

- [Claude Code Documentation](https://docs.anthropic.com/en/docs/claude-code)
- [OpenAI Codex Documentation](https://platform.openai.com/docs)
- [just Documentation](https://just.systems/man/en/)
