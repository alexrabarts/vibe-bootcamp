---
name: implement-plan
description: Implement an existing plan phase by phase with verification and self-review. Use when the user asks to implement a saved plan, continue from a plan file, execute planned work, or run the plan implementation workflow.
---

# Implement Plan

Automatically implement a plan with iterative development and self-review loops.

## When to Use

Use this skill after creating a plan (either via the `create-plan` skill or manually). It takes a structured plan and implements it phase by phase with quality checks.

## Prerequisites

- A plan file exists (check `.codex/plans/` or ask the user to specify)
- If no plan file is found, ask the user what to implement or suggest running the `create-plan` skill first

## Prove It

An agent reporting "implemented, tests pass" has made a **claim**, not shown evidence. A change can turn the suite green while doing nothing the plan asked for, and a diff can read correctly while the running system does not work. So nothing here is complete on assertion: every success criterion in the plan is a **proof obligation**, discharged by exercising the change — curl the endpoint, run the CLI, query the database, screenshot the page, read the logs — and reporting the raw output observed.

- **The prover is never the implementer.** An implementer vouching for its own work is precisely the claim under suspicion. If a subagent or delegation tool is available, hand the proof to a fresh agent that did not write the code. Otherwise — the normal case in a single Codex thread — prove in a separate, deliberate pass: take only the plan's obligation text and the running system as input, ignoring your own summary and your memory of what you meant to build. Say in the report which of the two you did; a self-proof is weaker evidence and the user is entitled to know.
- **Evidence is the raw output, inline.** The returned rows, the response body, the log lines, the printed value — verbatim, trimmed to the decisive part. "The query returns the right rows" is a claim; the rows are evidence. Only evidence that genuinely cannot be inlined (a screenshot, oversized output) becomes an artifact — park it wherever the user wants it, never in a repo working tree.
- **The standard: would this evidence look different if the change were broken or absent?** If not, it proves nothing. A green suite does not prove a UI renders; a 200 does not prove the body is right; a log line saying "starting" does not prove the work finished. Prove the claim at the outermost layer a user feels it.
- **Only refuted proof blocks.** Each obligation is MECHANICAL (a command runnable unattended — the default, and it covers more than you'd assume: HTTP calls against a locally started server, CLI invocations, database queries, log reads, a built binary's output, a headless screenshot of a dev server) or MANUAL (genuinely needs human judgement, real credentials, hardware, or an unreachable environment like production). Verdicts: PROVEN / REFUTED / BLOCKED / MANUAL_PENDING. REFUTED is CRITICAL and sends you back to Phase 3 exactly like a failing test. BLOCKED and MANUAL are warnings handed to the user — they never stall the run.
- **Mislabelling is the gaming vector.** The cheap escape is to call a runnable obligation MANUAL or BLOCKED and skip the work, so the Phase 4 audit checks every such label against the diff — a bogus one is CRITICAL.
- **The bar cannot move.** Obligations freeze when first read and are re-proven verbatim after every fix. Fix the BEHAVIOR, never the claim: do not reword an obligation, rewrite the plan, or special-case the proof command to make it pass.

The `create-plan` skill writes the plan's `## Proof Obligations` section, so the standard is set before any code is written. If a plan has none (hand-written, or older), derive one obligation per success criterion — a plan without an explicit proof block still has to be proven.

## Premises

Proof is a claim about what will be true AFTER the change. A **premise** is a claim about the world AS IT IS that the plan depends on — checkable now, by looking. The tense is the whole distinction, and it is why premises are not simply another obligation class: **proof cannot catch a false premise.** The prover would faithfully confirm the change does exactly what the plan said, and the plan was wrong. Green run, wrong outcome.

Premises are **established at plan time** — that is the `create-plan` skill's job, and the plan file carries them in a `## Premises` section, each entry naming the exact method that checks it. Here they are only **re-checked**, cheaply, before any code is written. A plan run a week after it was written can rest on a premise that has since gone stale: the function it depends on changed signature, the flag it assumed flipped, the table it queries was dropped, the bug it fixes was already fixed by someone else. The plan hands over the check command for free — re-running it costs a grep.

