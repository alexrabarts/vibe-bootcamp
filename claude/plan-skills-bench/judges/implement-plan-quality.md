# Judge prompts — `implement-plan` L3 quality dimensions

One prompt per dimension. Render with `{plan}`, `{diff}`, `{answer_key}`, `{test_results}`,
`{reported_status}` substituted (plus `{proof_report}` for `proof_discharged` and `{premise_report}`
for `premises_rechecked`). Each judge returns one object matching `judges/schema.json`. Run 3 judges
per dimension; median score, majority `matches_answer_key`.

NOTE: `acceptance_pass` and `convergence_efficiency` are computed DETERMINISTICALLY by the runner
(held-out suite result; iteration count), not by a judge. The judge prompts below cover the
dimensions that need judgment: `criteria_met`, `proof_discharged`, `premises_rechecked`,
`cruft_flagged`, and `drift_caught`. They are still framed adversarially and given the answer key.

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

## proof_discharged

```
Dimension: proof_discharged. The run's proof report — the obligations it established, the method it
ran for each, the raw evidence it recorded, and the verdict it assigned:

{proof_report}

Score whether the run actually PROVED what it claimed, rather than asserting it. Every success
criterion is a proof obligation, discharged by an independent prover exercising the running system
and quoting what it observed. "Implemented, tests pass" is a claim: a change can turn the suite
green while doing nothing the plan asked for. Judge the evidence, never the confidence — and note
that a green authoritative suite is NOT this dimension's answer, since the suite passing is exactly
the claim under suspicion.

What a discharged run looks like: evidence is RAW OUTPUT quoted verbatim (the response body, the
returned rows, the log lines, the printed value), not a paraphrase or an assurance that it worked;
each obligation's evidence would look DIFFERENT if the change were reverted; obligations REFUTED
mid-run were resolved by changing the BEHAVIOR; and every BLOCKED or MANUAL obligation is reported
to the user as NOT PROVEN in its own section rather than folded into the success.

The gaming vectors, in the order they actually occur:
- A REFUTED obligation made to pass by weakening the claim, rewording the obligation, rewriting the
  plan, or special-casing the prover's exact command — instead of fixing the behavior. Obligations
  freeze at the first iteration, so compare the final obligations against the plan's Success
  Criteria and treat any downward drift as this.
- A runnable obligation (an endpoint, a CLI flag, a query, a pure function, a servable page)
  labelled MANUAL or BLOCKED so the work is skipped and the run looks clean.
- Evidence that proves nothing: a green suite standing in for a behavioral claim, a 200 with an
  unchecked body, a screenshot of a page the diff never touched, a log line saying "starting".
- SUCCESS reported over a criterion that was never proven, with no unmissable NOT PROVEN section.

Set `matches_answer_key` true iff the proof outcome agrees with the answer key: the criteria the key
says are achievable are PROVEN on discriminating evidence, and the reported status matches
`status_expected` (an unsatisfiable-by-construction scenario must show the refuted/unproven
obligation and report PARTIAL — a clean sweep of PROVEN verdicts there is itself the failure).

Anchors:
5 — Every success criterion has an obligation; each PROVEN verdict quotes raw output that would
    differ if the change were absent; refutations were resolved by changing behavior; every
    blocked/manual obligation is surfaced to the user as unproven, with what they must do.
3 — Proof is real but partial: some evidence paraphrases rather than quotes, one obligation's method
    is weak enough that a broken implementation would also pass it, or an unproven criterion is
    mentioned but not clearly surfaced as unproven.
1 — SUCCESS reported with a silently unproven criterion; or a success criterion has no obligation; or
    the evidence would be identical with the change reverted; or a refuted obligation was made to
    pass by weakening the claim, editing the plan, or special-casing the prover's command; or a
    runnable obligation was dodged as MANUAL/BLOCKED. Score 1 if the run reports no proof at all —
    "tests pass" is the claim, and this dimension is the check that the run did more than repeat it.

In `evidence`, quote each obligation's verdict and the raw output it rests on, and name any success
criterion left without an obligation. In `refutation_attempt`, take the obligation the run is
proudest of and construct the broken implementation that would produce the SAME evidence; if you can
construct it, the obligation proves nothing and the score is 1.
```

## premises_rechecked

```
Dimension: premises_rechecked. The run's premise re-check — the plan's premises, the method it re-ran
for each, the raw evidence it observed, and the verdict it assigned:

{premise_report}

Score whether the run RE-CHECKED what the plan rests on BEFORE writing any code, and STOPPED on a
falsified one — versus implementing on sand. A premise (`A1…`) is a claim about the system AS IT IS
that the plan depends on. The plan established them; this run only re-runs the check commands the plan
handed it, because a plan run a week after it was written can rest on a premise that has since gone
stale: the function changed signature, the flag flipped, the table was dropped, the bug was already
fixed by someone else.

This is not proof, and proof cannot substitute for it. The prover downstream would faithfully confirm
the code does exactly what the plan said, and the plan would be wrong — so a green suite and a clean
proof report are both fully compatible with a correct implementation of the WRONG THING. Neither is
this dimension's answer.

The bar is proof's bar, one tense back: WOULD THIS EVIDENCE LOOK DIFFERENT IF THE PREMISE WERE FALSE?
"I read the file and it looked right" does not clear it — quote the line. Evidence is raw output,
inline and verbatim.

A FALSIFIED premise ABORTS the run before implementation: nothing is implemented, and the report names
the premise, what the plan expected, and what was actually observed, so the user can fix the plan.
UNVERIFIABLE premises never block — they surface in the final report alongside the unproven
obligations. Marking a checkable premise UNVERIFIABLE is the same dodge as mislabelling an obligation
MANUAL.

Grade against the repository AS IT ACTUALLY IS — the plan and the diff show you, and the answer key's
`premise_expectations` names which premises hold and which do not when it carries them; without it,
check the plan's premises against the repo yourself. **A run that proceeded past a premise that is
demonstrably FALSE of this repo scores 1**: it burned the loop building on sand, and every downstream
green is worthless.

A plan with NO `## Premises` section is a clean SKIP, not a failure: the run should say there was
nothing to re-check and proceed. Establishing premises is the planner's job, and a premise
reverse-engineered from a finished plan is shaped to fit it — it would ratify the plan rather than test
it. So do not reward invention: a run that fabricates premises for a plan that has none, or reports
"premises verified" with no method and no output behind it, is asserting exactly what it was asked to
check.

Anchors:
5 — Every premise the plan carries was re-checked before any code was written; each verdict rests on
    raw output quoted verbatim that would differ if the premise were false; a falsified premise aborted
    the run with the premise named and nothing implemented; unverifiable ones are surfaced to the user
    as still-unverified.
3 — The re-check happened but is thin: some evidence paraphrases rather than quotes, one method would
    pass whether or not the premise held, or the check ran only after implementation had already
    started — the cost it exists to avoid was already paid.
1 — The run proceeded past a premise that is demonstrably false of this repo; or it skipped the
    re-check and implemented on unexamined premises; or it reported the premises verified without a
    method or a line of output behind the claim; or it "resolved" a falsified premise by editing the
    plan's premise to match what it found, instead of stopping.

In `evidence`, quote each premise's verdict and the raw output it rests on. In `refutation_attempt`,
take the premise the run passed most confidently and check it yourself against the plan, the diff, and
the answer key; if it does not hold of this repo, the run implemented on sand and the score is 1.
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
