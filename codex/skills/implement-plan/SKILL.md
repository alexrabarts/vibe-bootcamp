# Implement Plan

Automatically implement a plan with iterative development and self-review loops.

## When to Use

Use this skill after creating a plan (either via the `create-plan` skill or manually). It takes a structured plan and implements it phase by phase with quality checks.

## Prerequisites

- A plan file exists (check `.codex/plans/` or ask the user to specify)
- If no plan file is found, ask the user what to implement or suggest running the `create-plan` skill first

## Process

### Phase 1: Read and Analyze the Plan

1. Read the plan file
2. Identify the implementation phases
3. Determine what files need to be created or modified
4. Check if any dependencies need to be installed

### Phase 2: Implement Phase by Phase

For each phase in the plan:

1. **Announce** what you're about to implement
2. **Implement** the changes described in the plan
   - Create new files as specified
   - Modify existing files as described
   - Follow the project's existing code style and patterns
3. **Write tests** as specified in the plan
4. **Run tests** after each phase to catch issues early
   - Look for: `justfile` with test recipe, `package.json` test script, `go test ./...`, `pytest`, `cargo test`
5. **Self-review** your implementation:
   - Does it match what the plan specified?
   - Are there any obvious bugs or issues?
   - Is error handling adequate?
   - Are there security concerns?
   - Is the code clean and well-documented?

### Phase 3: Fix Issues

If tests fail or you spot issues during self-review:

1. Diagnose the root cause
2. Fix the issue
3. Re-run tests
4. Repeat up to 5 times

### Phase 4: Final Review

After all phases are complete:

1. Run the full test suite
2. Review all changes holistically (do the pieces fit together?)
3. Check for:
   - Unused imports or dead code
   - Missing error handling
   - Security vulnerabilities
   - Performance concerns
   - Documentation gaps
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
- Error handling for all external operations
- Comments explaining non-obvious logic
- Consistent code style with the rest of the project
