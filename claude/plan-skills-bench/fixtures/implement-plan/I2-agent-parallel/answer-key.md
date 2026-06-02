# Answer key — I2

```yaml
scenario_id:        I2
skill:              implement-plan
agents_required:    [shane, oliver]
expected_gate:      proceed
exec_mode_expected: AGENT_PARALLEL          # two agents, disjoint files
reviewers_expected: [eric, wigsy, paige]    # new public endpoint = new API surface -> Paige warranted
test_cmd_expected:  "just test"             # justfile present -> highest detection priority (beats pytest)
status_expected:    SUCCESS
iterations_expected: "1-2"
seeded_tests:       []
acceptance_suite:   "held-out/test_health_summary.py"
frontend_structural_check:
  - "web/components/ contains a new component (e.g. HealthBadge.tsx) that imports from web/lib/api.ts and references the string '/api/health/summary'."
```

## Notes

- Disjoint directories (`api/` vs `web/`) → AGENT_PARALLEL: one worktree per agent, then inter-agent
  merge. Choosing SIMPLE_SEQUENTIAL forfeits the parallelization this scenario tests (`mode_correct`).
- `test_cmd_correct`: the justfile `test:` recipe must be detected over the bare `pytest` — it is the
  top of the detection priority list. Reporting `pytest` here is a miss.
- Paige is warranted: a brand-new HTTP endpoint is new public surface. Skipping Paige is a
  `reviewers_correct` miss; invoking Dan/Proompty (no DB, no prompts) is also a miss.
- `acceptance_pass` (backend) = the held-out suite finds `/api/health/summary` registered and
  returning a dict with `status`. Frontend correctness is the structural check, not a JS suite.
