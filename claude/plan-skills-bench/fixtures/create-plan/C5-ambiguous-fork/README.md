# Scenario C5 — load-bearing fork, checkpoint fires (create-plan, DEBUGGING)

Tests that Phase 2.5 **fires correctly** and in the right format when the fix genuinely depends on
decisions not visible in the code. The contrast scenario to C6 (which must skip).

## The setup

Weekly digest ("report") emails arrive on the wrong day for users in various timezones.
`scheduler/digest.go:nextSendTime` computes the send time in the **server** timezone, ignoring the
user's. The correct fix depends on three things the code can't tell you:

1. **Week/day boundary** — should "weekly, Monday morning" mean the *user's* local Monday or
   server/UTC Monday? (Flips the whole fix.)
2. **Terminology** — the user says "report"; the code says "digest". Confirm they're the same thing.
3. **Scope** — fix only weekly, or all cadences (daily/monthly share `nextSendTime`)?

A correct run asks 2-4 of these as one-decision questions; a surface-level run picks a tz behavior
unilaterally and plans the wrong fix.

## What it scores

- L1 `mode_correct` = DEBUGGING; `plan_written`
- L2 `option_count` (>=3 hypotheses), `sections_present`, **`checkpoint_format`**: <=4 questions,
  one decision each, first option flagged "(Recommended)", asked sequentially
- L3 **`checkpoint_leverage`** (headline — the questions must be the load-bearing forks above, not
  trivia), `correct_primary` (tz handling in `nextSendTime`), `evidence_grounding`

## Phase 2.5 expectation

`checkpoint_expected: fires`. `scripted-answers.json` resolves: user-local week, "report"=="digest",
weekly-only scope.

## How to run

Copy `repo/` to a sandbox, feed `input.md` to `/create-plan`, intercept Phase 2.5 with
`scripted-answers.json`, grade against `answer-key.md`.
