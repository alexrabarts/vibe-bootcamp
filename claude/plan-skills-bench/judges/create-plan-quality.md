# Judge prompts — `create-plan` L3 quality dimensions

One prompt per dimension. Render with `{plan}`, `{answer_key}`, `{questions_asked}` substituted.
Each judge returns one object matching `judges/schema.json`. Run 3 judges per dimension; take the
median score and majority `matches_answer_key`. Judges must be a different invocation (ideally a
different model) than the skill under test.

Shared preamble (prepend to every prompt):

```
You are an adversarial evaluator of an AI-generated implementation PLAN. You are NOT here to be
encouraging. Your job is to find where the plan is weakest. You have the GROUND-TRUTH answer key
for this scenario — grade against truth, not against how plausible or polished the plan sounds. A
fluent, well-formatted plan that reaches the wrong conclusion scores LOW. Return JSON matching the
provided schema. The `refutation_attempt` field is mandatory: state the strongest case against the
plan even when you score it high.

GROUND-TRUTH ANSWER KEY:
{answer_key}

THE PLAN UNDER REVIEW:
{plan}
```

---

## distinctness

```
Dimension: distinctness. Score whether the plan's hypotheses (debug) or approaches (feature/
refactor) are MECHANISTICALLY distinct — different root causes / different architectures — versus
the same idea reworded to hit the ">=3" requirement.

Anchors:
5 — Each option has a genuinely different mechanism or architecture; ruling one out does not rule
    out the others; they would lead to materially different fixes/implementations.
3 — Options are distinct but overlap heavily, or one is a thin variant of another.
1 — Options are rephrasings of a single idea; the "alternatives" are padding.

Quote the option headings/mechanisms in `evidence`. In `refutation_attempt`, argue that two of the
options collapse into one and assess whether that argument holds.
```

## evidence_grounding

```
Dimension: evidence_grounding. Score whether the plan's claims are anchored in the actual code —
file:line citations, an execution trace from outer layer inward — versus asserted from intuition.
This skill's stated mandate is anti-surface-level: it must trace systems inward and verify
assumptions by reading code.

Anchors:
5 — Specific file:line references throughout; a coherent outer->inner trace; claims about behavior
    are tied to quoted code, not guessed.
3 — Some references, but key claims are asserted without a code anchor; trace is partial.
1 — Hand-wavy; few or no references; reasons from symptom names rather than from the code.

In `evidence`, list the file:line references the plan actually provides. In `refutation_attempt`,
identify the most important claim that is NOT backed by a code reference.
```

## correct_primary

```
Dimension: correct_primary. Score whether the plan's PRIMARY hypothesis (debug) or RECOMMENDED
approach (feature) matches the ground-truth answer key. The answer key lists `true_primary` and a
set of `decoys` — obvious-but-wrong explanations the plan must NOT select as primary.

Set `matches_answer_key` true iff the selected primary corresponds to `true_primary` (same
mechanism and locus), false otherwise.

Anchors:
5 — Primary = true_primary, correctly localized (matches `true_primary_locus`), decoys explicitly
    considered and ranked below.
3 — True cause appears among the options but is NOT ranked primary, OR primary is correct but
    mislocalized.
1 — Primary is one of the decoys, or the true cause is absent entirely.

In `refutation_attempt`, make the strongest case that the plan anchored on a decoy.
```

## checkpoint_leverage

```
Dimension: checkpoint_leverage. The plan's Phase 2.5 asked the user these questions:
{questions_asked}

Score whether they are LOAD-BEARING — questions whose answer would materially reshape the plan
(a different answer flips the approach, scope, or fix) — versus trivial confirmations or questions
answerable by reading the code.

Anchors:
5 — Every question is a genuine fork; a different answer would change the downstream plan
    significantly; <=4 questions, no padding.
3 — Mixed: at least one real fork, but also a trivial or code-answerable question.
1 — Questions are cosmetic / could have been resolved by reading code / interrogate the user
    needlessly. (Also score low here if the scenario expected a SKIP but the skill asked anyway.)

If `checkpoint_expected` in the answer key is "skips" and the skill asked questions, score 1 and
note the over-asking in `refutation_attempt`.
```

## actionability

