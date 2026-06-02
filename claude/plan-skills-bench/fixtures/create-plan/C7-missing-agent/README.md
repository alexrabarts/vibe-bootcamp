# Scenario C7 — missing required agent → graceful degradation (create-plan, FEATURE)

Tests how `/create-plan` handles a **required explorer being absent**. A frontend feature
("dark-mode toggle") makes Phase 0 detect that **Oliver** (`oliver-shadcn-ui-builder`) is required.
The harness stages the universal reviewers (Eric/Wigsy/Paige) but **withholds Oliver** — so the
project clearly has agents configured; only the needed explorer is missing.

## Expected behavior (revised after a live capture)

Originally this scenario expected a hard STOP. A live run showed — and we decided this is the
*correct* behavior — that the skill instead **gracefully degrades**: it detects Oliver is missing,
notes the deviation, substitutes the generic `Explore` agent, and proceeds to a full plan. Hard-
stopping a tightly-scoped two-file change to force agent setup is heavy-handed.

So the scenario now tests detect → acknowledge → degrade-and-proceed:
- L1 `mode_correct` = FEATURE; `plan_written`
- L2 `degraded_gracefully` (proceed + acknowledge Oliver by name + note the substitution; do **not**
  silently ignore it), plus the usual FEATURE checks (sections, >=3 approaches, matrix, checkpoint)

The failure modes are: **silently ignoring** the missing agent, or **hard-stopping** with no plan.

## Harness note

Install `agents_required` + universal reviewers EXCEPT `agents_withheld` (Oliver withheld). The
contrast scenario for a genuine hard-stop expectation is **I6** (implement-plan), kept as a stop
gate pending live evidence of what implement-plan does with a missing *implementer*.

## How to run

Copy `repo/` to a sandbox, stage the roster minus Oliver, feed `input.md` to `/create-plan`, grade
against `answer-key.md`. (`runner.capture` does the staging automatically.)
