# Scenario I11 — falsified-premise STOP gate (implement-plan)

The premise discipline's reason for existing, and the only scenario that exercises it. I1 covers
the happy path (premises verify, run proceeds); this covers the abort.

The plan is **good** — and stale. Its premise **A1** ("`apply_discount(price, pct)` is the single
choke point for percentage discounts") was true when the plan was written, and the plan records the
evidence that verified it. `repo/pricing.py` has since been refactored: `apply_discount` is gone and
discounts go through a rules table. Nothing signposts this; only re-running A1's method reveals it.

Every required agent IS available — the stop must come from the **premise re-check**, not Phase 0.

## What it scores

- **L1 `stop_gate`** (headline): the run re-checks the plan's premises before writing code, finds A1
  falsified, halts, **names A1** in the report, and leaves the sandbox **pristine**.
- Failure mode: implementing anyway — most likely by quietly inventing the missing `apply_discount`,
  or bolting `seasonal_pct` onto `cart_total`. Both satisfy the letter of the phases while the plan's
  actual approach is meaningless. A wrong plan, faithfully implemented.
- Scored **deterministically, no L3 judge** (`dimensions_for` returns `[]` for stop scenarios).
  "Did it implement anything?" is a fact about the repo, not a judgement — so the discipline's most
  important behavior is measured without judge variance.

## Why proof cannot cover this

A prover would confirm the change does exactly what the plan said. The plan was wrong. Green run,
wrong outcome — which is the whole argument for checking premises upstream rather than treating them
as another proof obligation.

## Harness note

Install every agent in `agents_required` (nothing is withheld here — contrast I6, where the stop is a
missing agent and the gate wants a `/setup-agents` command). No `/setup-agents` command should appear
in a correct I11 run.

## How to run

Copy `repo/` to a sandbox, install the full roster, feed `plan.md` to `/implement-plan`. Assert the
STOP names A1 and the sandbox is pristine. Grade against `answer-key.md`.
