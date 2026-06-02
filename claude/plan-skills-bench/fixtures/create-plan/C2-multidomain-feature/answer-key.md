# Answer key — C2

```yaml
scenario_id:        C2
skill:              create-plan
mode_expected:      FEATURE
agents_required:    [shane, oliver, dan]
expected_gate:      proceed
true_primary:       "Persist saved filters server-side: a new table, CRUD API endpoints, and UI to save/apply. Client-only/localStorage storage is ruled out by the explicit cross-device requirement."
true_primary_locus: "new: migration (saved_filters table); api/handlers + api/store (CRUD); web (save/apply UI + api.ts client)"
decoys:
  - "Store saved filters in localStorage only (fails the cross-device requirement)."
checkpoint_expected: fires
checkpoint_required_forks:
  - "Schema shape: JSON blob column vs normalized criteria tables."
  - "v1 scope: private to the user vs shareable between users."
required_detections:
  - "Shane (Go backend) detected"
  - "Oliver (React frontend) detected"
  - "Dan (Postgres) detected AND Dan's DB review fires (new table)"
required_artifacts:
  - ">=3 distinct approaches"
  - "a comparison matrix across the approaches"
```

## Notes

- Three genuinely distinct approaches exist: (a) JSON blob column on a `saved_filters` table;
  (b) normalized schema (`saved_filter` + `saved_filter_criteria`); (c) client-side with server
  sync. All three are server-backed or sync to the server — a localStorage-only design is NOT a
  valid recommendation here.
- `correct_primary`: `matches_answer_key` is true iff the recommended approach persists across
  devices (server-side). Recommending localStorage-only = false.
- `distinctness`: penalize if the "approaches" are three variants of the same storage choice.
- Detection is gradeable from the Phase 0 report and the set of agents actually invoked; Dan must be
  consulted for the new table.
