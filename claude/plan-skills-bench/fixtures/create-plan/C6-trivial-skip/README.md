# Scenario C6 — trivial fix, checkpoint skips (create-plan, DEBUGGING)

Tests that Phase 2.5 **correctly skips** on a trivial, single-cause bug and logs the skip line —
and that the skill does not interrogate the user about a fix with no load-bearing decision.

## The bug

`HEALTHCHECK_TIMEOUT_SECONDS` is set to `0.001` (1 ms), so every upstream probe times out before any
real upstream can respond and `check_upstream` always returns `False`. One-line config fix, no
product decision involved.

## What it scores

- L1 `mode_correct` = DEBUGGING; `plan_written`
- L2 `option_count` (>=3 hypotheses per the DEBUGGING mandate), `sections_present`,
  **`checkpoint_format` (the skip line `[Phase 2.5] Skipped...` must be logged)**
- L3 `correct_primary` (the 1 ms timeout), `checkpoint_leverage` — **score 1 if it asked any
  question** (over-asking on a trivial fix is the failure mode this scenario hunts)

## Phase 2.5 expectation

`checkpoint_expected: skip`. The contrast scenario to C5/C8 (which must fire).

## How to run

Copy `repo/` to a sandbox, feed `input.md` to `/create-plan`, grade against `answer-key.md`.
