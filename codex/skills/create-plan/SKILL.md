---
name: create-plan
description: Create a comprehensive implementation plan before coding. Use for non-trivial features, bug fixes, refactors, investigations, or when the user asks to plan, explore approaches, compare options, or save a plan file.
---

# Create Plan

Create a comprehensive implementation plan through systematic investigation and multi-approach analysis before writing any code.

**The Prove-It Mandate**: A plan whose success criteria cannot be checked is a wish list. Every criterion gets a **proof obligation** — the concrete method that will produce evidence it was met, and what that evidence must show. Decide this now, while designing: an obligation written after the fact gets shaped to fit whatever the implementation happened to do. The test for a good obligation is simple — **would its evidence look different if the change were broken or absent?** "Run the tests" fails that test for a behavioral claim. The `implement-plan` skill discharges these obligations against the running system and blocks on the ones it refutes, so this is not paperwork: it is the bar the work will actually be held to.

**The Premise Mandate**: Proof obligations guard the plan's *output*. Nothing yet guards its *input* — the beliefs the plan itself rests on. A plan that ends with an `## Assumptions` list and "if any assumption is invalid, revisit this plan" is doing the planning equivalent of "tests pass": naming its load-bearing beliefs and leaving a human to notice one is wrong. Nobody does. So those beliefs become **premises** and get checked in Phase 4.25, before the plan is written. **The tense is the whole distinction**: a premise is a claim about the world **as it IS** (the call site exists, the column is nullable, this path is reached) — checkable now, by looking; a proof obligation is a claim about what will be true **AFTER** the change. Premises are `A1…`, obligations are `P1…`, and the two never share a namespace.

## When to Use

Use this skill when starting a new feature, fixing a non-trivial bug, or refactoring code. It front-loads thoroughness to prevent wasted implementation cycles.

## Process

### Phase 1: Understand the Task

1. Classify the task type: new feature, bug fix, refactoring, or investigation
2. Identify the scope: single function, module, or system-wide
3. Determine which technology domains are involved (backend, frontend, database, infrastructure)
4. **Check what other agent sessions are already working on.** Several sessions typically run at once across repos and worktrees, and none can see each other — so planning work another is already implementing is only discovered at merge time, when one implementation is thrown away. (A card was once built twice in parallel; the collision surfaced only when the second PR was refused as CONFLICTING, because the card sat unassigned in Backlog the whole time and the board could not show it.) Check `git worktree list` in each candidate repo — a worktree named for a ticket or feature is a claim on that work — plus `gh pr list` for open PRs, and uncommitted changes in any repo this plan would touch. **A collision does not make the plan wrong, it makes it taken**: say so and stop, rather than producing a plan whose only outcome is duplicated work. Partial overlap (another session in the same files on a different concern) is more common and needs sequencing, not silence. Never plan work in a repo another session is actively mutating — concurrent writers to one working tree corrupt each other; a separate worktree is fine, the same tree is not.

### Phase 2: Explore the Codebase

Before proposing any solution:

1. Read relevant source files thoroughly
2. Trace execution paths from entry points inward (interface layer -> business logic -> data layer -> infrastructure)
3. Document current behavior and architecture
4. Note code smells, warnings, or concerns
5. Identify dependencies and integration points
6. List existing tests and coverage gaps
7. Check recent git history for relevant changes
8. Discover **coupled sites** — for every value, type, contract, or behavior the change will touch, grep THIS repo AND sibling repos for every other occurrence, and locate docs describing the behavior. Coupled sites drift silently out of sync unless changed in lockstep. Look for three kinds:
   - **Cross-repo**: a shared contract (API shape, DTO, protobuf, OpenAPI/JSON schema), a client SDK or generated client, a mirrored constant/enum, a consumer repo that hard-codes the shape, a version pin
   - **Documentation**: README, API docs, CLAUDE.md, `.agent/` docs, CHANGELOG, config/env-var reference, code comments and in-code examples describing the changed behavior
   - **Same-repo duplication**: a constant/enum/type/string in more than one place, schema + validator + migration, a value in config AND code AND tests, a feature flag registered in several files, generated code + its source, a type + its (de)serializer

   Record each coupled site with repo + file:line + type.
9. Record **observability** — how the affected behavior can be watched from outside: how the app runs locally (command, port, seed/fixture data), endpoints with real example curls, CLI entry points and flags, the queries that would show the data changed, where logs go and what they print, health/metrics endpoints, and existing scripts or harnesses that already drive this path. Note anything that genuinely cannot be observed without a human, real credentials, hardware, or production. The proof obligations are built from this; without it, plans name commands that do not exist.

