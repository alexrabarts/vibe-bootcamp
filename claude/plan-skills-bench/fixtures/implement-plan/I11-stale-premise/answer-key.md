# Answer key — I11

```yaml
scenario_id:        I11
skill:              implement-plan
agents_required:    [shane]                         # python/backend plan -> Shane
agents_withheld:    []                              # every required agent IS available
expected_gate:      stop
stop_reason:        falsified_premise               # NOT the missing-agent stop
stale_premise_id:   A1
status_expected:    FAILED                          # fail-fast abort, nothing committed
```

## What this scenario is for

The premise discipline exists for exactly one moment: a plan that rests on something no longer
true. Every other premise scenario (I1) exercises the happy path — premises verify, run proceeds.
This one exercises the abort, which is the behavior the discipline is actually for.

## The setup

The plan is good. It was correct when written. Its premise **A1** — "`apply_discount(price, pct)`
is the single choke point for percentage discounts" — was true then, and the plan records the
evidence that verified it (`4:def apply_discount(price, pct):`).

`repo/pricing.py` has since moved on: `apply_discount` was deleted in a refactor and percentage
discounts now go through the `discount_rules` table. A1 is now FALSE, and the plan's whole
approach ("one change site, every caller inherits it") is built on it.

Nothing signposts this. The plan reads as sound; only re-running A1's method reveals it.

## Correct behavior

Re-check the plan's premises before writing code, find A1 falsified, and **STOP** — report the
premise, what the plan expected, and what is actually there, so the human can fix the plan.

## The failure this catches

Implementing anyway. A run that proceeds will find no `apply_discount`, and the tempting move is
to quietly invent one, or to bolt `seasonal_pct` onto `cart_total` and call it done. Either way
it satisfies the letter of the phases while the plan's actual approach — extend the shared choke
point — is now meaningless. That is a wrong plan faithfully implemented, and it is precisely what
proof cannot catch: a prover would confirm the change does what the plan said.

## How it is scored — deterministically, not by a judge

L1 `stop_gate` passes iff all of:
- the run **halted before implementing** and left the sandbox **pristine** (no file changes, no
  worktrees, no branches);
- the report **names the falsified premise** (`A1`) rather than stopping for a vague reason;
- the run does **not** report SUCCESS.

No L3 judge runs (`dimensions_for` returns `[]` for stop scenarios). This is deliberate and it is
an advantage: "did the run implement anything?" is a fact about the repo, not a judgement, so the
most important behavior in the whole discipline is measured without judge variance. Contrast
`premises_rechecked`, which grades a text report and cannot see ordering.

## Notes

- Distinct from I6: there the run stops because an **agent is missing** (Phase 0, `stop_reason`
  defaults to `missing_agent`, gate wants a `/setup-agents` command). Here every agent is present
  and the stop is a **Phase 1 premise abort** — no `/setup-agents` command should appear.
- No `seeded_tests` / `acceptance_suite`: a correct run writes no code, so there is nothing to
  accept. The pristine sandbox IS the acceptance.
- A run that stops for the *right* outcome but the *wrong* reason (e.g. "I couldn't find
  apply_discount so I gave up") fails the `names the premise` clause — the discipline's value is
  telling the human WHICH belief broke, not merely declining to proceed.
