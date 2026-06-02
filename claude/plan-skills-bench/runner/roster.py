"""Stage the per-scenario agent roster into a sandbox's project-local .claude/agents/.

The skills check `.claude/agents/` (in cwd) during Phase 0 and STOP if a required explorer is
missing. For a live "proceed" capture we therefore stage `agents_required` plus the universal
reviewers, minus `agents_withheld` — so the run has the agents it needs, while STOP-gate scenarios
keep their withheld agent genuinely absent.
"""

from __future__ import annotations

import shutil
from pathlib import Path

# short name (as used in answer-key `agents_required`) -> agent file stem
AGENT_FILES = {
    "shane": "shane-go-backend-dev",
    "oliver": "oliver-shadcn-ui-builder",
    "dan": "dba-dan-database-expert",
    "eric": "eric-strategic-architect",
    "wigsy": "wigsy-code-reviewer",
    "paige": "paige-technical-docs-writer",
    "proompty": "proompty-mc-proomptface-prompt-engineer",
    "amber": "amber-ux-designer",
    "david": "david-product-requirements-architect",
    "sarah": "sarah-q-lewis-data-analyst",
}

# reviewers the skills always (or conditionally) invoke; harmless to stage everywhere
UNIVERSAL = ["eric", "wigsy", "paige"]

DEFAULT_SOURCES = (
    Path.home() / ".claude" / "agents-library",
    Path.home() / ".claude" / "agents",
)


def roster_for(scenario) -> list[str]:
    """Short agent names to stage for a scenario: required + universal, minus withheld."""
    withheld = {a.lower() for a in scenario.agents_withheld}
    want = list(dict.fromkeys([*scenario.agents_required, *UNIVERSAL]))  # dedup, keep order
    return [a for a in want if a.lower() not in withheld]


def resolve_agent_file(full_name: str, sources=DEFAULT_SOURCES) -> Path | None:
    for base in sources:
        p = Path(base) / f"{full_name}.md"
        if p.exists():
            return p
    return None


def stage_roster(sandbox_path, names, sources=DEFAULT_SOURCES) -> tuple[list[str], list[str]]:
    """Copy the named agents (short names) into <sandbox>/.claude/agents/.

    Returns (staged, missing) full-name lists. `missing` are agents whose source file wasn't found.
    """
    dest = Path(sandbox_path) / ".claude" / "agents"
    dest.mkdir(parents=True, exist_ok=True)
    staged, missing = [], []
    for short in names:
        full = AGENT_FILES.get(short.lower(), short)
        src = resolve_agent_file(full, sources)
        if src:
            shutil.copyfile(src, dest / f"{full}.md")
            staged.append(full)
        else:
            missing.append(full)
    return staged, missing