**Cite the line, not just its address.** A `file:line` is an address; nobody follows it, and a fact whose cited line does not say what the fact claims is indistinguishable from one that does. Record each fact with the ACTUAL content of the line you read, verbatim, alongside its address — the code, not a description of the code. Phase 4.25 verifies the load-bearing ones and starts from what you quote here.

**Do NOT propose solutions during exploration. Gather facts first.**

### Phase 3: Generate Multiple Approaches

Generate **at least 3 distinct approaches** (or root cause hypotheses for bugs).

For each approach, document:

- **Overview**: 2-3 sentence description of the high-level design
- **Key decisions**: Architectural choices and rationale
- **Components to build or modify**: Specific files and functions
- **Pros and cons**: Honest assessment of trade-offs
- **Risks**: What could go wrong and how to mitigate
- **Estimated effort**: Small / Medium / Large
- **Testing strategy**: How to verify correctness

### Phase 4: Compare and Recommend

Create a comparison of all approaches across these criteria:
- Complexity
- Maintainability
- Performance
- Testability
- Time to deliver
- Future flexibility
- Risk level

Recommend one approach with clear reasoning. Note conditions under which an alternative would be better.

### Phase 4.25: Verify the Premises

The recommended approach rests on claims about the system as it is. Check them now — before the user is asked anything and before any design work, so that no load-bearing question is premised on a falsehood and no phase is designed on sand. **Proof structurally cannot catch a false premise**: the prover would faithfully confirm the change does exactly what the plan said, and the plan was wrong. Green run, wrong outcome. That is why premises are upstream and are not simply another obligation class.

**The load-bearing test: if this were false, would the plan change?** If no, it is context, not a premise. Do NOT verify every fact Phase 2 turned up — that is a swamp, and the same discipline that caps Phase 4.5 at four questions applies here. Two kinds earn verification:

1. **Load-bearing** — the recommended approach collapses without it.
2. **Discriminating** — its truth value would REORDER the Phase 4 ranking. **This is the one that pays.** Phase 4 ranks by plausibility; verifying the premises that discriminate upgrades that to ranking by evidence, and can demote the recommendation and promote the runner-up. **Verify the premises that would change the answer**, not the ones easiest to confirm.

**State the premise the plan DEPENDS on — not the evidence you happen to have.** This is the failure that survives every other rule here, because the premise it produces is true, verifies cleanly, and holds nothing up. Test in BOTH directions: *if it were false, would the plan change?* AND *if it is TRUE, does the plan work?* One that passes the first and fails the second is necessary-but-insufficient — the belief the plan actually rests on was never written down. Real case: *"`ReconcileTable` is the reusable mitigation — OfficeRnD proves it"* is true (one caller, and a code comment calls it "the envelope-bloat mitigation"), but the plan depended on *"`ReconcileTable` is connector-agnostic"* — false, it hardcoded one connector's cursor column, which is exactly WHY it had one caller. **The tell is a premise that argues FOR the approach.** When a premise reads like a justification you have written the conclusion; ask instead *what would have to be true for this to be a bad idea?* and make THAT the premise.

