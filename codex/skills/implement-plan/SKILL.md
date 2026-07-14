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

### Phase 2: Implement Phase by Phase

For each phase in the plan:

1. **Announce** what you're about to implement
2. **Implement** the changes described in the plan
   - Create new files as specified
   - Modify existing files as described
   - Follow the project's existing code style and patterns
   - **Update every coupled site** listed in the plan's "Ripple Effects / Coupled Sites" section in lockstep with its source — cross-repo contracts, docs, and same-repo duplication all change together. Call out any coupled site that falls outside this plan's scope (another repo or work item) so it isn't silently dropped.
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
3. Re-run tests
4. Repeat up to 5 times

### Phase 4: Final Review

After all phases are complete:

1. Run the full test suite (in every repo the plan touched)
2. Review all changes holistically (do the pieces fit together?) — for multi-repo plans, explicitly check the cross-repo seams: API/DTO contracts, shared types, config keys, and versioning must line up between the repos
3. Check for:
   - Unused imports or dead code
   - Missing error handling
   - Security vulnerabilities
   - Performance concerns
   - Documentation gaps
   - **Coupled-site drift** — flag any change whose coupled sites weren't updated in lockstep. Cross-repo drift is the sneakiest: the stale site is in a DIFFERENT repo, so THIS repo's tests pass green while the sibling silently breaks — so check cross-repo contract consumers explicitly even when local tests pass. Contract-breaking drift (API/DTO/schema/mirrored constant) is CRITICAL; doc or comment drift is a WARNING.
4. Make any final adjustments

### Phase 5: Report

Provide a summary:

- What was implemented (files created/modified)
- Test results
- Any issues encountered and how they were resolved
- Any remaining concerns or follow-up items
- Suggested next steps

**Do NOT commit or push changes.** Leave that to the user.

## Quality Standards

- All tests must pass before reporting success
- No unused imports or dead code
- No coupled site left stale — docs and cross-repo contracts consistent with the change
- Error handling for all external operations
- Comments explaining non-obvious logic
- Consistent code style with the rest of the project
