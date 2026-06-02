# Answer key — I8a (new endpoint)

```yaml
scenario_id:        I8a
skill:              implement-plan
agents_required:    [shane]
expected_gate:      proceed
exec_mode_expected: SIMPLE_SEQUENTIAL
reviewers_expected: [eric, wigsy, paige]   # new public endpoint = new API surface -> Paige warranted
test_cmd_expected:  "pytest"
status_expected:    SUCCESS
iterations_expected: "1-2"
seeded_tests:       []
acceptance_suite:   "held-out/test_widgets.py"
paige_warranted:    true
```

## Notes

- The discriminating check is `reviewers_correct`: Paige MUST be invoked because a brand-new HTTP
  endpoint is new user-facing API surface (per the implement-plan Paige-detection list). Skipping
  Paige here is the failure this sub-fixture hunts.
- `acceptance_pass`: the held-out test finds `("POST", "/api/widgets")` registered and callable.
