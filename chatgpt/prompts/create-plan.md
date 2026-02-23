# Create Plan Prompt

Paste the following into ChatGPT when you want to plan a feature or fix. Replace the bracketed sections with your specifics.

---

I want to plan the implementation of: **[describe what you want to build or fix]**

Please follow this process:

**Phase 1 - Explore:** Before proposing solutions, examine the codebase. Read the relevant files, trace execution paths, and document what exists today. List the files you investigated and what you found.

**Phase 2 - Generate approaches:** Come up with at least 3 distinct approaches to solve this. For each approach, describe:
- Overview (2-3 sentences)
- Key architectural decisions and rationale
- Files to create or modify
- Pros and cons
- Risks and mitigations
- Estimated effort (small/medium/large)

**Phase 3 - Compare:** Create a comparison table across: complexity, maintainability, performance, testability, time to deliver, risk level. Recommend one approach with clear reasoning.

**Phase 4 - Detail the plan:** For the recommended approach, create a phased implementation plan. For each phase:
- Goal
- Specific files to modify (with description of changes)
- Specific files to create (with purpose)
- Database changes (if any)
- Tests to write
- How to verify the phase is complete

Include an overall testing strategy, risk assessment, and clear success criteria.

Save the plan so we can reference it during implementation.
