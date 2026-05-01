# Vibe Bootcamp

An opinionated but flexible starting point for working with AI coding agents — a curated set of specialist agents, automated planning and review workflows, and multi-AI support (Claude Code, OpenAI Codex, ChatGPT).

## Choose Your Path

This repo serves two audiences. Pick the guide that matches your situation:

- **[Hackathon / vibe coding →](docs/hackathon.md)** For greenfield projects taking an idea from zero to production. Covers domain and hosting choices, full local setup, the agent workflow, and two deployment paths (self-managed VPS or Vercel + Supabase).

- **[Engineering teams →](docs/dev-team.md)** For engineers introducing Claude Code into existing repositories. Covers install, agents, and the day-to-day workflow. Skips deployment and hosting.

## What's in the Repo

- **`claude/`** — Agents, slash commands, and configuration for Claude Code. Copied to `~/.claude` during setup.
- **`codex/`** — Equivalent skills for OpenAI Codex.
- **`chatgpt/`** — Prompt templates and custom instructions for the ChatGPT / Codex web app.

## License

MIT