- **The same bar as proof, one tense back: would this evidence look different if the premise were FALSE?** Evidence is the raw output, inline and verbatim, exactly as in proof. "I read the file and it looked right" does not clear it — quote the line. Re-run the method against the code as it is now; never confirm a premise from the evidence recorded in the plan, which is precisely what may have gone stale.
- **A FALSIFIED premise ABORTS the run before implementation.** Verdicts are VERIFIED / FALSIFIED / UNVERIFIABLE. Falsified means the plan is built on sand: nothing is implemented, and the report names the premise, what the plan expected, and what was actually observed, so the user can fix the plan. Burning five fix iterations on a false premise produces a correct implementation of the wrong thing.
- **UNVERIFIABLE premises pass through.** Some beliefs genuinely cannot be checked from here — they need production, a human, or a third party. They never block; they surface in the final report alongside the unproven obligations. Marking a *checkable* premise UNVERIFIABLE is the same dodge as mislabelling an obligation MANUAL, and gets the same scepticism.
- **No `## Premises` section → skip cleanly.** A hand-written or older plan simply has none. Do not invent premises and do not block: this is a re-check, not a first check, and a premise reverse-engineered from a finished plan is shaped to fit it — it would ratify the plan rather than test it.

Independence is less of a problem here than in proof: the claim and its method were fixed by the plan before you read it, so re-running them is a real check even in a single Codex thread — you are not the one who asserted them. Where it does apply is the temptation to rule on a premise you are about to build on; rule on what the command prints, and change no source while checking. Fixing a falsified premise is not your call either — the plan is what needs fixing, and that is the user's decision.

Ids are `A1…` — the old `## Assumptions` section grown teeth. Proof obligations stay `P1…`; the two never share a namespace.

## Multi-Repo Plans

A plan may span **several repositories** (e.g. a backend repo plus its frontend consumer, or the same change across many repos). When it does:

- Work each repo independently — implement, test, and review it on its own.
- Run **each repo's own test suite** (each repo may use a different test command).
- Never assume changes in one repo are visible in another — they are separate git histories.
- Do a **cross-repo review** at the end: verify the seams line up (API/DTO contracts, shared types, config keys, versioning). A mismatch between repos is a critical issue.
- Report results **per repo**, and remember each repo is committed separately by the user.

Single-repo plans are just the one-repo case — nothing extra to do.

## Process

### Phase 1: Read and Analyze the Plan

1. Read the plan file
2. Identify the implementation phases
3. Determine which **repositories** the plan touches, and which files in each need to be created or modified
4. Check if any dependencies need to be installed (in each repo)
5. Extract the plan's `## Proof Obligations` (or derive one per success criterion if absent), assigning stable ids (P1, P2, ...). **Freeze this list now** — it is the bar the work will be held to, and it must not soften as the fix loop pushes for green
6. **Re-check the plan's `## Premises`** before writing any code. Run each method as written against the current repositories — if it no longer runs verbatim (a path moved, a command was renamed), adapt it minimally to check the SAME claim and say what changed; if it cannot run because the thing it points at is gone, that is usually evidence the premise is FALSE, not a reason to call it unverifiable, so quote the error and rule on the claim. Record the raw output as evidence and assign VERIFIED / FALSIFIED / UNVERIFIABLE:

```
  ✓ A1 VERIFIED      The handler at api/foo.go:42 is the only writer to accounts.status
        rg -n 'acct\.Status\s*=' --type go
        evidence: api/foo.go:42:  acct.Status = req.Status
  ⚠ A3 UNVERIFIABLE  The vendor's /v2 endpoint returns 410 for archived records
        needs real credentials against the vendor's production API
```

   **Any FALSIFIED premise stops the run here**: do not review, do not implement, do not burn the fix loop building on sand — report FAILED with the premise named, what the plan expected, and what was actually observed (see Phase 5), and leave the plan for the user to fix. UNVERIFIABLE premises do not block; carry them to the final report. If the plan has no `## Premises` section, say so plainly ("skipped: the plan has no Premises section, nothing to re-check") and proceed — a vacuous pass is worse than silence

### Phase 2: Implement Phase by Phase

For each phase in the plan:

