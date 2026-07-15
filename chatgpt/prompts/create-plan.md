# Create Plan Prompt

Paste the following into ChatGPT when you want to plan a feature or fix. Replace the bracketed sections with your specifics.

---

I want to plan the implementation of: **[describe what you want to build or fix]**

Please follow this process:

**Phase 1 - Explore:** Before proposing solutions, examine the codebase. Read the relevant files, trace execution paths, and document what exists today. List the files you investigated and what you found. Also search this repo (and any sibling repos in scope) for every OTHER occurrence of each value/type/contract the change touches — mirrored constants/enums, shared API shapes/DTOs/schemas, generated clients, config-in-multiple-places — and note any docs that describe the behavior (README, API docs, CHANGELOG, config/env-var reference, comments). List these "coupled sites." Also record how the affected behavior can be OBSERVED from outside: how the app runs locally (command, port, fixtures), endpoints with real example curls, CLI entry points and flags, the queries that would show the data changed, where the logs go and what they print, existing scripts or harnesses that already drive this path — plus anything that genuinely cannot be observed without a human, real credentials, hardware, or production. The proof obligations below are built from this; without it you will invent commands that do not exist.

**Phase 2 - Generate approaches:** Come up with at least 3 distinct approaches to solve this. For each approach, describe:
- Overview (2-3 sentences)
- Key architectural decisions and rationale
- Files to create or modify
- Pros and cons
- Risks and mitigations
- Estimated effort (small/medium/large)

**Phase 3 - Compare:** Create a comparison table across: complexity, maintainability, performance, testability, time to deliver, risk level. Recommend one approach with clear reasoning.

**Phase 3.25 - Verify what the plan rests on:** Before you ask me anything or flesh out the plan, list the claims about the system **as it is today** that your recommendation depends on — the call site exists, the column is nullable, that code path is reached. These are checkable now, by looking, and proof cannot save you from a false one: you would faithfully build exactly what the plan said and the plan would be wrong. Apply the load-bearing test — **if this were false, would the plan change?** If no, it is context, not a premise; don't verify every fact you turned up. Then test the other direction — **if it is TRUE, does the plan work?** A premise that passes the first and fails the second verifies cleanly and holds nothing up, because the claim you were actually leaning on never got written down; the tell is a premise that argues FOR the approach, so ask instead what would have to be true for this to be a bad idea, and make THAT the premise. Include any claim whose truth would REORDER your Phase 3 ranking: that ranking is by plausibility until something checks it, and those are the ones that pay. For each, give an id (A1, A2, …), what in the plan changes if it is false, the exact check (grep, query, `git log`, file read, curl) — then RUN it and quote the raw output verbatim. Go back to the code for this rather than confirming it from your Phase 1 notes; the claim under suspicion is your own. The bar: **would this evidence look different if the premise were FALSE?** "I read the file and it looked right" does not clear it — quote the line. Exercise the mechanism, never a description of it: a code comment, a runbook or design doc, an analogy to a sibling, or a line number without the guard above it is someone's claim about the code, which is the thing you are checking. Scope is part of the claim too — a negative or universal premise ("nothing consumes X", "this is the only writer") has to search for the behavior, the URL path or field name or call shape, across every repo in scope, never for a name someone chose. If a premise turns out false, do not plan around it: go back to Phase 2/3, re-rank the approaches on the new evidence, and re-select before continuing. Record the verified premises (with their evidence) in the saved plan under a "Premises" section. Only what genuinely cannot be checked now — predictions, future states, third parties — stays under "Assumptions", marked unverified; anything a grep could settle is a premise, not an assumption.

**Phase 3.5 - Resolve key decisions:** Before fleshing out the detailed plan, identify 2–4 load-bearing decisions where answering differently would invalidate the plan (e.g., terminology mismatches, scope boundaries, sync vs. async forks, additive vs. breaking changes). Ask me one focused question at a time. For each question, propose your recommended answer with rationale, plus 2–3 alternatives, and wait for my answer before asking the next. Skip this step if the recommended approach has no genuine forks. Record the resolved decisions in the final saved plan under a "Resolved Decisions" section.

**Phase 4 - Detail the plan:** For the recommended approach, create a phased implementation plan. For each phase:
- Goal
- Specific files to modify (with description of changes)
- Specific files to create (with purpose)
- Database changes (if any)
- Tests to write
- Ripple Effects / Coupled Sites: every site that must change in lockstep with this phase, each tagged with repo + type (cross-repo contract / docs / same-repo duplicate) + why. Write "None — self-contained" if there are none. If a coupled site lives in a repo not currently in scope, flag it so that repo gets added.
- How to verify the phase is complete

Include an overall testing strategy, risk assessment, and clear success criteria. Success criteria must include: no coupled site left stale — docs and cross-repo contracts stay consistent with the change.

**Phase 5 - Proof obligations:** A plan whose success criteria cannot be checked is a wish list, so give every criterion exactly one proof obligation — decided now, while designing, because an obligation written after the fact gets shaped to fit whatever the implementation happened to do. For each: an id (P1, P2, …), the claim in one sentence, the EXACT command to run with real paths, payloads, and any setup (drawn from Phase 1's observability findings, not invented), and what the output must show — specific enough that someone could call pass or fail without knowing your intent. Cross-reference each success criterion to its id ("— proven by **P1**"). The bar every obligation must clear: **would its evidence look different if the change were broken or absent?** "Run the tests" fails that bar for a behavioral claim. Default to obligations runnable unattended — that covers more than you'd assume (curls against a locally started server, CLI invocations, queries, log reads, headless screenshots); mark one as needing me only when it truly needs human judgement, real credentials, hardware, or production, because those are the criteria nobody will check. A criterion you cannot write a discriminating obligation for is too vague to be in the plan — sharpen it or drop it.

Save the plan so we can reference it during implementation.
