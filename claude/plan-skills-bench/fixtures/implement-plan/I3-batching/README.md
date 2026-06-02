# Scenario I3 — within-agent parallelization + dependency batching (implement-plan)

Tests HYBRID/FULL_PARALLEL execution and correct **dependency batching**: two independent modules
can be built in parallel, but the module that depends on both must run **after** them.

## The plan

One agent (Shane), three phases mirroring the implement-plan spec's own example:
- **Batch 1 (parallel):** `users_source.py` and `orders_source.py` — independent, different files.
- **Batch 2:** `report.py` — imports and depends on **both** sources.
- **Batch 3:** tests.

A correct run schedules `report` only after both sources exist. Building `report` in the first batch
(or before a source) is a batching error.

## What it scores

- L1 `honest_status`, `clean_state` (FULL_PARALLEL exercises the harder cleanup path: work-item
  worktrees + merged-batch branches)
- L2 `mode_correct` (FULL_PARALLEL; SIMPLE_SEQUENTIAL acceptable if it judges the items too small),
  **`batching_correct`** (report after both sources — the hard check), `test_cmd_correct` = pytest
- L3 `acceptance_pass` (**deterministic**): `held-out/test_report.py` passes

## Deterministic data

The source stubs ship seeded module-level data (`_ACTIVE`, `_ORDERS`) so the combined report is
deterministic: active users are `u1`,`u2`; `u1` has orders 10+5, `u2` none, `u3` (inactive) is
excluded → `{"u1": 15.0, "u2": 0.0}`.

## How to run

Copy `repo/` to a sandbox, install Shane, feed `plan.md` to `/implement-plan`. Parse the round/
dependency trace for `batching_correct`, run the held-out suite, grade against `answer-key.md`.
