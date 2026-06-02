# Answer key — C5

```yaml
scenario_id:        C5
skill:              create-plan
mode_expected:      DEBUGGING
agents_required:    [shane]
expected_gate:      proceed
true_primary:       "nextSendTime computes the send time in the server timezone, ignoring the user's timezone, so weekly digests fire at the server-local weekday/hour rather than the user's local Monday morning."
true_primary_locus: "scheduler/digest.go:nextSendTime"
decoys:
  - "The scheduler cron interval is wrong / off-by-one day."
  - "The stored SendWeekday is incorrect for the affected users."
checkpoint_expected: fires
checkpoint_required_forks:
  - "Week/day boundary in user-local time vs server/UTC time (changes the fix)."
  - "Terminology: confirm the user's 'report' == the code's 'digest'."
  - "Scope: fix weekly only, or all cadences (daily/monthly share nextSendTime)?"
```

## Notes

- The defining behavior is that Phase 2.5 fires with load-bearing questions. `checkpoint_leverage`
  should score high only if the questions map to the forks above; generic or code-answerable
  questions score low.
- `checkpoint_format` must hold: <=4 questions, exactly one decision per question, first option
  flagged "(Recommended)", asked one at a time (sequential).
- Given the scripted answers (user-local week, weekly-only), the PRIMARY fix is to compute
  `nextSendTime` in the user's timezone for the weekly cadence.
- `correct_primary` = 1 if the plan blames the cron interval or the stored weekday (decoys) instead
  of the timezone handling.
