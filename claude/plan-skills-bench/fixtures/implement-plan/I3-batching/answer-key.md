# Answer key — I3

```yaml
scenario_id:        I3
skill:              implement-plan
agents_required:    [shane]
expected_gate:      proceed
exec_mode_expected: FULL_PARALLEL          # single agent, within-agent parallelization across batches
reviewers_expected: [eric, wigsy]
test_cmd_expected:  "pytest"
status_expected:    SUCCESS
iterations_expected: "1-2"
seeded_tests:       []
acceptance_suite:   "held-out/test_report.py"
batching_expected:  "report (Batch 2) runs AFTER both users_source and orders_source (Batch 1); tests last."
```

## Notes

- `batching_correct` is the hard check: `report.py` depends on both sources and must be scheduled
  after them. Building it in the first batch, or before a source, is a batching failure.
- `mode_correct`: FULL_PARALLEL is expected (one agent, parallelizable Batch 1). SIMPLE_SEQUENTIAL is
  acceptable if the skill judges three small items not worth worktrees — but the dependency ordering
  (report after sources) must hold either way.
- If FULL_PARALLEL is chosen, `clean_state` exercises the harder cleanup path (work-item worktrees +
  `*-merged-batch*` branches). All must be removed; changes left uncommitted.
- Reference result: `{"u1": 15.0, "u2": 0.0}` — u1 = 10.0+5.0, u2 = no orders → 0.0, u3 inactive.
