# Answer key — C7

```yaml
scenario_id:        C7
skill:              create-plan
mode_expected:      FEATURE
agents_required:    [oliver]                       # frontend feature -> Oliver detected as required
agents_withheld:    [oliver]                        # harness withholds Oliver; reviewers ARE staged
expected_gate:      proceed                          # graceful degradation, NOT a hard stop (see note)
degradation_expected: true
missing_agent:      oliver                           # whose absence must be acknowledged
checkpoint_expected: fires
```

## What this scenario tests (revised)

Originally C7 expected a hard STOP when a required explorer is missing. A live capture proved the
skill does **not** hard-stop: with Eric/Wigsy/Paige present and only Oliver withheld, `/create-plan`
**detected** the missing explorer, **noted the deviation explicitly**, **substituted the generic
`Explore` agent**, and **proceeded** to a full FEATURE plan — and that graceful degradation is the
*desired* behavior (a hard stop for a tightly-scoped change is heavy-handed).

So C7 now tests **graceful degradation**, not a halt:

- L1 `mode_correct` = FEATURE; `plan_written` (a plan IS produced)
- L2 `degraded_gracefully`: the run must (a) proceed, (b) acknowledge Oliver is missing by name, and
  (c) note the substitution/deviation — i.e. neither silently ignore the gap nor hard-stop. Plus the
  usual FEATURE L2 checks (sections, >=3 approaches, comparison matrix, checkpoint format).

## Failure modes to penalize

- **Silently ignoring** the missing agent (proceeds but never acknowledges Oliver is absent) ->
  `degraded_gracefully` = 0.
- **Hard-stopping** with no plan (the old expectation) -> `plan_written` = false, so L1 fails.
  (If you decide a hard stop IS desired here, flip `expected_gate` back to `stop` and drop the
  degradation fields; the harness still supports the stop path — see I6.)

## Harness note

The one scenario where the installed roster deliberately omits a required agent: install
`agents_required` + universal reviewers EXCEPT `agents_withheld` (so Oliver is genuinely absent while
the reviewers are present — the clean test of the detect-and-degrade behavior).
