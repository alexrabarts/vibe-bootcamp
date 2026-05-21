---
name: setup-agents
description: Select relevant Codex specialist persona skills for a project. Use at the start of work, when the user asks to set up agents, choose a specialist team, adapt Claude agents to Codex, or identify which persona skills fit the codebase.
---

# Setup Agents

Configure your working persona based on the project type.

## When to Use

Use this skill at the start of a project to configure the right mindset and expertise for the work ahead.

## How It Works

Unlike Claude Code's agent system (which uses separate sub-agents), Codex uses Skills. This repo provides one Codex skill per specialist persona under `codex/skills/` using the same names as the Claude agents. Use this skill to identify which persona skills are relevant to the current project and tell the user which `$skill-name` entries to invoke.

## Process

### Step 1: Detect Project Type

Look for indicator files:

| Files Found | Project Type | Expertise Needed |
|-------------|-------------|-----------------|
| `go.mod` | Go backend | `$shane-go-backend-dev`, `$dba-dan-database-expert` |
| `package.json` + `next.config.*` | Next.js | `$oliver-shadcn-ui-builder`, `$amber-ux-designer` |
| `package.json` (generic) | Node.js | `$oliver-shadcn-ui-builder` when UI-focused |
| `Cargo.toml` | Rust | Systems programming |
| `pyproject.toml` / `requirements.txt` | Python | `$monty-python-backend-dev`, `$sarah-q-lewis-data-analyst` when data-heavy |
| `Dockerfile` / `docker-compose.yml` | Containerized | `$scott-sysadmin-expert`, `$lee-network-infrastructure-expert` when networking is involved |
| `*.xcodeproj` / `Podfile` | iOS | `$iris-ios-expert-reviewer` |
| `build.gradle` + `app/src/main/kotlin` | Android | `$andy-android-kotlin-expert` |

### Step 2: Report Configuration

Tell the user what expertise areas are relevant and how you'll approach the project.

Example:
```
Detected: Go backend project with database usage

I'll focus on:
- Go backend development (API design, error handling, concurrency)
- Database design (schema, queries, migrations)
- Code quality (testing, security, documentation)

Ready to start. What would you like to build?
```

### Step 3: Note Available Workflows

Remind the user of available workflow skills:
- `$create-plan` - Plan before implementing
- `$implement-plan` - Automated implementation with review loops
- `$code-review` - Pre-commit code review
- `$update-doc` - Document learnings and issues

Also mention relevant specialist persona skills. Universal defaults are:
- `$karen-manager` - strict scope and quality feedback
- `$paige-technical-docs-writer` - documentation
- `$wigsy-code-reviewer` - code review and release quality
- `$proompty-mc-proomptface-prompt-engineer` - prompt engineering

## Specialist Knowledge Areas

When a project type is detected, prioritize these considerations:

**Backend (Go):** Strong typing, error wrapping, context propagation, goroutine safety, database connection pooling, middleware patterns.

**Frontend (React/Next.js):** Component composition, state management, accessibility, server vs client rendering, TypeScript strict mode.

**Database:** Normalization, index strategy, migration safety (additive changes for zero-downtime), query optimization, connection pooling.

**Infrastructure:** Least privilege, secret management, logging and monitoring, graceful shutdown, health checks.
