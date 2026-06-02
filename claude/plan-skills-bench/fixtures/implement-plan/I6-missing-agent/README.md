# Scenario I6 — missing-agent STOP gate (implement-plan)

The implement-plan counterpart to create-plan's C7. The plan needs a frontend implementer (Oliver),
but the harness installs a roster that **withholds Oliver**. The skill must STOP at Phase 0, emit the
`/setup-agents` instruction, and make **no changes** to the repo.

## What it scores

- **L1 `stop_gate`** (headline): halts at Phase 0 with the `/setup-agents oliver-shadcn-ui-builder`
  instruction, AND the sandbox is pristine (no files changed, no worktrees created).
- Failure mode: proceeding to plan review / implementation despite the missing agent.

## Harness note

Install everything in `agents_required` EXCEPT what's in `agents_withheld` (here: withhold Oliver).

## How to run

Copy `repo/` to a sandbox, install a roster without Oliver, feed `plan.md` to `/implement-plan`.
Assert the STOP + pristine sandbox. Grade against `answer-key.md`.