```
Dimension: actionability. Score whether a competent implementer could execute this plan WITHOUT
re-deriving the analysis — concrete files, phased steps with dependencies, testable success
criteria, verification steps.

Anchors:
5 — Phases are concrete and ordered with dependencies; each names specific files and changes;
    success criteria are testable; verification steps are runnable.
3 — Plan is followable but has gaps an implementer must fill (vague files, untestable criteria).
1 — Plan is a high-level wish list; an implementer would have to start the analysis over.

In `refutation_attempt`, name the phase or criterion an implementer would get stuck on.
```

## coupled_site_coverage

```
Dimension: coupled_site_coverage. Score whether the plan ENUMERATES the sites that must change in
lockstep with this change so nothing silently drifts out of sync — cross-repo contract consumers
(client SDKs, DTOs, OpenAPI/protobuf schemas, version pins), same-repo duplicated constants / enums
/ types, and the docs that describe the changed behavior. A change to a producer that leaves its
consumers, duplicated definitions, or docs stale is the failure this dimension catches.

Anchors:
5 — A thorough "Ripple Effects / Coupled Sites" enumeration: every consumer/duplicate/doc that must
    move with the change is listed and tagged by repo + type (contract-consumer / duplicated-constant
    / doc), so an implementer updates them in lockstep; cross-repo consumers are explicitly named.
3 — Some coupled sites named, but the enumeration is partial — one class is missed (e.g. lists
    same-repo duplicates but ignores cross-repo consumers, or omits the docs).
1 — The plan changes one site and ignores its duplicates/consumers/docs entirely; ripple effects are
    unaddressed, leaving coupled sites to drift.

In `evidence`, quote the plan's coupled-site / ripple-effect enumeration (repo + type tags if
present). In `refutation_attempt`, name the most load-bearing consumer, duplicated definition, or doc
the plan failed to enumerate — cross-repo consumers are the easiest to miss.
```

## proof_adequacy

```
Dimension: proof_adequacy. Score whether the plan's `## Proof Obligations` section actually
discharges the bar it exists to set: EVERY success criterion gets exactly one obligation (cross-
referenced by id); each obligation's `method` is a real, runnable command with the paths, payloads,
and setup it needs; each `expected` is a pass condition specific enough to call pass/fail without
knowing the author's intent; and — the standard the rest serves — the evidence that method would
produce WOULD LOOK DIFFERENT if the change were broken or absent. The plan SPECIFIES the proof; a
later run discharges it. An obligation that cannot discriminate a working change from a broken one
sets no bar at all, and nothing downstream can recover it.

Obligations are MECHANICAL (a command runnable unattended — an HTTP call against a locally started
server, a CLI invocation, a database query, a log read, a binary's output, a headless screenshot of
a dev server) or MANUAL (genuinely needs human judgement, real credentials, hardware, or an
unreachable environment like production). Only MECHANICAL obligations are ever enforced, so MANUAL
is the cheap escape: a criterion labelled MANUAL is a criterion nobody will check. Treat a MANUAL
label on anything the plan's own text shows is runnable as a dodge, not a judgement call.

If the answer key carries `proof_expectations`, grade the obligations against it. If it does not,
grade against the plan's own Success Criteria plus the answer key's ground truth — an obligation
that would pass even if `true_primary` were never fixed is not proof.

Anchors:
5 — One obligation per success criterion, cross-referenced by id; every method is a concrete command
    with real paths/payloads/setup; every expectation is a specific pass condition; each
    obligation's evidence would visibly change if the change were reverted; the claim is proven at
    the outermost layer a user feels it; any MANUAL label is genuinely unautomatable.
3 — Obligations cover the criteria but the bar sags: a method is vague enough that the implementer
    must invent the command, an expectation is loose enough that a broken implementation would also
    satisfy it, or one plainly runnable criterion is parked as MANUAL.
1 — A success criterion has no obligation; or "run the test suite" / "tests pass" stands in for a
    behavioral claim (the suite goes green either way once a test is written to match the bug); or
    methods name commands, endpoints, or paths that do not exist; or criteria are dodged wholesale
    by labelling them MANUAL. The section is proof-shaped and proves nothing. Score 1 if the plan
    has no Proof Obligations section at all.

