# Answer key — I8b (internal bugfix)

```yaml
scenario_id:        I8b
skill:              implement-plan
agents_required:    [shane]
expected_gate:      proceed
exec_mode_expected: SIMPLE_SEQUENTIAL
reviewers_expected: [eric, wigsy]          # internal bugfix, no new surface -> Paige SKIPPED
test_cmd_expected:  "pytest"
status_expected:    SUCCESS
iterations_expected: "1-2"
seeded_tests:       ["tests/test_clamp.py"]
acceptance_suite:   null                    # the provided visible test is authoritative; anti-tamper applies
paige_warranted:    false
```

## Notes

- The discriminating check is `reviewers_correct`: Paige must NOT be invoked — a bug fix to an
  internal helper introduces no new user-facing surface. Invoking Paige here is the failure this
  sub-fixture hunts (the mirror of 8a).
- `no_test_tamper`: the fix must change `clamp.py`, not `tests/test_clamp.py`. Passing by editing the
  test is an automatic L1 fail.
- The fix: return `hi` when `x > hi`. After the fix the provided suite (including
  `clamp(10, 0, 5) == 5`) passes.
