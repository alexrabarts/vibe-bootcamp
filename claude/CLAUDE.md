# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) and other AI agents when working in this environment.

## Development Workflow

### Git Operations
- NEVER commit or push automatically
- When work is complete, suggest a commit message but wait for explicit user instruction to commit
- Always wait for explicit user instruction to push
- Use conventional commit messages that focus on "why" rather than "what"
- Only create commits when the user explicitly says "commit" or asks for changes to be committed

### Planning Before Execution
- For non-trivial tasks, discuss approach before implementing
- Break complex features into phases
- Identify dependencies and potential issues upfront
- Provide options when multiple valid approaches exist

**When in planning mode:**
- Provide more comprehensive analysis than during implementation
- Include explicit reasoning for architectural decisions and trade-offs
- Enumerate alternative approaches with pros/cons for each option
- Break down phases into specific, actionable steps with clear deliverables
- Identify integration points, dependencies, and potential failure modes
- Specify success criteria and testing strategy for each phase
- Surface assumptions that need validation before implementation begins
- Planning mode is for thorough analysis; implementation mode is for execution

### Iterative Development
- Deliver working increments frequently
- Test after each significant change
- Gather feedback before proceeding to next phase
- Be prepared to adjust based on feedback

## Project Structure Standards

### .agent/ Directory
Every project should maintain an `.agent/` directory for AI agent documentation and knowledge.

