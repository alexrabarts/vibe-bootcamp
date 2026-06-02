# Scenario C9 — distinctness under temptation (create-plan, FEATURE)

Tests whether the skill generates **>=3 genuinely distinct approaches** for a feature that has one
"obvious" implementation — rather than padding the count with three variants of the same idea. This
is the scenario that exercises the `distinctness` judge hardest.

## The feature

Add full-text search to a notes app. The obvious move is `WHERE content ILIKE '%query%'`. The
request adds scale + ranking ("~50k notes per user, latency matters, search the body, rank
sensibly"), which makes naive substring matching clearly inferior and opens genuinely distinct
designs:

- **Naive ILIKE** on title+body — no ranking, sequential scan, too slow at 50k.
- **Postgres full-text search** — `tsvector` (title+body) + GIN index + `ts_rank`.
- **External search engine** — a dedicated index service; most powerful, most ops overhead.

The padding trap to catch: presenting "ILIKE title", "ILIKE title+body", "ILIKE case-insensitive"
as three "approaches" — that's one idea, not three.

## What it scores

- L1 `mode_correct` = FEATURE; `plan_written`
- L2 `option_count` (>=3 approaches), `comparison_matrix`, `sections_present`, `checkpoint_format`
- L3 **`distinctness`** (headline — must be mechanistically distinct, not LIKE-variants),
  `correct_primary` (Postgres FTS fits the 50k/latency constraint; naive LIKE and external-engine-
  for-v1 are weaker), `actionability`

## Phase 2.5 expectation

`checkpoint_expected: fires`. Forks: Postgres FTS vs external engine (roadmap/scale), and search
scope (title only vs full body). `scripted-answers.json` picks Postgres FTS + full body.

## How to run

Copy `repo/` to a sandbox, install Shane + Dan, feed `input.md` to `/create-plan`, intercept
Phase 2.5, grade against `answer-key.md`.
