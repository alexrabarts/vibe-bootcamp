# Scenario C1 — clear-cause debug (create-plan, DEBUGGING)

The happy-path debug case: the root cause is genuinely clear once you read the code. Tests whether
the skill executes its structured DEBUGGING flow (classify, enumerate >=3 hypotheses, rank with
evidence, write a plan) **without over-thinking** a simple bug — and lands the primary on the real
cause, not the plausible decoy the report dangles.

## The bug

Product average ratings read too low and always land on whole numbers. `ratings.average_rating`
uses floor division (`total // len(scores)`), truncating the mean to an int. The report mentions
that approved-only filtering is *correct* behavior — a deliberate decoy pointing at `store.py`.

## What it scores

- L1 `mode_correct` = DEBUGGING; `plan_written`
- L2 `option_count` (>=3 hypotheses), `sections_present`, `checkpoint_format` (skip logged)
- L3 `correct_primary` (must be the floor division, not the approved-filter decoy),
  `evidence_grounding`, `distinctness`

## Phase 2.5 expectation

`checkpoint_expected: skip` — single clear cause, no load-bearing fork. Asking a display-precision
question is tolerated (the answerer has a rule for it) but the skip path is preferred; gratuitous
questioning is penalized by `checkpoint_leverage`.

## How to run

Copy `repo/` to a sandbox, feed `input.md` to `/create-plan`, grade against `answer-key.md`.
