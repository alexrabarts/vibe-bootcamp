# Scenario C8 — surface-level trap (create-plan, DEBUGGING)

Tests the skill's stated **anti-surface-level mandate**: does it enumerate alternatives and trace
inward to the real cause, or does it anchor on the obvious suspects the bug report dangles?

## The trap

The bug report (`repo/README.md`) explicitly names two recent changes as suspects — a role check
added to the handler and a tightened `COUNT` query. Both are **decoys**. The real cause is two
layers down in `timewindow.day_bounds()`: the current-day window's `end` is clamped to a
mis-adjusted "now" that lands `TENANT_UTC_OFFSET_HOURS` in the past, silently dropping the most
recent events. The symptom profile (today undercounts, worst in the morning, shrinks through the
day, older days correct, reproduces on UTC servers) points at a fixed excluded tail — not at auth
or at the aggregate.

A surface-level run will rank a decoy as primary. A correct run ranks the `day_bounds` clamp as
primary, with the decoys considered and demoted on evidence.

## What it scores

- L1 `mode_correct` = DEBUGGING
- L2 `option_count` (>=3 hypotheses), `sections_present`, `checkpoint_format`
- L3 `correct_primary` (the headline — must be the `day_bounds` clamp, not a decoy),
  `evidence_grounding` (file:line trace inward), `distinctness`, `checkpoint_leverage`

## Phase 2.5 expectation

`checkpoint_expected: fires`. The load-bearing fork is **UTC calendar day vs tenant-local day**,
because it changes the fix size. `scripted-answers.json` answers "tenant-local day", which makes
the correct fix the larger one (build the whole window in tenant tz, convert to UTC, clamp `end`
to the real current instant).

## How to run

1. Copy `repo/` into a fresh sandbox.
2. Feed `input.md` to `/create-plan`.
3. Intercept Phase 2.5 questions with `scripted-answers.json`.
4. Grade the emitted plan against `answer-key.md` using the rubric in `../../../SPEC.md` and the
   judges in `../../../judges/create-plan-quality.md`.
