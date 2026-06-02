# Scenario C4 — investigation only (create-plan, INVESTIGATION)

Tests INVESTIGATION-mode classification and the discipline of **not proposing a fix**. The user
explicitly asks to understand the auth token refresh flow before any changes. A surface-level run
jumps to "here's what I'd change"; a correct run documents the flow accurately and offers
*next-step options* without committing to an implementation.

## What it scores

- L1 `mode_correct` = INVESTIGATION; `plan_written` (an `investigate-*.md` file)
- **C4-specific gate `no_premature_solution`**: the output must NOT contain an implementation plan
  with concrete code changes / a chosen fix. Offering next-step options is allowed; prescribing a
  solution is not.
- L2 is **relaxed**: the implementation-plan schema does not apply. Instead check the investigation
  output shape (findings + answered questions + open questions + next-step OPTIONS).
- L3 `evidence_grounding` (file:line trace) and a findings-accuracy judge against `ground_truth_flow`
  (reuse the `criteria_met`-style framing: does the explanation match reality?).

## Phase 2.5 expectation

`checkpoint_expected: skip` — the user wants understanding, not decisions.

## How to run

Copy `repo/` to a sandbox, feed `input.md` to `/create-plan`, grade against `answer-key.md`. Pay
special attention to the `no_premature_solution` gate.