In `evidence`, quote each obligation's id, class, method, and expected — and name any success
criterion with no obligation. In `refutation_attempt`, take the obligation the plan is proudest of
and construct the broken implementation that would produce the SAME evidence; say whether that
construction holds. If it does, the obligation proves nothing.
```

## premise_verification

```
Dimension: premise_verification. Score whether the plan VERIFIED what it RESTS ON, rather than
asserting it. A premise (`A1…`) is a claim about the system AS IT IS that the plan depends on —
checkable NOW, by looking. The tense is the whole distinction: proof obligations (`P1…`) cover what
will be true AFTER the change, and proof structurally CANNOT catch a false premise — the prover would
faithfully confirm the change does exactly what the plan said, and the plan was wrong. Green run,
wrong outcome. The `## Premises` section is the only guard against that, so audit it as hard as the
obligations.

The load-bearing test for what owes a premise: IF THIS WERE FALSE, WOULD THE PLAN CHANGE? If no, it is
context, not a premise — verifying every fact the investigation turned up is a swamp, and a padded
section is not a virtue. Two kinds earn verification: LOAD-BEARING premises (the selected hypothesis /
approach collapses without them) and DISCRIMINATING premises (their truth value would REORDER the
hypothesis ranking).

Discriminating premises are what this dimension is really measuring. The plan ranks its hypotheses by
"likelihood based on evidence", which is ranking by PLAUSIBILITY — every hypothesis ends "IF
CONFIRMED" and nothing has confirmed one. Verifying the premises that would reorder that ranking is
what upgrades it to ranking by EVIDENCE, and it is the only thing that can demote the primary and
promote the secondary. A plan that verified only the safe, confirmatory premises of the hypothesis it
already liked has ANNOTATED its ranking, not tested it.

Verdicts are VERIFIED / FALSIFIED / UNVERIFIABLE. A FALSIFIED load-bearing premise blocks
finalization — the plan goes back to re-rank and re-select — so a finished plan that shows a FALSIFIED
premise and proceeds anyway is a plan knowingly built on sand.

Use the answer key's ground truth. A plan whose premises are ALL VERIFIED but whose primary hypothesis
contradicts `true_primary` verified the WRONG THINGS: the checks were real, the evidence was raw, and
the ranking is still wrong — precisely the failure discriminating premises exist to prevent. Grade
against the key's `premise_expectations` if it carries them; if it does not, grade against the plan's
own load-bearing claims plus the key's ground truth.

Anchors:
5 — The premises that would REORDER the ranking are the ones verified, not merely the comfortable
    ones; each method is a real command (grep / query / git log / curl / file read) whose output would
    look DIFFERENT if the premise were false; evidence is raw output quoted verbatim; the design cites
    premises by id; UNVERIFIABLE is used only for what genuinely needs production, a human, or a third
    party, and those are carried into `## Assumptions` as unverified.
3 — Premises are real but the section is safe: only the selected hypothesis's confirmatory premises are
    verified while the one that discriminates between hypotheses is left unchecked, or one method is
    weak enough that it would pass either way, or an evidence block paraphrases instead of quoting.
1 — A load-bearing belief has NO premise covering it; or a method could not discriminate ("read the
    file and it looked right", no quoted line — it would pass whether or not the premise holds); or a
    plainly checkable claim about the current code is parked as UNVERIFIABLE (the same dodge as
    labelling a runnable obligation MANUAL, and the same verdict); or the evidence is a paraphrase
    rather than raw output; or — the big one — a DEBUGGING-mode plan designs a fix for a root cause it
    NEVER CONFIRMED, which is the failure the whole discipline exists to catch. Score 1 if the plan has
    no Premises section at all and its beliefs about the current system are simply asserted, or if
    checkable claims are smuggled into `## Assumptions` to dodge the check.

In `evidence`, quote each premise's id, method, evidence, and verdict — and name any load-bearing
belief with no premise covering it. In `refutation_attempt`, take the premise the plan most depends on
and construct the world in which it is FALSE but the plan's method still passes; if you can construct
it, the check discriminates nothing and the score is 1. If every premise is VERIFIED, ask instead what
the plan did NOT check that would have reordered its ranking — and whether the key's ground truth says
the ranking is wrong regardless.
```
