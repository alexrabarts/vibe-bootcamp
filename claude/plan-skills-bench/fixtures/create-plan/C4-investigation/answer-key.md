# Answer key — C4

```yaml
scenario_id:        C4
skill:              create-plan
mode_expected:      INVESTIGATION
agents_required:    [shane]
expected_gate:      proceed
checkpoint_expected: skip
expected_output_shape: "INVESTIGATION FINDINGS: answered questions + open questions + next-step OPTIONS. NOT an implementation plan with file changes or a chosen fix."
penalize_if:
  - "The output contains an Implementation Plan with concrete file changes."
  - "The output commits to a specific fix/solution rather than offering options."
```

## ground_truth_flow (judge checks the explanation against this)

1. `RequireAuth` (`middleware.go`) validates the access token on every request via
   `verifyAccessToken`. On any failure — including an expired access token — it returns 401 and
   does **not** refresh inline.
2. `verifyAccessToken` (`jwks.go`) checks the token signature against a JWKS key set cached for
   10 minutes. Access tokens are short-lived (~15 min). The JWKS cache TTL is how key rotation
   propagates: a rotated key is picked up on the next cache refresh.
3. On a 401 the client calls `Refresh` (`refresh.go`), which looks up the refresh token, rejects it
   if revoked or expired, **rotates** it (single-use: revoke the presented token, issue a new one),
   and issues a fresh access token.

## Notes

- The headline check is behavioral: the run stays investigative. `no_premature_solution` fails if it
  prescribes a fix.
- The findings-accuracy judge scores how faithfully the explanation matches `ground_truth_flow`
  (the inline-refresh-vs-401 behavior, the 10-min JWKS cache as the rotation mechanism, and
  single-use refresh rotation are the three points most often gotten wrong).
- `mode_correct` = INVESTIGATION. If the skill classifies this as DEBUGGING or FEATURE and produces
  a fix plan, that is both a `mode_correct` fail and a `no_premature_solution` fail.
