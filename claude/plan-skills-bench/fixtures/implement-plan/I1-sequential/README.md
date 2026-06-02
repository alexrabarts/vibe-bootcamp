# Scenario I1 — SIMPLE_SEQUENTIAL happy path (implement-plan)

The simplest successful run: one agent (Shane), two dependent phases, no worktrees, pytest detected,
the held-out acceptance suite passes, status SUCCESS. The baseline every other scenario is measured
against.

## The plan

Implement `apply_discount` (Phase 1) then `cart_total` (Phase 2, which calls `apply_discount`). The
dependency forces sequential execution by a single agent — there is nothing to parallelize.

## What it scores

- L1 `clean_state` (no worktrees created, changes left uncommitted), `honest_status`
- L2 `mode_correct` = SIMPLE_SEQUENTIAL, `test_cmd_correct` = pytest, `reviewers_correct` =
  {eric, wigsy} (internal helpers — no DB, no prompts, no new public surface, so Paige is skipped)
- L3 `acceptance_pass` (**deterministic, headline**): `held-out/test_acceptance.py` passes,
  `criteria_met`

## Notes

The implementer writes its own tests; the harness runs `held-out/test_acceptance.py` (never shown to
the skill) post-hoc as the authoritative outcome signal.

## How to run

Copy `repo/` to a fresh sandbox, install Shane, feed `plan.md` to `/implement-plan`. After the run,
run the held-out suite against `pricing.py` and grade against `answer-key.md`.
