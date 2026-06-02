# Scenario C2 — multi-domain feature (create-plan, FEATURE)

Tests multi-domain agent detection, the >=3-approaches + comparison-matrix requirement, and that
Dan's DB review fires for new schema. The "saved filters" feature spans API (Go), DB (Postgres),
and UI (React), so Phase 0 must detect **Shane + Oliver + Dan**.

## The feature

Users want to save a named set of dashboard filters and re-apply it later. Critically, the request
states saved filters must **follow the user across devices** — which rules out a localStorage-only
approach and forces server-side persistence. That constraint gives the judge a checkable
correctness signal for `correct_primary`.

## What it scores

- L1 `mode_correct` = FEATURE; `plan_written`
- L2 `sections_present`, `option_count` (>=3 approaches), **`comparison_matrix`** present,
  `checkpoint_format`
- L3 `distinctness` (3 mechanistically distinct approaches), `correct_primary` (server-persisted;
  localStorage-only is wrong), `checkpoint_leverage`, `actionability`
- Detection checks (assert from the Phase 0 report / agent invocations): Shane + Oliver + Dan
  detected; Dan's DB review fires.

## Phase 2.5 expectation

`checkpoint_expected: fires`. Forks: schema shape (JSON blob vs normalized) and v1 scope
(private vs shareable). `scripted-answers.json` picks JSON blob + private-for-v1.

## How to run

Copy `repo/` to a sandbox, install Shane + Oliver + Dan, feed `input.md` to `/create-plan`,
intercept Phase 2.5, grade against `answer-key.md`.
