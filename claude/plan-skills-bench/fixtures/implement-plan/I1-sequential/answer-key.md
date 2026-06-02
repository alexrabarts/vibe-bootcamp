# Answer key — I1

```yaml
scenario_id:        I1
skill:              implement-plan
agents_required:    [shane]
expected_gate:      proceed
exec_mode_expected: SIMPLE_SEQUENTIAL     # one agent, dependent phases, nothing to parallelize
reviewers_expected: [eric, wigsy]          # no DB, no prompts, no new public surface -> no Paige
test_cmd_expected:  "pytest"
status_expected:    SUCCESS
iterations_expected: "1-2"
seeded_tests:       []
acceptance_suite:   "held-out/test_acceptance.py"
```

## Notes

- `cart_total` depends on `apply_discount`, so the only correct execution mode is SIMPLE_SEQUENTIAL
  (no worktrees). Picking AGENT_PARALLEL/FULL_PARALLEL here is a `mode_correct` fail.
- The change is internal helper functions — no endpoint/CLI/config/README surface — so Paige must be
  skipped. Invoking Paige is a `reviewers_correct` miss.
- `acceptance_pass` is the headline: the held-out suite must pass against the implemented `pricing.py`.
- Reference implementation behavior: `apply_discount(price, pct) == price * (1 - pct/100)`;
  `cart_total(items, d) == apply_discount(sum(items), d)`.
