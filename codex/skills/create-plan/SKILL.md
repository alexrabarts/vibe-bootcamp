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
- **Risks and mitigations**: For each identified risk
- **Success criteria**: Clear, testable conditions for completion
- **Assumptions**: Things that need to be true for the plan to work

### Output

Save the plan to `.codex/plans/` with a descriptive filename (e.g., `feature-user-auth-20260223.md`).

The plan should be self-contained - someone reading just the plan file should understand the full context, approach, alternatives considered, and implementation details.
