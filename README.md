# Vibe Bootcamp

An opinionated but flexible starting point for vibe coding that takes you from idea to production.

## The Problem

Vibe coding is exciting, but people consistently hit the same walls:

- **"Where do I even start?"** - The blank canvas problem. You have an idea but no clear path from zero to working app.
- **"What tech stack should I use?"** - Decision paralysis from too many options, or picking something that creates problems later.
- **"It works on my machine, now what?"** - Getting from a local prototype to something hosted and accessible is a surprisingly large leap.
- **"The AI keeps going in circles"** - Workflows that don't get the most out of the models, leading to wasted time and frustrating results.

## What This Bootcamp Provides

This repo gives you an opinionated but flexible foundation:

- A **curated set of AI agents** with distinct specializations (backend, frontend, architecture, code review, etc.) that collaborate on your project
- **Automated workflows** that handle planning, implementation, and review loops - so you spend time on decisions, not on babysitting the AI
- A **production hosting blueprint** using battle-tested tools (Caddy, systemd, just) so deployment isn't an afterthought
- **Support for multiple AI tools** - primarily Claude Code, but with equivalent setups for OpenAI Codex and ChatGPT

The approach is opinionated so you can get moving fast, but everything is customizable once you understand the patterns.

---

## Before the Hackathon

Two things to do ahead of time. Everything else can be done on the day with Claude's help.

### 1. Sign Up for Accounts

