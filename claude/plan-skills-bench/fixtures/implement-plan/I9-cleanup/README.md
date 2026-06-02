# Scenario I9 — cleanup + commit discipline (implement-plan)

Tests the Phase 4 post-conditions: after the run, **zero orphaned worktrees/branches** and changes
**left uncommitted** (the spec instructs implementers not to commit). Two independent backend modules
in different directories give the skill the option to parallelize within the agent (FULL_PARALLEL,
the harder cleanup path) — but the invariant must hold regardless of the mode chosen.

## What it scores

- **L1 `clean_state`** (headline): no `impl-*` worktrees remain (`git worktree list`), no work-item
  or `*-merged-batch*` branches remain (`git branch`), and `git status` shows uncommitted changes.
- L2 `test_cmd_correct` = pytest
- L3 `acceptance_pass` (**deterministic**): both held-out suites pass

## Notes

If the skill picks FULL_PARALLEL, this exercises the most complex cleanup (per-work-item worktrees +
intermediate merged-batch branches). If it picks SIMPLE_SEQUENTIAL, the end state is trivially clean.
Either is acceptable — the gate is about the *end state*, not the mode. A runner that wants to save
cost can attach these same post-condition assertions to the I2/I3 runs instead of running I9 standalone.

## How to run

Copy `repo/` to a sandbox (`git init && commit` baseline), install Shane, feed `plan.md` to
`/implement-plan`. After: assert worktree/branch/commit post-conditions, run both held-out suites,
grade against `answer-key.md`.