1. **Announce** what you're about to implement
2. **Implement** the changes described in the plan
   - Create new files as specified
   - Modify existing files as described
   - Follow the project's existing code style and patterns
   - **Update every coupled site** listed in the plan's "Ripple Effects / Coupled Sites" section in lockstep with its source — cross-repo contracts, docs, and same-repo duplication all change together. Call out any coupled site that falls outside this plan's scope (another repo or work item) so it isn't silently dropped.
   - **Refuse rather than fill the gap.** If a work item rests on something untrue of the repo, is already done, or would break something — report it and stop. That is a SUCCESSFUL outcome, exactly as REFUTED is for a prover: you found a real gap between the plan and reality, and a refuted item caught here is worth more than code. What you must not do is fill the gap with adjacent work. One agent asked to add an optimisation found it already in production and changed nothing — which was correct — then shipped a 119-line test pinning the existing behavior and reported the item done; the diffstat read "+39 lines" and the production diff was empty, so the whole finding stayed invisible for hours. The model is the other agent, which proved the plan's safety premise false, refused to build the destructive thing, shipped a read-only evidence probe instead, and said exactly that. Refuse loudly; never let a diffstat imply work that is not there. If you implement nothing, say "I implemented nothing, here is why" and report no files changed — do not add a test, a comment, or a doc to make the item look serviced. If you implement PART of it, say which part and why the rest is refused.
3. **Write tests** as specified in the plan
4. **Run tests** after each phase to catch issues early
   - Look for: `justfile` with test recipe, `package.json` test script, `go test ./...`, `pytest`, `cargo test`
5. **Self-review** your implementation:
   - Does it match what the plan specified?
   - Are there any obvious bugs or issues?
   - Is error handling adequate?
   - Are there security concerns?
   - Is the code clean and well-documented?
   - **Any missed coupled sites?** Explicitly hunt for occurrences the plan didn't list. A missed contract-breaking site (API/DTO/schema/mirrored constant) is CRITICAL; a missed doc or code comment is a minor/WARNING.

### Phase 3: Fix Issues

If tests fail or you spot issues during self-review:

1. Diagnose the root cause
2. Fix the issue
3. Re-run tests, and re-prove any refuted obligation with the same method, verbatim
4. Repeat up to 5 times

A REFUTED obligation is fixed by changing the behavior until the unchanged method yields the expected result. Never weaken the claim, rewrite the plan, or special-case the proof command.

**Only blockers get fixed: test failures, REFUTED obligations, and CRITICAL issues. Warnings do not block.** Chasing warnings to zero turns this loop into a treadmill — a real run went 8 → 4 → 5 → 1 → 3 warnings across five iterations, going UP twice, never converging, hitting the cap and reporting PARTIAL having done everything asked. Worse, it drags in unscoped work: a change specced as "one `/healthz` field plus four small debts" came back as 3,191 insertions across 32 files with an unrelated de-flaking campaign attached, because every pass found more warnings to fix. Report warnings for the user to judge and move on; fix one only where it sits in code this plan already touches and the fix is incidental. If something genuinely must block, it is CRITICAL — categorize it that way rather than relying on a warning to stop the run.

### Phase 3.5: Prove the Success Criteria

Tests prove the suite is green; this proves the plan's criteria are actually met. They are independent observations of the same code, so run this whether or not tests exist.

For each frozen obligation:

1. **Classify** it MECHANICAL or MANUAL. Lean MECHANICAL — dodging a runnable obligation by labelling it MANUAL is the failure mode this gate exists to catch.
2. **Discharge** each mechanical one: run its method exactly as written (start whatever it needs — dev server, test DB — and tear it down after), then record the RAW output inline as evidence, verbatim and trimmed to the decisive part.
3. **Assign a verdict**: PROVEN (evidence shows expected), REFUTED (evidence contradicts expected), BLOCKED (genuinely could not run — state precisely what stopped it), MANUAL_PENDING.

Change no source while proving — observe and report; fix in Phase 3. REFUTED is a *successful* outcome for a prover: finding a real gap between claim and reality is the job.

```
  P1 PROVEN   GET /api/foo returns the new `status` field
      curl -s localhost:8080/api/foo
      evidence: {"id":7,"status":"active"}
  P2 REFUTED  Dashboard shows the archived count
      evidence: panel renders "—"; archived_count absent from the response payload
  P3 BLOCKED  Migration applies cleanly on a prod-sized dataset
      no prod-sized fixture available locally
```

Any REFUTED obligation is CRITICAL: return to Phase 3. BLOCKED and MANUAL_PENDING are warnings carried to the report.

### Phase 4: Final Review

