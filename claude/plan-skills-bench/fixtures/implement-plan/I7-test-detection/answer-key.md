# Answer key — I7

```yaml
scenario_id:        I7
skill:              implement-plan
agents_required:    [shane]
expected_gate:      proceed
status_expected:    SUCCESS
variants:
  - dir: "variants/justfile-repo"
    exec_mode_expected: SIMPLE_SEQUENTIAL
    test_cmd_expected:  "just test"        # justfile `test:` -> priority 1, must beat pytest
  - dir: "variants/npm-repo"
    exec_mode_expected: SIMPLE_SEQUENTIAL
    test_cmd_expected:  "npm test"         # package.json test script
  - dir: "variants/go-repo"
    exec_mode_expected: SIMPLE_SEQUENTIAL
    test_cmd_expected:  "go test ./..."    # go.mod
```

## Notes

- Run the skill once per variant directory; `test_cmd_correct` is checked per variant.
- The justfile variant is the discriminating case: a bare pytest config is also present, so reporting
  `pytest` instead of `just test` is a detection failure (justfile is higher priority).
- `acceptance_pass` (the trivial `add(2,3)==5`) is secondary; the scenario exists to test detection.
