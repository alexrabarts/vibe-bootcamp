# Answer key — I10

```yaml
scenario_id:        I10
skill:              implement-plan
agents_required:    [shane]
expected_gate:      proceed
exec_mode_expected: SIMPLE_SEQUENTIAL
reviewers_expected: [eric, wigsy]
test_cmd_expected:  "pytest"
status_expected:    SUCCESS
iterations_expected: "1-2"
seeded_tests:       []
acceptance_suite:   "held-out/test_contacts.py"
cruft_to_find:
  - "Unused import: json."
  - "Leftover debug logging: print('DEBUG normalize_email:', ...) inside normalize_email."
  - "Dead function _legacy_format_phone (uncalled, wrong/old format)."
  - "Commented-out reference line inside format_phone."
```

## Notes

- `cruft_flagged` is the headline L3 dimension. For each item in `cruft_to_find`, a passing run
  either (a) removes it (absent in the final file / shown removed in the diff) or (b) Wigsy flags it
  as WARNING. An item that survives unflagged scores the dimension down.
- The cruft sits in/adjacent to `contacts.py`, which the plan modifies, so it is within the change's
  blast radius and visible to Wigsy's diff-based review.
- `acceptance_pass`: `format_phone("1234567890") == "(123) 456-7890"`, and `normalize_email` still
  works (`"  Foo@Bar.COM " -> "foo@bar.com"`) — i.e. cleaning the debug print must not break it.