After all phases are complete:

1. Run the full test suite (in every repo the plan touched)
2. **Audit the proof** — read it as a reviewer would, against the diff rather than at face value:
   - A MANUAL or BLOCKED label on something the diff shows IS runnable (an HTTP endpoint, a CLI flag, a query, a pure function, a page the dev server can serve) — CRITICAL
   - Evidence that would look IDENTICAL if the change were reverted (a green suite standing in for a behavioral claim, a 200 with an unchecked body, a screenshot of an untouched page) — CRITICAL
   - A success criterion with NO obligation covering it — CRITICAL
   - Evidence that paraphrases or asserts success instead of quoting raw output — WARNING
   - A genuinely BLOCKED or MANUAL obligation with an honest reason — WARNING; say what the human must do
3. Review all changes holistically (do the pieces fit together?) — for multi-repo plans, explicitly check the cross-repo seams: API/DTO contracts, shared types, config keys, and versioning must line up between the repos
4. Check for:
   - **Empty work** — a diffstat is not a diff. For any item reported as implemented, strip comments and blank lines and see what PRODUCTION code is left. Comments-only, docs-only, or only a test pinning behavior that already existed, while the summary reads as though the item was built — CRITICAL. It is the most expensive failure available here, because it looks like work in every view except this one, and it buries a refutation the user needed. An HONEST empty diff ("I implemented nothing, the plan is wrong, here is the evidence") is NOT a finding — that is the correct outcome; say so and let it stand.
   - Unused imports or dead code
   - Missing error handling
   - Security vulnerabilities
   - Performance concerns
   - Documentation gaps
   - **Coupled-site drift** — flag any change whose coupled sites weren't updated in lockstep. Cross-repo drift is the sneakiest: the stale site is in a DIFFERENT repo, so THIS repo's tests pass green while the sibling silently breaks — so check cross-repo contract consumers explicitly even when local tests pass. Contract-breaking drift (API/DTO/schema/mirrored constant) is CRITICAL; doc or comment drift is a WARNING.
5. Make any final adjustments

### Phase 5: Report

Provide a summary:

- What was implemented (files created/modified)
- **Premises** — one line per re-checked premise with the evidence that settles it. Omit the section entirely if the plan had none. If a premise was FALSIFIED, the report is about that and nothing else: nothing was implemented, so name the premise, what the plan expected, and what you observed instead, and stop
- Test results
- **Proof** — one line per obligation: the claim, the method so the user can re-run it, and the evidence that settles it (the actual output, not "verified"). State whether a separate agent proved the work or you proved your own.
- Any issues encountered and how they were resolved
- **Warnings** — list every one Wigsy raised, with file:line and the recommended fix. Never collapse them to a count: warnings no longer block, so this list is the ONLY place they reach the user — omit it and you have not relaxed a gate, you have deleted the findings. Say plainly that they were left alone deliberately, and that anything which should have blocked was mis-categorized and wanted to be CRITICAL
- Any remaining concerns or follow-up items
- Suggested next steps

If any obligation is BLOCKED or MANUAL, or any premise UNVERIFIABLE, this section is mandatory and never buried:

```
NOT PROVEN — REQUIRES YOU:
  P3  Migration applies cleanly on a prod-sized dataset  (BLOCKED)
      Why: no prod-sized fixture available locally
      To discharge: [what the user should run or do]
  P4  Screen-reader announces the new control  (MANUAL)
      To discharge: [what the user should run or do]
  A3  The vendor's /v2 endpoint returns 410 for archived records  (UNVERIFIABLE premise)
      The plan rests on this and it is still a belief, not a fact
      To settle: [what the user should run or do]
```

These were NOT verified. The work can be complete on everything provable mechanically while these criteria remain claims until the user checks them — never imply they were checked.

**Do NOT commit or push changes.** Leave that to the user.

## Quality Standards

- All tests must pass before reporting success
- Every mechanical proof obligation PROVEN, with its raw evidence shown — no REFUTED obligation, and no unproven criterion reported as anything other than unproven
- Warnings reported for the user to judge, never chased — they do not block completion (see Phase 3)
- No unused imports or dead code
- No coupled site left stale — docs and cross-repo contracts consistent with the change
- Error handling for all external operations
- Comments explaining non-obvious logic
- Consistent code style with the rest of the project
