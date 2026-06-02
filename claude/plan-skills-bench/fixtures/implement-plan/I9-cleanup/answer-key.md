# Answer key — I9

```yaml
scenario_id:        I9
skill:              implement-plan
agents_required:    [shane]
expected_gate:      proceed
exec_mode_expected: "FULL_PARALLEL or SIMPLE_SEQUENTIAL"   # either acceptable; clean_state must hold regardless
reviewers_expected: [eric, wigsy]
test_cmd_expected:  "pytest"
status_expected:    SUCCESS
iterations_expected: "1-2"
seeded_tests:       []
acceptance_suite:   ["held-out/test_distance.py", "held-out/test_slugify.py"]
```

## Notes

- Headline gate `clean_state`, checked AFTER the run regardless of execution mode:
  - `git worktree list` shows only the main worktree (no `impl-*`).
  - `git branch` shows no work-item branches and no `*-merged-batch*` branches.
  - `git status --porcelain` is non-empty (changes left staged/unstaged, NOT committed).
- Reference behavior: `manhattan((0,0),(3,4)) == 7`; `slugify("Hello, World!") == "hello-world"`;
  `slugify("  a  b  ") == "a-b"`.
- Both held-out suites must pass for `acceptance_pass`.
