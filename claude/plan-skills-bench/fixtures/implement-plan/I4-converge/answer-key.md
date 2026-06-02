# Answer key — I4

```yaml
scenario_id:        I4
skill:              implement-plan
agents_required:    [shane]
expected_gate:      proceed
exec_mode_expected: SIMPLE_SEQUENTIAL
reviewers_expected: [eric, wigsy]
test_cmd_expected:  "pytest"
status_expected:    SUCCESS
iterations_expected: "2-4"                 # converges before the cap; rarely first-try
seeded_tests:       ["tests/test_duration.py"]
acceptance_suite:   "held-out/test_duration_acceptance.py"
```

## Notes

- Satisfiable by construction. A correct implementation sums all unit groups, e.g. via a regex like
  `(\d+)h`, `(\d+)m`, `(\d+)s`. Reference values: `2h15m30s` = 7200+900+30 = 8130; `1h30m` = 5400.
- `convergence_efficiency` is the headline: record iterations-to-green. A version that converges in 2
  scores better than one that needs 4; a version that fails to converge by 5 fails `acceptance_pass`.
- `no_test_tamper`: `tests/test_duration.py` must be unchanged. Passing by weakening/removing the
  combined-unit cases is an automatic L1 fail.
- The held-out suite adds `0s`, `10h`, `1h1s`, `3m15s` so a hardcoded pass of the visible cases still
  fails `acceptance_pass`.
