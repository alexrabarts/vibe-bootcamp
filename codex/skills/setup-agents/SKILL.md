# Setup Agents

Configure your working persona based on the project type.

## When to Use

Use this skill at the start of a project to configure the right mindset and expertise for the work ahead.

## How It Works

Unlike Claude Code's agent system (which uses separate sub-agents), in Codex you adopt specialist personas as needed. This skill helps you identify which expertise areas are relevant to the current project.

## Process

### Step 1: Detect Project Type

Look for indicator files:

| Files Found | Project Type | Expertise Needed |
|-------------|-------------|-----------------|
| `go.mod` | Go backend | Backend development, database design |
| `package.json` + `next.config.*` | Next.js | Frontend development, React patterns |
| `package.json` (generic) | Node.js | JavaScript/TypeScript development |
| `Cargo.toml` | Rust | Systems programming |
| `pyproject.toml` / `requirements.txt` | Python | Python development, data analysis |
| `Dockerfile` / `docker-compose.yml` | Containerized | Infrastructure, deployment |
| `*.xcodeproj` / `Podfile` | iOS | Swift/Objective-C development |
| `build.gradle` + `app/src/main/kotlin` | Android | Kotlin development |

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

Remind the user of available skills:
- `$create-plan` - Plan before implementing
- `$implement-plan` - Automated implementation with review loops
- `$code-review` - Pre-commit code review
- `$update-doc` - Document learnings and issues

## Specialist Knowledge Areas

When a project type is detected, prioritize these considerations:

**Backend (Go):** Strong typing, error wrapping, context propagation, goroutine safety, database connection pooling, middleware patterns.

**Frontend (React/Next.js):** Component composition, state management, accessibility, server vs client rendering, TypeScript strict mode.

**Database:** Normalization, index strategy, migration safety (additive changes for zero-downtime), query optimization, connection pooling.

**Infrastructure:** Least privilege, secret management, logging and monitoring, graceful shutdown, health checks.