- **[GitHub](https://github.com)** - Source control. You'll push your project here.
- **[Claude.ai](https://claude.ai)** - You'll need a Pro or Team plan to use Claude Code.

**Alternative AI tool:** If you prefer, you can use [OpenAI Codex](https://openai.com/codex) instead of Claude Code. See the [Codex Setup](#codex-setup) section.

### 2. Come With an Idea

This is the most important preparation step. Come with a project idea - or better yet, two:

- **Your ambitious idea** - The thing you actually want to build. A SaaS tool, a game, an API, a personal project you've been putting off.
- **A paired-back fallback** - A simpler version or a different idea entirely that you're confident can be executed in a day. If the ambitious idea hits roadblocks, you pivot to this.

Your idea could be something entirely new, an existing project you want to move into production, or an existing project you want to improve or extend. The key is to arrive knowing what you want to build.

---

## Get Claude Running

Once you have a Claude.ai account, this is all it takes to get started.

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

# Copy the agent configuration
cp -r claude ~/.claude

# Launch Claude
claude
```

**Windows** — see [Local Setup](#local-setup) for platform-specific install instructions, then come back here.

Once Claude is running, paste this to kick things off:

```
Read the README.md in this repo. I want to build [describe your idea briefly].
Help me set up my project and walk me through getting it into production.
Ask me any questions you need to understand what I'm building.
Pre-work I've already done: [e.g. "I have a VPS at x.x.x.x and domain example.com pointed to it" or "nothing yet"]
```

**That's it.** Claude will read this guide, ask you about your idea, help you pick a tech stack, set up your project, and walk you through production deployment step by step — including things like DNS and server configuration that can be tricky to do alone.

The remaining sections document everything Claude will walk you through, so you know what's happening and can do any of it manually if you prefer.

### A Note on Permissions

By default, Claude Code asks for permission before running shell commands, editing files, etc. During a hackathon where speed matters, you can skip these prompts:

```bash
claude --dangerously-skip-permissions
```

**A word of caution:** This lets Claude execute any command without asking first — including destructive ones like deleting files or overwriting work. It's convenient for rapid prototyping when you're comfortable with what the AI is doing, but you're giving up the safety net. Use it when you trust the context (e.g., a fresh project with nothing critical to lose), and switch back to normal mode for anything production-adjacent.

Add an alias to save typing:

**macOS / Linux** — add to `~/.bashrc` or `~/.zshrc`:

```bash
alias c-dsp='claude --dangerously-skip-permissions'
```

Then reload your shell (`source ~/.zshrc` or open a new terminal) and use:

```bash
c-dsp
```

**Windows (PowerShell)** — add to your PowerShell profile (`notepad $PROFILE`):

```powershell
function c-dsp { claude --dangerously-skip-permissions @args }
```

---

## Do Ahead or With Claude

These steps are worth doing before the hackathon, but if you haven't done them yet Claude can walk you through them live.

### Buy a Domain

You'll need a domain name for your project. A `.dev`, `.app`, or `.xyz` domain can be had for a few dollars.

**Where to buy:**

- **[Cloudflare Registrar](https://www.cloudflare.com/products/registrar/)** - At-cost pricing, no markup. Convenient if you're already using Cloudflare for DNS.
- **[Namecheap](https://www.namecheap.com)** - Good prices, easy interface.
- **[GoDaddy](https://www.godaddy.com)** - Large selection, frequent promotions.

If you buy from a registrar other than Cloudflare, you'll need to point your domain's nameservers to Cloudflare (Cloudflare will walk you through this when you add the domain).

### Buy VPS Hosting

A VPS (Virtual Private Server) is the approach we'll use in this bootcamp because it gives you full control and works for any project type. There are other paths too — platforms like Vercel + Supabase, Railway, Fly.io, etc. — and Claude can help you explore those if they suit your project better. But a VPS is a solid default that teaches you the fundamentals.

**Recommended providers:**

| Provider | Cheapest Plan | Notes |
|----------|--------------|-------|
| [Hetzner](https://www.hetzner.com/cloud) | ~$4/month (CX22) | Best value. EU and US datacenters. |
| [Hostinger](https://www.hostinger.com/vps) | ~$5/month | Easy setup, good for beginners. |
| [DigitalOcean](https://www.digitalocean.com) | $6/month | Excellent docs and community. |
| [Linode (Akamai)](https://www.linode.com) | $5/month | Reliable, good support. |

All of these are **month-to-month with no commitment** — most bill hourly, so you can spin up a server for the hackathon and delete it the same day if you want. No contracts, cancel any time.

**When creating your server:**

- Choose **Debian 12** (or Ubuntu 24.04 if you prefer)
- The smallest plan is fine to start
- Pick a datacenter close to your users
- Set up SSH key authentication (the provider will walk you through this)

### Set Up DNS

Once you have your server's IP address, configure DNS in Cloudflare:

1. Log into Cloudflare and add your domain (if not already added)
2. Create an **A record** for your root domain:
   - Name: `@`
   - Content: `your.server.ip.address`
   - Proxy status: DNS only (grey cloud) for now
3. Create a **wildcard A record** for subdomains:
   - Name: `*`
   - Content: `your.server.ip.address`
   - Proxy status: DNS only (grey cloud)

The wildcard record means any subdomain (e.g., `api.yourdomain.com`, `staging.yourdomain.com`) will automatically point to your server. This is very handy for running multiple projects or environments on one server.

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

### SSH Key Setup

You'll need an SSH key to connect to your VPS and to push code to GitHub. If you don't already have one:

```bash
# Generate a new SSH key (press Enter to accept defaults when prompted)
ssh-keygen -t ed25519 -C "your-email@example.com"
```

This creates a key pair in `~/.ssh/`:
- `id_ed25519` - your private key (never share this)
- `id_ed25519.pub` - your public key (this is what you share)

**Add your key to GitHub:**

1. Copy your public key: `cat ~/.ssh/id_ed25519.pub`
2. Go to [GitHub > Settings > SSH Keys](https://github.com/settings/keys)
3. Click "New SSH key", paste the key, and save

**Add your key to your VPS** (when you have one):

```bash
# Copy your public key to the server
ssh-copy-id you@your-server-ip
```

If `ssh-copy-id` isn't available (some Windows setups), you can do it manually:

```bash
# Copy the key content
cat ~/.ssh/id_ed25519.pub

# Then on the server, append it to:
# ~/.ssh/authorized_keys
```

**Windows note:** OpenSSH is included in Windows 10/11. Open PowerShell and run `ssh -V` to verify. If it's not available, enable it via Settings > Apps > Optional Features > OpenSSH Client.

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

For reference: here's what Claude will walk you through once you've kicked off a session. You don't need to follow these steps manually — paste the kickoff prompt from [Get Claude Running](#get-claude-running) and Claude will guide you through them.

### Initialize Your Project

Create a new directory for your project and initialize it:

```bash
mkdir my-awesome-project
cd my-awesome-project
git init
```

Then start Claude Code in your project:

```bash
claude
```

### Set Up Agents for Your Project

Inside Claude Code, run:

```
/setup-agents
```

This command analyzes your project and activates the relevant specialist agents. For a new project, it will ask you what you're building and set up the right team.

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

You don't need to intervene between steps. Go get a coffee. When it's done, review the changes with `git diff` and commit when you're satisfied.

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

## Moving to Production

Once your app is working locally, it's time to deploy. This section covers our opinionated production setup.

### Why This Approach

In the professional world, deployment often involves "DevOps" - a whole discipline around automating infrastructure using tools like Docker, Kubernetes, Terraform, CI/CD pipelines, and cloud-specific services (AWS Lambda, Google Cloud Run, etc.). These tools solve real problems at scale, but they also add enormous complexity. For a solo developer or small team, you can easily spend more time configuring infrastructure than building your actual product.

Our approach deliberately avoids all of that. Instead, we use simple, proven Linux tools that have been around for years (in some cases, decades). The philosophy is:

- **No proprietary lock-in.** Everything here runs on any Linux server from any provider. If Hetzner doubles their prices tomorrow, you can move to DigitalOcean in an afternoon. Try doing that with a stack built on AWS-specific services.
- **No containers or orchestration.** Docker and Kubernetes are powerful but add layers of abstraction you don't need for most projects. A systemd service does the same job with zero overhead.
- **No CI/CD pipelines to maintain.** A `just deploy` command that runs rsync and restarts a service is all you need. You can add GitHub Actions later if you want, but it's not required.
- **Debuggable with basic skills.** If something breaks, you SSH in, read the logs, and fix it. No need to understand container networking, pod scheduling, or cloud console dashboards.
- **Battle-tested.** Caddy, systemd, and rsync are mature, well-documented tools used in production by millions of servers. They rarely surprise you.

This is not the "right" approach for every situation - a startup scaling to millions of users will eventually outgrow it. But for getting a project live and keeping it running reliably, it's hard to beat.

### The Stack

| Component | Tool | Purpose |
|-----------|------|---------|
| OS | Debian 12 | Stable, minimal, well-supported |
| Reverse proxy | Caddy | Automatic HTTPS, simple config |
| Process manager | systemd | Service management, auto-restart |
| Logging | journald + logrotate | Centralized logs with rotation |
| Task runner | just | Deployment commands |
| Source control | git | Pull-based deployment |

### Server Directory Layout

```
/home/you/
  repos/
    my-project/           # Git checkout (development/reference)

/srv/
  my-project/             # Production deployment
    current/              # Checked out project files
    Caddyfile             # Project-specific Caddy config
    my-project.service    # systemd unit file (or symlinked)

/etc/caddy/
  Caddyfile               # Main Caddyfile that imports project configs

/var/log/apps/
  my-project.log          # Application logs (with logrotate)
```

### Caddy Configuration

The main Caddyfile at `/etc/caddy/Caddyfile` imports per-project configurations:

```caddyfile
# /etc/caddy/Caddyfile
# Global options
{
    email you@yourdomain.com
}

# Import all project Caddyfiles
import /srv/*/Caddyfile
```

Each project has its own Caddyfile:

```caddyfile
# /srv/my-project/Caddyfile
my-project.yourdomain.com {
    reverse_proxy localhost:8080
}
```

Caddy automatically provisions and renews HTTPS certificates via Let's Encrypt. You don't need to configure certificates manually.

### systemd Service

Each project runs as a systemd service:

```ini
# /srv/my-project/my-project.service
[Unit]
Description=My Project
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/srv/my-project/current
ExecStart=/srv/my-project/current/my-project
Restart=always
RestartSec=5
StandardOutput=append:/var/log/apps/my-project.log
StandardError=append:/var/log/apps/my-project.log

[Install]
WantedBy=multi-user.target
```

Enable and start the service:

```bash
sudo systemctl enable /srv/my-project/my-project.service
sudo systemctl start my-project
```

### Logging with logrotate

Create a logrotate config for your app:

```
# /etc/logrotate.d/my-project
/var/log/apps/my-project.log {
    daily
    rotate 14
    compress
    delaycompress
    missingok
    notifempty
    copytruncate
}
```

View logs:

```bash
# Recent logs
tail -f /var/log/apps/my-project.log

# Or via journald (if not using file logging)
journalctl -u my-project -f
```

### Deployment with just

Each project has a `justfile` with deployment recipes. Here's a template:

```just
# justfile

# Default recipe - show available commands
default:
    @just --list

# Build the project
build:
    go build -o bin/my-project ./cmd/my-project

# Run locally for testing
run: build
    ./bin/my-project

# Run test suite
test:
    go test ./...

# Install/update dependencies
deps:
    go mod tidy

# Deploy to production
deploy: build
    rsync -avz --delete \
        --exclude '.git' \
        --exclude '.env' \
        ./ production:/srv/my-project/current/
    ssh production 'sudo systemctl restart my-project'

# View production logs
logs:
    ssh production 'tail -f /var/log/apps/my-project.log'

# Check production service status
status:
    ssh production 'systemctl status my-project'
```

Install just:

```bash
# macOS
brew install just

# Linux (Debian/Ubuntu)
# See https://github.com/casey/just#installation for options
cargo install just
# Or download a prebuilt binary from the releases page
```

### Deployment Workflow

Putting it all together, deploying looks like this:

```bash
# 1. Make sure tests pass
just test

# 2. Build
just build

# 3. Deploy
just deploy

# 4. Check it's running
just status

# 5. Watch the logs
just logs
```

### First-Time Server Setup

When setting up a new server for the first time:

```bash
# SSH into your server
ssh you@your-server-ip

# Update system
sudo apt update && sudo apt upgrade -y

# Install Caddy
sudo apt install -y debian-keyring debian-archive-keyring apt-transport-https
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | sudo gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | sudo tee /etc/apt/sources.list.d/caddy-stable.list
sudo apt update
sudo apt install caddy

# Create directory structure
sudo mkdir -p /srv
sudo mkdir -p /var/log/apps
sudo chown $USER:$USER /srv

# Set up the main Caddyfile
sudo tee /etc/caddy/Caddyfile << 'EOF'
{
    email you@yourdomain.com
}

import /srv/*/Caddyfile
EOF

# Restart Caddy to pick up config
sudo systemctl restart caddy

# Install just (if deploying from server)
curl --proto '=https' --tlsv1.2 -sSf https://just.systems/install.sh | bash -s -- --to /usr/local/bin
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

### DNS not resolving

After changing DNS in Cloudflare, it can take a few minutes to propagate. Check propagation status at [dnschecker.org](https://www.dnschecker.org).

### Caddy not serving your site

```bash
# Check Caddy status
sudo systemctl status caddy

# Check Caddy logs
sudo journalctl -u caddy -f

# Validate your Caddyfile
caddy validate --config /etc/caddy/Caddyfile
```

### systemd service won't start

```bash
# Check the service status for error details
sudo systemctl status my-project

# Check the logs
sudo journalctl -u my-project --no-pager -n 50

# Make sure the binary exists and is executable
ls -la /srv/my-project/current/my-project
```

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
- [Caddy Documentation](https://caddyserver.com/docs/)
- [just Documentation](https://just.systems/man/en/)
- [Cloudflare DNS Setup](https://developers.cloudflare.com/dns/)

---

## License

MIT
