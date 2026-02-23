---
description: Set up project-specific agents from the agent library
---

You are helping the user set up project-specific Claude Code agents. The user has a library of agents in `~/.claude/agents-library/` and wants to activate only relevant agents for the current project.

## Command Modes

### 1. Auto Mode: `/setup-agents auto`
Automatically detect project type and symlink appropriate agents without asking questions.

### 2. Interactive Mode: `/setup-agents` (no arguments)
Detect project type, suggest agents, and ask clarifying questions for ambiguous cases.

### 3. Manual Mode: `/setup-agents agent1 agent2 ...`
Symlink specific agents by name (e.g., `/setup-agents go-backend-dev database-expert`).

### 4. Sync Mode: `/setup-agents sync`
Re-create symlinks for existing project agents (useful if library was moved or links broken).

### 5. List Mode: `/setup-agents list`
Show available agents organized by category.

## Agent Library Structure

The agent library is located at `~/.claude/agents-library/` with the following categories:

- **backend/** - go-backend-dev, database-expert
- **frontend/** - shadcn-ui-builder
- **mobile/** - android-kotlin-expert, ios-expert-reviewer
- **infrastructure/** - network-infrastructure-expert, sysadmin-expert
- **planning/** - product-requirements-architect, strategic-architect, agent-orchestrator
- **data/** - data-analyst
- **automation/** - autonomous-executor
- **specialized/** - music-theory-expert, geo-aeo-strategist

**Universal agents** (always available in `~/.claude/agents/`):
- code-reviewer
- technical-docs-writer
- prompt-engineer

## Your Task

### Step 1: Parse Command Arguments

Determine which mode the user is requesting:
- No arguments or any text besides mode keywords → Interactive mode
- `auto` → Auto mode
- `sync` → Sync mode
- `list` → List mode
- Specific agent names → Manual mode

### Step 2: Check Current State

1. Check if `.claude/` directory exists in the project root
2. Check if `.claude/agents/` directory exists
3. Check if `agent-manifest.yaml` exists (indicates previously configured)

### Step 3: Execute Based on Mode

#### List Mode
Simply list all available agents organized by category with brief descriptions extracted from each agent's frontmatter.

#### Auto Mode
1. **Detect project type** by checking for indicator files (see detection patterns below)
2. **Select agents** based on detected patterns
3. **Create symlinks** from library to `.claude/agents/`
4. **Create manifest** with detection results
5. **Report** what was set up and why

#### Interactive Mode
1. **Detect project type** (same as auto mode)
2. **Present suggestions** based on detection
3. **Ask clarifying questions** if project type is ambiguous or multi-stack
4. **Create symlinks** for selected agents based on user responses
5. **Create manifest**
6. **Report** completion

#### Manual Mode
1. **Validate agent names** against library
2. **Create symlinks** to `.claude/agents/` for specified agents
3. **Update or create manifest**
4. **Report** what was linked

#### Sync Mode
1. **Read existing manifest** to see which agents should be active
2. **Remove broken symlinks** and re-create them from library
3. **Update manifest** with sync timestamp
4. **Report** what was updated

## Project Detection Patterns

Use Glob tool to check for these indicator files (check multiple patterns in parallel):

### Backend Projects

| Pattern | Project Type | Suggested Agents |
|---------|-------------|------------------|
| `go.mod` | Go backend | go-backend-dev, database-expert |
| `Cargo.toml` | Rust | (none specific, use universal agents) |
| `pom.xml` or `build.gradle*` (without android/) | Java backend | database-expert |
| `requirements.txt` or `pyproject.toml` or `setup.py` | Python | data-analyst |

### Frontend Projects

| Pattern | Project Type | Suggested Agents |
|---------|-------------|------------------|
| `package.json` + `next.config.*` | Next.js | shadcn-ui-builder |
| `package.json` + `app/` + `nuxt.config.*` | Nuxt | (none specific) |
| `package.json` (generic) | Node.js | (none specific, use universal agents) |

### Mobile Projects

| Pattern | Project Type | Suggested Agents |
|---------|-------------|------------------|
| `build.gradle*` + `app/src/main/java` or `app/src/main/kotlin` | Android | android-kotlin-expert |
| `*.xcodeproj` or `*.xcworkspace` or `Podfile` | iOS | ios-expert-reviewer |
| `pubspec.yaml` | Flutter | (none specific) |

### Infrastructure Projects

| Pattern | Project Type | Suggested Agents |
|---------|-------------|------------------|
| `docker-compose.yml` or `Dockerfile` | Docker/containers | sysadmin-expert |
| `terraform/*.tf` or `*.tf` | Infrastructure as Code | sysadmin-expert, network-infrastructure-expert |
| `.github/workflows/` or `.gitlab-ci.yml` | CI/CD | sysadmin-expert |
| `ansible/` or `playbooks/` | Configuration management | sysadmin-expert |

### Multi-Stack Detection

If multiple patterns match, suggest agents from all matching categories. Examples:
- `go.mod` + `package.json` → go-backend-dev, database-expert, shadcn-ui-builder
- `go.mod` + `Dockerfile` → go-backend-dev, database-expert, sysadmin-expert
- `build.gradle` + `go.mod` → android-kotlin-expert, go-backend-dev, database-expert

### Planning/Documentation Projects

If no clear technical stack is detected, ask if this is a planning/documentation project and suggest:
- product-requirements-architect
- strategic-architect
- technical-docs-writer

## Interactive Questions

When project type is ambiguous or you want to confirm, use AskUserQuestion tool:

### Question 1: Project Type (if unclear)
```
header: "Project type"
question: "What is the primary focus of this project?"
options:
  - label: "Backend API/Service"
    description: "Server-side application or API"
  - label: "Web Application"
    description: "Frontend web application"
  - label: "Mobile Application"
    description: "Android or iOS app"
  - label: "Infrastructure/DevOps"
    description: "Infrastructure, deployment, or automation"
multiSelect: false
```

### Question 2: Technologies (for multi-stack or ambiguous)
```
header: "Tech stack"
question: "Which technologies are you actively using?"
options:
  - label: "Go"
    description: "Go backend development"
  - label: "TypeScript/React/Next.js"
    description: "Modern JavaScript frontend"
  - label: "Android (Kotlin)"
    description: "Native Android development"
  - label: "iOS (Swift)"
    description: "Native iOS development"
  - label: "Database (PostgreSQL/DuckDB)"
    description: "Database design and queries"
  - label: "Infrastructure (Docker/K8s)"
    description: "Deployment and infrastructure"
multiSelect: true
```

### Question 3: Work Type (optional, for fine-tuning)
```
header: "Work focus"
question: "What type of work will you do most in this project?"
options:
  - label: "Feature development"
    description: "Building new functionality"
  - label: "Architecture planning"
    description: "Designing system architecture"
  - label: "Code review & refactoring"
    description: "Reviewing and improving code"
  - label: "Documentation"
    description: "Writing technical documentation"
multiSelect: true
```

Based on answers, map to agents:
- Backend API + Go → go-backend-dev, database-expert
- Web Application + TypeScript → shadcn-ui-builder
- Mobile + Android → android-kotlin-expert
- Infrastructure → sysadmin-expert, network-infrastructure-expert
- Architecture planning → strategic-architect, product-requirements-architect

## Agent Manifest Format

Create or update `.claude/agent-manifest.yaml`:

```yaml
version: 1
updated: YYYY-MM-DDTHH:MM:SSZ
project_type: go-backend
detection_method: auto  # or interactive or manual
agents:
  - name: go-backend-dev
    source: go-backend-dev.md
  - name: database-expert
    source: database-expert.md
notes: "Detected Go backend project with database usage"
```

Notes:
- `updated`: Timestamp in ISO 8601 format for when manifest was last modified
- `source`: Filename in `~/.claude/agents-library/` (agents are symlinked, not copied)
- No `copied` timestamp needed since symlinks always reflect latest version

## File Operations

### Creating .claude directory structure
```bash
mkdir -p .claude/agents
```

### Creating symlinks to agents
```bash
ln -sf ~/.claude/agents-library/go-backend-dev.md .claude/agents/go-backend-dev.md
```

Note: Use `-sf` flags for `ln`:
- `-s`: Create symbolic link
- `-f`: Force (overwrite existing file/link if present)

### Validating agent exists
Check if source file exists before symlinking:
```bash
test -f ~/.claude/agents-library/go-backend-dev.md && echo "exists"
```

### Checking for broken symlinks
```bash
# Check if symlink exists but target is missing
if [ -L .claude/agents/go-backend-dev.md ] && [ ! -e .claude/agents/go-backend-dev.md ]; then
    echo "broken symlink"
fi
```

## Important Guidelines

1. **Always check if .claude/agents/ already exists**
   - If it exists and has agents, warn user and ask if they want to replace or add to existing agents
   - In sync mode, this is expected

2. **Validate agent names** in manual mode
   - Check that each requested agent exists in the library
   - Provide helpful error if agent doesn't exist (list similar names)

3. **Be conservative with suggestions**
   - Don't suggest too many agents - only what's clearly relevant
   - Universal agents (code-reviewer, etc.) are always available, don't symlink them to project

4. **Provide clear feedback**
   - List which agents were activated and why
   - Explain how to add more agents later (run command again)
   - Mention that changes take effect immediately (agents are loaded at start)

5. **Handle edge cases**
   - Empty project (no indicator files) → ask questions
   - Library directory missing → report error with setup instructions
   - Agent file missing from library → report which agents couldn't be copied

6. **Git considerations**
   - Suggest adding `.claude/agents/` to `.gitignore` for private agents
   - OR suggest committing them for team collaboration
   - Never add/commit automatically - just advise

## Example Outputs

### Auto Mode Success
```
Detected project type: Go backend with database

Symlinked agents to .claude/agents/:
  ✓ go-backend-dev (backend development)
  ✓ database-expert (database design and queries)

Universal agents already available:
  • code-reviewer
  • technical-docs-writer
  • prompt-engineer

Created agent manifest at .claude/agent-manifest.yaml

These agents are now active for this project. Changes to library agents
will automatically propagate to this project.

To add more agents:
  /setup-agents agent-name

To re-create symlinks (if library moved):
  /setup-agents sync
```

### Interactive Mode with Questions
```
Detected indicators for multiple project types:
  - Go backend (go.mod)
  - Frontend (package.json)

[Shows AskUserQuestion with tech stack options]

Based on your selections, symlinked agents:
  ✓ go-backend-dev
  ✓ database-expert
  ✓ shadcn-ui-builder

Created agent manifest at .claude/agent-manifest.yaml
```

### Manual Mode
```
Symlinking requested agents to .claude/agents/:
  ✓ go-backend-dev
  ✓ strategic-architect

Updated agent manifest at .claude/agent-manifest.yaml

These agents are now active for this project.
```

### List Mode
```
Available agents in ~/.claude/agents-library/:

Backend:
  • go-backend-dev - Go service development
  • database-expert - Database design and optimization

Frontend:
  • shadcn-ui-builder - React/Next.js with shadcn/ui components

Mobile:
  • android-kotlin-expert - Android app development
  • ios-expert-reviewer - iOS app code review

Infrastructure:
  • network-infrastructure-expert - Network and infrastructure
  • sysadmin-expert - System administration

Planning:
  • product-requirements-architect - PRD creation
  • strategic-architect - System architecture design
  • agent-orchestrator - Agent coordination

Data:
  • data-analyst - Database queries and analysis

Automation:
  • autonomous-executor - Long-running autonomous tasks

Specialized:
  • music-theory-expert - Music theory and composition
  • geo-aeo-strategist - AI content optimization

Universal (always available):
  • code-reviewer - Code review and quality
  • technical-docs-writer - Technical documentation
  • prompt-engineer - AI prompt optimization

To activate agents: /setup-agents <agent-name> ...
To auto-detect: /setup-agents auto
```

## Error Handling

- **Library not found**: "Agent library not found at ~/.claude/agents-library/. Run 'chezmoi apply' to sync your dotfiles."
- **Agent not found**: "Agent 'foo' not found in library. Available agents: [list]. Did you mean 'go-backend-dev'?"
- **Already configured**: ".claude/agents/ already exists with N agents. Add more agents (a), replace all (r), or cancel (c)?"
- **Permission denied**: "Cannot create .claude/ directory. Check permissions."
- **Broken symlinks**: "Found N broken symlinks in .claude/agents/. Run '/setup-agents sync' to fix."

Now execute the user's requested mode!
