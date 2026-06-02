# Scenario I2 — AGENT_PARALLEL (implement-plan)

Tests agent-level parallelization, inter-agent integration, and the reviewer set when work spans two
agents on disjoint files. Backend (Shane) adds an endpoint; frontend (Oliver) adds a component that
calls it. Different directories, no shared files → AGENT_PARALLEL with one worktree per agent.

## What it scores

- L1 `clean_state` (agent worktrees removed, branches deleted, changes uncommitted), `honest_status`
- L2 `mode_correct` = AGENT_PARALLEL, `reviewers_correct` = {eric, wigsy, **paige**} (a new public
  endpoint is new API surface → Paige warranted), `test_cmd_correct` = `just test` (justfile is the
  highest detection priority — it must win over the bare pytest config)
- L3 `acceptance_pass` (**deterministic**, backend): `held-out/test_health_summary.py` passes;
  plus a `frontend_structural_check` (the new component references the endpoint)

## Notes

The backend is independently testable via the held-out pytest suite. The frontend is verified
structurally (a new component imports the API client and references `/api/health/summary`) rather
than via a JS test runner, to keep the acceptance check tractable.

## How to run

Copy `repo/` to a sandbox, install Shane + Oliver, feed `plan.md` to `/implement-plan`. After: assert
no `impl-*` worktrees/branches remain, run the held-out backend suite, run the frontend structural
check, grade against `answer-key.md`.
