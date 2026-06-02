# Answer key — C1

```yaml
scenario_id:        C1
skill:              create-plan
mode_expected:      DEBUGGING
agents_required:    [shane]
expected_gate:      proceed
true_primary:       "average_rating uses floor division (total // len(scores)), truncating the mean to an integer, so averages read low and always land on whole numbers."
true_primary_locus: "ratings.py:average_rating (return total // len(scores))"
decoys:
  - "The approved-only filter in store.fetch_review_scores is excluding reviews and dragging the average down."
  - "Serialization/rounding in the handler truncates the value."
  - "A stale cache is returning old averages."
checkpoint_expected: skip
```

## Notes

- The fix is to use true division and round for display: `round(total / len(scores), 1)` (or
  return the float and round in serialization). A plan that does this is correct.
- The skill still must enumerate >=3 hypotheses (its DEBUGGING mandate) even though the cause is
  clear; ranking the floor division as PRIMARY with evidence is what matters.
- `correct_primary` = 1 if the plan blames the approved-filter (decoy), the cache, or serialization.
- Acceptable to ask at most one display-precision question; asking more (or asking which behavior is
  "correct" when it isn't ambiguous) is over-asking and scores `checkpoint_leverage` low.
