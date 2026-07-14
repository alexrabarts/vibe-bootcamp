# Implement Plan Prompt

Paste the following into ChatGPT when you're ready to implement a plan. Reference the plan you created earlier.

---

Please implement the plan we created for **[feature name]**. Work through it phase by phase:

If the plan spans **multiple repositories** (e.g. a backend repo plus its frontend consumer), work each repo independently: implement and run each repo's own tests separately, and at the end do a cross-repo review to confirm the seams line up (API/DTO contracts, shared types, config keys, versioning) — a mismatch between repos is a critical issue. Report results per repo; each repo is committed separately.

For each phase:
1. Tell me what you're about to implement
2. Write the code (create new files, modify existing ones as the plan specifies), and update EVERY coupled site the phase's Ripple Effects list names — mirrored constants/enums, shared contracts/DTOs/schemas, generated clients, docs, config-in-multiple-places — not just the primary change. Call out any coupled site that falls outside the current scope.
3. Write the tests specified in the plan
4. Run the tests and fix any failures
5. Self-review your work:
   - Does it match what the plan specified?
   - Any obvious bugs?
   - Is error handling adequate?
   - Any security concerns?
   - Any dead code or unused imports?
   - Any MISSED coupled site? A missed contract-breaking site is critical; a missed doc is minor. Cross-repo drift is the sneakiest — a stale site in another repo won't be caught by this repo's tests.
6. Move to the next phase

After all phases are complete:
1. Run the full test suite
2. Do a holistic review - do all the pieces fit together? Flag any change whose coupled sites weren't updated in lockstep, and confirm docs and cross-repo contracts are consistent with the code.
3. List any remaining concerns
4. Summarize what was implemented, what tests pass, and suggested next steps

Do NOT commit or push. I'll review the changes first.

If you hit a problem that requires changing the plan, explain the issue and your proposed adjustment before continuing.
