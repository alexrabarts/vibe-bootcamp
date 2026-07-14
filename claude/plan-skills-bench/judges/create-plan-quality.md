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
