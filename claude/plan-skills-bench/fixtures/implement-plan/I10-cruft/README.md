# Scenario I10 — cruft check (implement-plan)

Tests whether Wigsy's CRUFT CHECK actually catches leftover debug logging and dead code. The file the
plan modifies (`contacts.py`) ships with planted cruft in its blast radius: an unused import, a
leftover `print("DEBUG...")`, a dead/superseded function, and a commented-out reference line. A
quality run either removes the cruft (it appears removed in the diff) or Wigsy flags it as WARNING;
shipping it unflagged is the failure.

## What it scores

- L1 `honest_status`, `clean_state`
- L2 `mode_correct` = SIMPLE_SEQUENTIAL, `test_cmd_correct` = pytest
- L3 `acceptance_pass` (**deterministic**: `held-out/test_contacts.py` — confirms `format_phone`
  works and that cleanup did not break `normalize_email`), and **`cruft_flagged`** (the headline:
  were the planted cruft items flagged or removed?)

## Planted cruft (see `answer-key.md` for the list)

`import json` (unused), a `print("DEBUG ...")` in `normalize_email`, a dead `_legacy_format_phone`
(wrong/old format, uncalled), and a commented-out reference line inside `format_phone`.

## How to run

Copy `repo/` to a sandbox, install Shane, feed `plan.md` to `/implement-plan`. After: run the
held-out suite; inspect the diff + Wigsy's review for whether each cruft item was flagged or removed.
Grade against `answer-key.md`.
