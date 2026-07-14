---
name: create-plan
description: Create a comprehensive implementation plan before coding. Use for non-trivial features, bug fixes, refactors, investigations, or when the user asks to plan, explore approaches, compare options, or save a plan file.
---

# Create Plan

Create a comprehensive implementation plan through systematic investigation and multi-approach analysis before writing any code.

## When to Use

Use this skill when starting a new feature, fixing a non-trivial bug, or refactoring code. It front-loads thoroughness to prevent wasted implementation cycles.

## Process

### Phase 1: Understand the Task

1. Classify the task type: new feature, bug fix, refactoring, or investigation
2. Identify the scope: single function, module, or system-wide
3. Determine which technology domains are involved (backend, frontend, database, infrastructure)

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
- **Verification**: How to confirm this phase is complete

Include:
- **Testing strategy**: Unit tests, integration tests, manual testing steps
- **Ripple Effects / Coupled Sites**: Enumerate every coupled site found in Phase 2 (repo + type + why it couples), so each is updated in lockstep with its source. Write "None — self-contained" if there are none. If a coupled site lives in a repo not already in the plan's repo set, flag it explicitly so that repo is added to the plan.
- **Risks and mitigations**: For each identified risk
- **Success criteria**: Clear, testable conditions for completion — including that no coupled site is left stale and that docs and cross-repo contracts stay consistent
- **Assumptions**: Things that need to be true for the plan to work

### Output

Save the plan to `.codex/plans/` with a descriptive filename (e.g., `feature-user-auth-20260223.md`).

The plan should be self-contained - someone reading just the plan file should understand the full context, approach, alternatives considered, and implementation details.
