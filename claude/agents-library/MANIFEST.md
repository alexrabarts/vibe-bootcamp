# Agent Library Manifest

This directory contains ALL agents - both universal and specialized - in a flat structure. Each agent filename starts with their name for easy identification.

**Universal agents** (Karen, Paige, Wigsy) are symlinked from here into `~/.claude/agents/` so they're always available. All other agents are opt-in via `/setup-agents`.

## Categories

### Universal (Always Available)
- **Karen** (karen-manager.md) - "Call the manager" - stern feedback when Claude is being lazy or cutting corners
- **Paige** (paige-technical-docs-writer.md) - Technical documentation and guides
- **Wigsy** (wigsy-code-reviewer.md) - Code review, quality analysis, Git/JJ expertise, merge and release management

### Backend
- **Shane** (shane-go-backend-dev.md) - Go service development with DuckDB/PostgreSQL; cynical and snarky
- **DBA Dan** (dba-dan-database-expert.md) - Database design, optimization, and query tuning; very friendly and helpful

### Design
- **Amber** (amber-ux-designer.md) - UX design, user research, accessibility, information architecture; empathetic and user-focused

### Frontend
- **Oliver** (oliver-shadcn-ui-builder.md) - React/Next.js with shadcn/ui components

### Mobile
- **Andy** (andy-android-kotlin-expert.md) - Native Android development
- **Iris** (iris-ios-expert-reviewer.md) - Native iOS development

### Infrastructure
- **Scott** (scott-sysadmin-expert.md) - System administration (Linux/macOS), systemd, Homebrew, chezmoi; cynical but educational
- **Lee** (lee-network-infrastructure-expert.md) - Network configuration and troubleshooting

### Planning
- **Eric** (eric-strategic-architect.md) - System architecture design; cynical and intellectually above everyone
- **David** (david-product-requirements-architect.md) - PRD creation and feature planning
- **Agent Orchestrator** (agent-orchestrator.md) - Agent coordination and routing (no personality yet)

### Data
- **Sarah Q. Lewis** (sarah-q-lewis-data-analyst.md) - Database queries and data analysis; SQL expert (S.Q.L.)

### Automation
- **Winston** (winston-autonomous-executor.md) - Long-running autonomous tasks; reliable and methodical

### Specialized
- **Jacob** (jacob-music-theory-expert.md) - Music theory and composition
- **Mark** (mark-geo-aeo-strategist.md) - AI content optimization (GEO/AEO)
- **Paul** (paul-home-assistant-expert.md) - Home Assistant configuration, automations, blueprints, and dashboards; enthusiastic tinkerer
- **Proompty Mc Proomptface** (proompty-mc-proomptface-prompt-engineer.md) - AI prompt engineering and optimization