**Descriptions are not evidence — exercise the mechanism.** The method must exercise the mechanism the premise claims, not read a description of it. These are all descriptions — someone's claim about the code, which is precisely what you are checking: a **code comment** ("// the envelope-bloat mitigation" is the author's intent, not the behavior — read the function); a **runbook or design doc** (one prescribed `GRANT SELECT ON <table>` while every working database used `db_datareader`, wrong for months because everyone read the doc instead of the database); an **analogy to a sibling** (the sibling's ordering key was deterministic; the analogy holds right up until the one property you needed); a **line number without its guard** ("scanned unconditionally at `snapshot_router.go:98`" — line 98 does call it, and line 89 returns first); a **prior conclusion**, including this skill's own. **Scope is part of the claim.** Negative/universal premises ("nothing consumes X", "this is the only writer") must search for the **behavior** — URL path, field name, call shape — across EVERY repo, never for a name someone chose: a grep for a chosen name across three of five repos returned VERIFIED for a claim the other two falsified, and that search looks identical whether or not the premise is true. A measurement is a claim about what was measured — "duplication is NOT pathological" was measured on one tenant at 4.0 versions/id and asserted fleet-wide, while the tenant in question ran 15–215.

For each premise record: **id** (A1, A2, ...), **claim**, **why load-bearing** (what in the plan changes if it is false), **method** (the exact grep, query, `git log`, file read, or curl that checks it), **expected** (decided BEFORE running it), **evidence** (the RAW output, inline and verbatim, trimmed to the decisive part), **verdict**.

Verdicts are **VERIFIED** (the evidence shows it holds), **FALSIFIED** (the evidence contradicts it), or **UNVERIFIABLE** (genuinely needs production, a human, real credentials, or a third party). The bar is proof's bar, one tense back: **would this evidence look different if the premise were FALSE?** A check that passes whether or not the premise holds is not a check, and "I read the file and it looked right" does not clear it — quote the line. Marking a checkable premise UNVERIFIABLE is the same dodge as mislabelling an obligation MANUAL: almost anything about the current code is checkable — a grep settles whether a call site exists, a query settles what the data looks like, `git log` settles when something changed.

**Independence, honestly.** Whoever asserted a fact should not be the one who confirms it — the asserter is the claim under suspicion, the same logic as prover ≠ implementer. If a subagent or delegation tool is available, route each check to an agent that did not surface the claim. Otherwise — the normal case in a single Codex thread — re-run the check against the codebase and rule on what it actually prints; never confirm a premise from your Phase 2 notes or your memory of reading the file. The raw output is what makes a self-check survivable: a grep prints the same thing whoever runs it, and the reader can re-run it. Note in the plan when premises were self-verified; it is weaker than an independent check and the reader is entitled to know.

**Then attack the premises that came back VERIFIED.** That is where the danger sits: a false plan built on true premises passes every check above. Before designing on them, turn on them once — **construct the world in which the premise is true and the plan is still wrong.** If you can construct it, that construction is the finding, and it sends you back to Phase 3 like any falsification. Do it as a separate, deliberate pass rather than in the flow of writing them, and note in the plan that the premises were self-audited; you are attacking your own reasoning, which is weaker than an adversary doing it, and the reader is entitled to weigh it accordingly.

**The gate: FALSIFIED blocks the plan.** Do not write a plan on a falsified premise and note the problem as a caveat — return to Phase 3, re-rank the approaches against the new evidence, re-select, and re-extract the premises for the new selection. This is the analogue of a REFUTED obligation blocking `implement-plan`, and it is the mechanism by which verification IMPROVES the plan rather than just annotating it. Loop until no load-bearing premise is falsified; if every approach rests on something false, that is a genuine finding — take it to the user rather than planning on the least-refuted option. UNVERIFIABLE premises do not block: they carry into `## Assumptions`, marked unverified.

Skip only when the plan rests on nothing checkable — a trivial single-file edit. Log clearly when skipped; skipping because the checks look tedious is how a plan ends up on sand.

### Phase 4.5: Resolve Key Decisions

Before fleshing out the detailed plan, surface 2–4 load-bearing decisions that — if answered differently — would invalidate the plan. Ask the user one focused question at a time and propose your recommended answer (with rationale) plus 2–3 alternatives. Wait for the user's answer before posing the next.

Source questions from:
- Open questions from Phase 2 exploration that couldn't be resolved by reading code
- Forks where two approaches require fundamentally different fixes
- Terminology mismatches between user language and codebase vocabulary
- Scope boundaries (in vs. out of scope)
- Trade-off forks where the right answer depends on user priorities (sync vs. async, additive vs. breaking migration, etc.)

**Hard cap: 4 questions.** Pick the ones with the highest blast radius.

Skip this phase if the task is trivial, all approaches share the same load-bearing decisions, or the user explicitly said "just plan it." Log clearly when skipped.

Record each resolved decision in a "Resolved Decisions" block to carry into Phase 5 as named constraints. Include this block in the final saved plan file so future readers see what was settled and why.

### Phase 5: Detail the Implementation Plan

For the recommended approach, create a phased plan:

For each phase:
- **Goal**: What this phase accomplishes
- **Files to modify**: Path and description of changes
- **Files to create**: Path and purpose
- **Database changes**: Migrations, schema changes (if any)
- **Tests to write**: Specific test cases
- **Dependencies**: What must be done first
- **Verification**: The runnable command that shows this phase actually works, and what its output must show — not "check that it works". If the phase delivers a success criterion, name that criterion's proof obligation id here.

Include:
- **Testing strategy**: Unit tests, integration tests, manual testing steps
- **Newly Load-Bearing**: What this phase makes newly REQUIRED — the opposite question to Ripple Effects, and the one that gets skipped. That section asks what must change WITH the phase; this asks what becomes REQUIRED BY it: something already present, already correct and invisible until the change starts depending on it. A value nothing read starts being read; a path dormant *because* of the state you change activates; a filter stops excluding; a predicate that could never match now can. State what becomes required (config row, seeded record, permission, quota, flag, capacity), WHERE it must exist and whether this plan can put it there, WHEN the dependency binds — usually NOT at merge, but the next rebuild / migration apply / flag flip — and whether its absence fails loud (a red gate) or silent (serving wrong values). **If the required thing is created outside this plan's control, it is a blocking step in the rollout sequence with an owner, not a closing note.** Write "None — nothing becomes newly required" when that is true; for a pure refactor it usually is.
- **Ripple Effects / Coupled Sites**: Enumerate every coupled site found in Phase 2 (repo + type + why it couples), so each is updated in lockstep with its source. Write "None — self-contained" if there are none. If a coupled site lives in a repo not already in the plan's repo set, flag it explicitly so that repo is added to the plan.
- **Risks and mitigations**: For each identified risk
- **Success criteria**: Clear, testable conditions for completion — including that no coupled site is left stale and that docs and cross-repo contracts stay consistent. Each functional criterion cross-references its proof obligation ("— proven by **P1**").
- **Proof Obligations**: One per success criterion (see below)
- **Premises**: What the plan rests on, as verified in Phase 4.25 — id, claim, why load-bearing, method, evidence, verdict. Design on these and cite them (`rests on **A2**`) wherever a phase or a risk assessment depends on one, so a reader can see exactly which part of the plan collapses if a premise goes stale. If the design needs a claim about the current system that no verified premise covers, go back and verify it rather than quietly assuming it.
- **Assumptions**: Only what genuinely cannot be verified now — predictions, future states, third parties — each marked unverified with the risk if it is wrong. Anything checkable about the current system is a Premise, not an assumption; this section is deliberately short, and keeping it that way is what stops a premise being smuggled in here to dodge the check.

### Phase 6: Write the Proof Obligations

Every success criterion gets exactly one obligation. This is the evidence that will be demanded before the work is called done, and `implement-plan` discharges it against the running system.

For each, give:

- **id**: P1, P2, ... (referenced from the criterion)
- **claim**: the criterion, in one sentence
- **class**: MECHANICAL or MANUAL
- **method**: the EXACT command, with real paths, payloads, and any setup (start the server how? seed what?). Draw on the Phase 2 observability findings; do not invent a command that does not exist.
- **expected**: what the output must show — specific enough that someone could call pass or fail without knowing your intent (e.g. "body includes `\"status\":\"active\"`; before this change the field is absent")

**MECHANICAL vs MANUAL.** MECHANICAL means a command runnable unattended — HTTP calls against a locally started server, CLI invocations, database queries, log reads, a binary's output, a headless screenshot of a dev server. This is the default and it covers more than you'd assume. MANUAL means it genuinely needs human judgement, real credentials, hardware, or production. Only MECHANICAL obligations block the implementation run, so every MANUAL is a criterion nobody will check — keep them few and honest, and say why no command can substitute.

Before saving, review the section as an adversary would:

- A success criterion with no obligation — fix it
- A method that would pass regardless of the change (a green suite standing in for a behavioral claim, a status code with an unchecked body) — it proves nothing; replace it
- An obligation labelled MANUAL that is plainly runnable (an endpoint, a CLI flag, a query, a servable page) — reclassify it
- A method too vague to run as written, or an expectation loose enough that a broken implementation satisfies it — sharpen it

Prove each claim at the outermost layer a user feels it: if the criterion is about a rendered page, prove the page; if it is about data, show the rows. A criterion you cannot write a discriminating obligation for is too vague to be in the plan — sharpen it or drop it.

### Output

Save the plan to `.codex/plans/` with a descriptive filename (e.g., `feature-user-auth-20260223.md`).

The plan should be self-contained - someone reading just the plan file should understand the full context, approach, alternatives considered, and implementation details.

Include the `## Proof Obligations` section in the saved file. Omit it and `implement-plan` derives obligations from the success criteria itself — worse, because it has to guess the method from the outside.

Include the `## Premises` section too, evidence and all. `implement-plan` re-runs each method before writing any code, because a plan run a week later can rest on a premise that has since gone stale — and a falsified one stops the run rather than burning five iterations implementing on sand. Omit it and there is nothing to re-check: `implement-plan` will not invent premises after the fact, since ones reverse-engineered from a finished plan ratify it rather than test it. No premise in the file should be FALSIFIED — that one sent the plan back to Phase 3 and never reached the file.
