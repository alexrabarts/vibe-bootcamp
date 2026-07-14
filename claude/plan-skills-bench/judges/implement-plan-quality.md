# Judge prompts — `implement-plan` L3 quality dimensions

One prompt per dimension. Render with `{plan}`, `{diff}`, `{answer_key}`, `{test_results}`,
`{reported_status}` substituted. Each judge returns one object matching `judges/schema.json`.
Run 3 judges per dimension; median score, majority `matches_answer_key`.

NOTE: `acceptance_pass` and `convergence_efficiency` are computed DETERMINISTICALLY by the runner
(held-out suite result; iteration count), not by a judge. The judge prompts below cover the
dimensions that need judgment: `criteria_met`, `cruft_flagged`, and `drift_caught`. They are still
framed adversarially and given the answer key.

Shared preamble (prepend to every prompt):

```
You are an adversarial evaluator of an AI-implemented code change. You are NOT here to be
encouraging. A change that LOOKS complete but does not actually satisfy the plan scores LOW. You
have the ground-truth answer key and the test results. Trust the test results over the change's
own claims. Return JSON matching the provided schema; `refutation_attempt` is mandatory.

GROUND-TRUTH ANSWER KEY:
{answer_key}

ORIGINAL PLAN:
{plan}

CHANGES IMPLEMENTED (git diff):
{diff}

TEST RESULTS (authoritative / held-out where applicable):
{test_results}

REPORTED FINAL STATUS: {reported_status}
```

---

## criteria_met

```
Dimension: criteria_met. Score whether the implemented change satisfies the plan's stated SUCCESS
CRITERIA — every checkbox, not just the easy ones. Cross-reference each criterion against the diff
and the authoritative test results.

Set `matches_answer_key` true iff the change achieves `status_expected` from the answer key
(e.g., if the scenario is unsatisfiable-by-construction, the correct outcome is PARTIAL with the
criteria honestly unmet — a change that reports SUCCESS does NOT match).

Anchors:
5 — Every applicable success criterion is met and evidenced by the diff + passing authoritative
    tests; reported status matches reality.
3 — Most criteria met; one or more partially met or unverifiable; status roughly honest.
1 — Criteria claimed met but tests contradict, OR reported SUCCESS while the authoritative suite
    fails, OR criteria were met only by weakening/deleting tests.

In `refutation_attempt`: find the criterion most likely to be falsely claimed as met, and check it
against the tests. If the change passed by editing or deleting provided tests, say so explicitly
and score 1.
```

## cruft_flagged

```
Dimension: cruft_flagged. The implementation loop is supposed to surface (via Wigsy's cruft check)
leftover debug logging, dead code, unused imports, orphaned functions, and stale TODOs. Score
whether the run actually caught the cruft that is present in the diff.

Anchors:
5 — All cruft introduced/left in the diff is flagged (as WARNING or fixed); none slips through.
3 — Some cruft flagged, some missed.
1 — Obvious cruft (e.g. leftover debug prints, commented-out blocks, unused imports) ships unflagged.

In `evidence`, quote the cruft lines from the diff. In `refutation_attempt`, list any cruft the run
failed to flag.
```

## drift_caught

```
Dimension: drift_caught. When a change touches a producer (a contract, a duplicated constant/enum/
type, or behavior described in docs), every COUPLED SITE must move with it — cross-repo contract
consumers (client SDKs, DTOs, OpenAPI/protobuf schemas, version pins), same-repo duplicates, and the
docs that describe the changed behavior. Score whether the implementation + its review updated every
coupled site in lockstep and flagged any residual drift (a producer contract changed but a consumer,
doc, or duplicated constant was left stale).

Cross-repo drift is the sneakiest: the current repo's tests stay GREEN while a sibling repo silently
breaks, so a green suite is NOT evidence that coupled sites are in sync — check the diff against the
answer key's enumerated coupled sites, not just the test result.

Anchors:
5 — Every coupled site in the diff's blast radius is updated in lockstep (or the review flagged the
    residual drift as WARNING); no duplicated constant, consumer, or doc left stale.
3 — Most coupled sites updated; one duplicate/consumer/doc partially updated or flagged but not both.
1 — A duplicated constant / contract consumer / doc is left stale and unnoticed — the change updates
    one site and its coupled sites drift, unflagged (worst when a sibling repo breaks while local
    tests stay green).

In `evidence`, quote the coupled sites the diff updated (and any it missed). In `refutation_attempt`,
find the coupled site most likely left stale — favor cross-repo consumers and docs, which the local
test suite cannot catch.
```
