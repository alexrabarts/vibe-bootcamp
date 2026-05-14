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

**Phase 3.5 - Resolve key decisions:** Before fleshing out the detailed plan, identify 2–4 load-bearing decisions where answering differently would invalidate the plan (e.g., terminology mismatches, scope boundaries, sync vs. async forks, additive vs. breaking changes). Ask me one focused question at a time. For each question, propose your recommended answer with rationale, plus 2–3 alternatives, and wait for my answer before asking the next. Skip this step if the recommended approach has no genuine forks. Record the resolved decisions in the final saved plan under a "Resolved Decisions" section.

**Phase 4 - Detail the plan:** For the recommended approach, create a phased implementation plan. For each phase:
- Goal
- Specific files to modify (with description of changes)
- Specific files to create (with purpose)
- Database changes (if any)
- Tests to write
- How to verify the phase is complete

Include an overall testing strategy, risk assessment, and clear success criteria.

Save the plan so we can reference it during implementation.
