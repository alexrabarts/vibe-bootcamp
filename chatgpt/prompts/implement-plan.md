# Implement Plan Prompt

Paste the following into ChatGPT when you're ready to implement a plan. Reference the plan you created earlier.

---

Please implement the plan we created for **[feature name]**. Work through it phase by phase:

If the plan spans **multiple repositories** (e.g. a backend repo plus its frontend consumer), work each repo independently: implement and run each repo's own tests separately, and at the end do a cross-repo review to confirm the seams line up (API/DTO contracts, shared types, config keys, versioning) — a mismatch between repos is a critical issue. Report results per repo; each repo is committed separately.

**Prove it.** "Implemented, tests pass" is a claim, not evidence — a change can turn the suite green while doing nothing the plan asked for. So don't tell me it works: exercise the change yourself and show me the raw output. Curl the endpoint, run the CLI, query the database, read the logs, screenshot the page — then quote what came back verbatim, inline, trimmed to the decisive part. "The query returns the right rows" is a claim; the rows are evidence. The standard for every piece of evidence: **would this look different if the change were broken or absent?** If not, it proves nothing — a green suite does not prove a UI renders, a 200 does not prove the body is right, a log line saying "starting" does not prove the work finished. Prove the claim at the outermost layer a user feels it. If the plan has a Proof Obligations section, run those methods as written; if it doesn't, derive one obligation per success criterion.

**Check what it rests on first.** Proof is about what will be true after the change; the plan also rests on claims about the code as it is NOW, and proof structurally cannot catch a false one — you would faithfully confirm the change does exactly what the plan said, and the plan was wrong. So before you write any code: if the plan has a Premises section, re-run each check against the current code and quote the raw output. A plan written last week can rest on a function that changed signature, a flag that flipped, or a bug someone already fixed, and re-running the check the plan hands you costs a grep. If a premise comes back FALSE, stop — don't burn the whole implementation building on sand — and tell me the premise, what the plan expected, and what you actually observed, so I can fix the plan. Anything the plan marks unverifiable (needs production, real credentials, a third party) doesn't block; list it at the end under "NOT PROVEN — REQUIRES YOU". If the plan has no Premises section, skip this and say so — don't invent premises now, because ones reverse-engineered from a finished plan just ratify it instead of testing it.

For each phase:
1. Tell me what you're about to implement
2. Write the code (create new files, modify existing ones as the plan specifies), and update EVERY coupled site the phase's Ripple Effects list names — mirrored constants/enums, shared contracts/DTOs/schemas, generated clients, docs, config-in-multiple-places — not just the primary change. Call out any coupled site that falls outside the current scope.
3. Write the tests specified in the plan
4. Run the tests and fix any failures
5. Prove the phase: for each success criterion this phase delivers, run its proof obligation against the running system and show me the command and its raw output. If the evidence refutes the claim, the phase is not done — change the BEHAVIOR and re-prove; never soften the claim or special-case the command to make it pass.
6. Self-review your work:
   - Does it match what the plan specified?
   - Any obvious bugs?
   - Is error handling adequate?
   - Any security concerns?
   - Any dead code or unused imports?
   - Any MISSED coupled site? A missed contract-breaking site is critical; a missed doc is minor. Cross-repo drift is the sneakiest — a stale site in another repo won't be caught by this repo's tests.
7. Move to the next phase

After all phases are complete:
1. Run the full test suite
2. Re-prove every success criterion against the final integrated code — same claims, same methods, nothing dropped or reworded because it failed earlier. Report each as PROVEN (with its evidence) or REFUTED (which means not done — fix and re-prove).
3. Do a holistic review - do all the pieces fit together? Flag any change whose coupled sites weren't updated in lockstep, and confirm docs and cross-repo contracts are consistent with the code.
4. List any remaining concerns
5. Summarize what was implemented, what tests pass, and suggested next steps
6. List separately, under "NOT PROVEN — REQUIRES YOU", every criterion you could not prove — anything that genuinely needed my judgement, real credentials, hardware, or production — with what I have to do to settle it. Say it plainly rather than glossing it: an unproven criterion must never be reported as if it were checked.

Do NOT commit or push. I'll review the changes first.

If you hit a problem that requires changing the plan, explain the issue and your proposed adjustment before continuing. And if a work item turns out to rest on something untrue of the code, or is already done, or would break something — say so and stop. That is a successful outcome, not a failure: don't fill the gap with adjacent work, and never let a diff look like work that isn't there. If you implemented nothing, tell me you implemented nothing and why, rather than shipping a test that pins behavior which already existed.
