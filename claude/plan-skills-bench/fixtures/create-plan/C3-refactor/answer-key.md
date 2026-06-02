# Answer key — C3

```yaml
scenario_id:        C3
skill:              create-plan
mode_expected:      REFACTOR
agents_required:    [shane]
expected_gate:      proceed
true_primary:       "Split build_report into separate fetch / transform-format / export responsibilities and reuse utils.format_currency instead of the inline duplicate; remove the dead code identified below."
true_primary_locus: "reports.py:build_report"
cruft_to_find:
  - "Dead function legacy_export (never called)."
  - "Unused import: datetime."
  - "Inline currency formatting in build_report duplicates utils.format_currency (DRY)."
  - "Commented-out PDF experiment in the else branch."
  - "Stale TODO referencing the completed 2024-01 migration."
checkpoint_expected: fires
checkpoint_required_forks:
  - "Risk appetite: behavior-preserving incremental extraction vs a larger module/class restructure."
required_artifacts:
  - ">=3 distinct refactoring strategies"
  - "a comparison matrix across strategies"
```

## Notes

- Three genuinely distinct strategies: (a) incremental extract-function (low risk, same module);
  (b) split into fetch/transform/export modules; (c) introduce a Report pipeline/class abstraction.
  `distinctness` penalizes presenting one plan under three risk labels.
- Cruft check is partly deterministic: scan the plan text for mentions of `legacy_export` and the
  duplicated `format_currency` logic at minimum. A strong run names all five items in `cruft_to_find`.
- Given the scripted answer (behavior-preserving/incremental), the recommended strategy should be
  the low-risk extraction with a test-characterization step, not a rewrite.
