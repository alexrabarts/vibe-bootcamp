# Scenario C3 — refactor (create-plan, REFACTOR)

Tests REFACTOR-mode classification, the >=3-strategies requirement, and the skill's dead-code/cruft
identification (its exploration checklist explicitly hunts unused imports, dead code, stale TODOs).

## The target

`reports.py` has a god-function `build_report` that fetches, transforms, formats, and exports in one
body, with currency formatting duplicated from `utils.format_currency`. The file also carries
plantable cruft: a dead `legacy_export` function, an unused `datetime` import, a commented-out PDF
experiment, and a stale TODO referencing a finished migration.

## What it scores

- L1 `mode_correct` = REFACTOR; `plan_written`
- L2 `option_count` (>=3 strategies), `comparison_matrix`, `sections_present`, `checkpoint_format`
- L3 `distinctness` (3 mechanistically distinct strategies — extract-functions vs module-split vs
  pipeline/class abstraction, NOT three risk labels on one plan), `actionability`,
  plus **cruft identification**: the plan's "Code to Remove" / dead-code section should name the
  items in `cruft_to_find` (at minimum `legacy_export` and the duplicated formatting).

## Phase 2.5 expectation

`checkpoint_expected: fires`. Fork: risk appetite — behavior-preserving incremental extraction vs a
larger restructure. `scripted-answers.json` picks behavior-preserving/incremental.

## How to run

Copy `repo/` to a sandbox, feed `input.md` to `/create-plan`, intercept Phase 2.5, grade against
`answer-key.md`.