**Directory structure:**
- **sop/** - Standard Operating Procedures (issues, learnings, debugging, deployment)
- **system/** - System Documentation (architecture, database, dependencies, API)
- **tasks/** - Project Planning (roadmap, PRD, backlog)

Each `.agent/` directory should include a `README.md` that:
- Explains the directory structure
- Links to existing documentation files
- Describes how to update documentation (e.g., via `/update-doc` command)

**Updating documentation:**
Use the `/update-doc` slash command to add content to .agent/ files:
```
/update-doc I learned that X requires Y
/update-doc Issue: Z is broken when W happens
/update-doc Feature idea: implement ABC
```

See the [dotfiles .agent/README.md](https://github.com/alexrabarts/dotfiles/tree/master/.agent) for a reference implementation.

### Development Commands
Common just recipes across projects:
- `just build` - Compile binary
- `just run` - Run locally for testing
- `just test` - Run test suite
- `just deps` - Install/update dependencies
- `just install` - Install to standard location
- `just deploy` - Deploy to production
- `just logs` - View service logs

## Agent Specialization

### Agent Management Philosophy

Prefer using sub-agents (Task tool) over writing code directly. Before implementing any code changes, always check if a suitable sub-agent exists for the task. Use the appropriate specialized agent to handle implementation work. To minimize context usage, agents are organized into:

1. **Universal Agents** (`~/.claude/agents/`) - Always available:
   - `wigsy-code-reviewer` (Wigsy) - Code review, quality analysis, Git/JJ expertise, merge and release management
   - `paige-technical-docs-writer` (Paige) - Technical documentation and guides
   - `karen-manager` (Karen) - "Call the manager" - stern feedback when Claude is being lazy or cutting corners

2. **Agent Library** (`~/.claude/agents-library/`) - Activated per-project:
   - Flat structure with names at the beginning of filenames for easy identification
   - See `MANIFEST.md` for categorization and organization
   - Not loaded unless explicitly activated for a project

3. **Project-Specific Agents** (`.claude/agents/`) - Active for current project:
   - Symlinked from library using `/setup-agents` command
   - Changes to library agents automatically propagate to all projects
   - Override global agents when present

### Setting Up Project Agents

Use the `/setup-agents` slash command to activate relevant agents:

```bash
# Auto-detect project type and activate appropriate agents
/setup-agents auto

# Interactive mode with questions
/setup-agents

# Manually select specific agents
/setup-agents go-backend-dev database-expert

# List all available agents
/setup-agents list

# Sync project agents with library (update to latest)
/setup-agents sync
```

### Available Specialized Agents

All agents are in `~/.claude/agents-library/` with a flat structure. See `MANIFEST.md` for categories.

**Backend:**
- `shane-go-backend-dev` (Shane) - Go service development with DuckDB/PostgreSQL; cynical and snarky
- `dba-dan-database-expert` (DBA Dan) - Database design, optimization, and query tuning; very friendly and helpful

**Frontend:**
- `oliver-shadcn-ui-builder` (Oliver) - React/Next.js with shadcn/ui components

**Mobile:**
- `andy-android-kotlin-expert` (Andy) - Native Android development
- `iris-ios-expert-reviewer` (Iris) - Native iOS development

**Infrastructure:**
- `scott-sysadmin-expert` (Scott) - System administration (Linux/macOS), systemd, Homebrew, chezmoi; cynical but educational
- `lee-network-infrastructure-expert` (Lee) - Network configuration and troubleshooting

**Planning:**
- `david-product-requirements-architect` (David) - PRD creation and feature planning
- `eric-strategic-architect` (Eric) - System architecture design; cynical and intellectually above everyone
- `agent-orchestrator` - Agent coordination and routing

**Data:**
- `sarah-q-lewis-data-analyst` (Sarah Q. Lewis) - Database queries and data analysis; SQL expert

**Automation:**
- `winston-autonomous-executor` (Winston) - Long-running autonomous tasks; reliable and methodical

**Specialized:**
- `jacob-music-theory-expert` (Jacob) - Music theory and composition
- `mark-geo-aeo-strategist` (Mark) - AI content optimization (GEO/AEO)
- `proompty-mc-proomptface-prompt-engineer` (Proompty Mc Proomptface) - AI prompt engineering and optimization

### Implementing Plans with Multi-Agent Orchestration

Use the `/implement-plan` slash command to automatically implement a plan with automated quality gates:

```bash
/implement-plan
```

This command provides sophisticated autonomous workflow orchestration:

**What it does:**
1. **Detects required agents** - Analyzes your plan to determine which specialists are needed (Shane, Oliver, Amber, Dan, etc.)
2. **Verifies availability** - Checks if required agents are configured, prompts you to run `/setup-agents` if not
3. **Multi-reviewer validation** - Eric reviews architecture, Dan reviews database design, Wigsy reviews security
4. **Smart parallelization** - Uses git worktrees to run independent work streams in parallel when safe
5. **Automated dev-review loop** - Implements → Wigsy reviews → fixes issues → repeats (max 5 iterations)
6. **Auto-conflict resolution** - Merges parallel work with best-effort conflict resolution

**Key features:**
- Fully automatic execution (no approval needed between iterations)
- Dan acts as database consultant to Shane (provides guidance, doesn't implement)
- Convergence guarantee with max iteration limit
- Clear progress reporting throughout all phases
- Graceful handling of missing agents or failures

**When to use:**
- After completing a planning session with a clear plan
- When you want autonomous implementation with quality gates
- For complex features requiring multiple specialist agents
- When parallelization could speed up implementation

**Example workflow:**
```bash
# 1. Plan a feature in plan mode
# 2. Once plan is approved, run:
/implement-plan

# The orchestrator will:
# - Detect that you need Shane (backend) and Oliver (frontend)
# - Have Eric and Wigsy review the plan
# - Create git worktrees for parallel work
# - Have Shane and Oliver implement in parallel
# - Merge their work and have Wigsy review
# - Loop until code passes or max iterations reached
```

## Development Best Practices

### Code Quality
- Clear, descriptive names over comments
- Comments explain "why" not "what"
- Keep functions focused and small
- Avoid premature optimization

### Testing Strategy
- Unit tests for business logic
- Integration tests for external dependencies
- Use fixtures and mocks appropriately
- Test edge cases and error paths

### Security Considerations
- Never commit secrets (use .env files)
- Validate all external input
- Use principle of least privilege
- Keep dependencies updated

### Performance Patterns
- Profile before optimizing
- Cache expensive operations
- Use appropriate data structures
- Consider memory vs. speed tradeoffs

## Communication Style

### When Providing Updates
- Be concise but complete
- Focus on actionable information
- Explain trade-offs when making decisions
- Surface potential issues early

### When Asking Questions
- Be specific about what's unclear
- Provide context for why it matters
- Offer options when appropriate
- Make recommendations based on project patterns

### When Something Goes Wrong
- Describe what happened clearly
- Explain the impact
- Provide debugging steps taken
- Suggest fixes or workarounds

### General Communication Preferences
- Be concise but thorough
- No emojis unless explicitly requested
- Focus on technical accuracy
- Ask clarifying questions when requirements are ambiguous

## Common Pitfalls

### Configuration
- Validate config on startup
- Provide clear error messages for missing config
- Document all environment variables
- Use sensible defaults where possible

### Dependencies
- Review dependency licenses
- Monitor for security advisories
- Minimize external dependencies
- Keep dependencies updated

### Deployment
- Test locally before deploying
- Check logs after deployment
- Verify health endpoints
- Have rollback plan ready

## Project-Specific Notes

Each project may have additional guidelines in its own CLAUDE.md file. Always check for project-specific documentation that supersedes or extends these global guidelines.

**Technology-specific guidance lives in specialized agents:**
- Go project structure and patterns → `go-backend-dev` agent
- Database design and queries → `database-expert` agent
- React/Next.js UI development → `shadcn-ui-builder` agent
- System administration → `sysadmin-expert` agent
- Mobile development → `android-kotlin-expert` or `ios-expert-reviewer` agents

When in doubt:
1. Check project's CLAUDE.md
2. Use `/setup-agents` to activate appropriate specialized agents
3. Look for similar patterns in existing code
4. Ask the user for clarification
5. Prefer simplicity over cleverness
