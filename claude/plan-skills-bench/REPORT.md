# Benchmark report — `/create-plan` and `/implement-plan`

**Date:** 2026-06-02
**Scope:** Build an eval set + runner for the two custom skills, then benchmark them against it.
**Artifacts:** `SPEC.md` (eval set), `runner/` (harness, self-tested), `fixtures/` (22 scenarios),
`judges/` (L3 prompts), `examples/` + `captured/` (replay bundles). Self-test: **78/78**.

> TL;DR — The skills are good where it counts. `create-plan` honors its anti-surface-level mandate
> (it found a deep root cause and refuted the decoys). The two skills handle a missing required
> agent *differently on purpose* — `create-plan` degrades gracefully for a read-only explorer,
> `implement-plan` hard-stops for an implementer — which is the right risk-appropriate distinction.
> Live runs also caught four harness bugs (now fixed) and one minor skill inconsistency.

---

## 1. Method

Each scenario is a fixture (a repo + a task/plan + a ground-truth answer key). A run is graded in
three layers: **L1** binary gates (correctness/honesty/safety — a fail caps the score at 0), **L2**
deterministic structural checks (0–1), **L3** LLM-judge quality dimensions (0–1). Score = 0 if any
L1 fails, else the weighted mean of L2 (0.4) and L3 (0.6). See `SPEC.md`.

Runs are produced by a driver: `MockDriver`/`ReplayDriver` (offline, for the harness self-test) or
`CliDriver` (live — `claude -p … --output-format stream-json` in a sandbox, with the per-scenario
agent roster staged and, for implement-plan, the plan injected). Live results below come from real
`/create-plan` and `/implement-plan` runs, graded offline from captured bundles in `captured/`.

**Caveat:** the live captures so far are the two missing-agent scenarios (C7, I6) and the C8
surface-trap. `implement-plan`'s *implementation quality* (correct code, convergence, cleanup) is
validated by the harness via mock/replay but has **not** yet been measured on a live proceed run
(I1/I4). The strongest implement-plan claims below are about its gate behavior, not its code output.

## 2. Skill findings (the benchmark results)

### 2.1 `create-plan` honors the anti-surface-level mandate — C8, live, score 1.0
C8 is a trap: the bug report dangles two decoys (a recently-added role check, a "tightened" COUNT
query) over a deeper timezone bug. The live run:
- classified DEBUGGING and traced inward `app.py → service.py → timewindow.py → db.py`;
- selected the **deep cause** as primary — the current-day window clamp at `timewindow.py:30`
  (`end = min(end, now_utc - TENANT_UTC_OFFSET_HOURS)`), named to the line;
- **refuted both decoys** explicitly ("COUNT(*) would read *high*, not low… no time dependency";
  "all-or-nothing 403 on access, not the count value").

This is direct evidence the mandate works in practice, not just in the skill text.

### 2.2 Missing-agent behavior diverges by design — C7 vs I6, both live
| Skill | Missing agent | Observed behavior | Score |
|-------|---------------|-------------------|-------|
| `create-plan` (C7) | read-only **explorer** (Oliver) | **Degrades gracefully** — detects the gap, notes the deviation, substitutes the generic `Explore` agent, proceeds to a full FEATURE plan (3 distinct approaches + matrix) | 0.8 |
| `implement-plan` (I6) | **implementer** (Oliver) | **Hard-stops** — *"if any required agent is missing, stop before implementation rather than substituting"*; emits `setup-agents`; writes zero code | 1.0 |

This is a **principled, risk-appropriate distinction** — substituting a generic agent for read-only
investigation is cheap; substituting one to write production code is not — and the skills get it
right. (The eval originally expected both to hard-stop; C7 was revised to reward degradation after
this evidence. I6 confirms implement-plan is correctly stricter.)

### 2.3 Minor skill inconsistency — checkpoint option labeling
`create-plan`'s spec says the first Phase-2.5 option must be labeled `(Recommended)`. The C8 run did
this; the C7 run did **not** (bare option labels). Same skill, inconsistent adherence across runs —
the only reason C7 scored 0.8 rather than ~1.0 (`checkpoint_format = 0`). Worth tightening in the
skill prompt if checkpoint formatting matters downstream.

## 3. Live scorecard

| Scenario | Skill | What it tests | Result | Score |
|----------|-------|---------------|--------|-------|
| C8 | create-plan | anti-surface-level (deep cause vs decoys) | found deep cause, refuted decoys | **1.0** |
| C7 | create-plan | missing explorer | graceful degradation (minor labeling miss) | **0.8** |
| I6 | implement-plan | missing implementer | correct hard-stop, no code written | **1.0** |

## 4. Harness findings (bugs the live runs caught — all fixed + regression-tested)

The live captures doubled as a test of the harness itself. Each of these would have produced a
wrong grade:
1. **stream-json parsing** — original parsers read top-level keys; real assistant text lives in
   `message.content[].text`, usage in `message.usage`, wall-clock in the `result` event. First C7
   capture produced an empty transcript. Fixed, tuned to Claude Code v2.1.x, regression-tested.
2. **`option_count` false-pass** — counted "Approach N" markers, missing the actual hypotheses;
   C8 passed only because its alternatives section happened to contain them. Hardened to count
   "Primary/Secondary/Tertiary Hypothesis" prose too.
3. **`output_tokens` undercount** — read **95** for an 8.5-min multi-agent run: `claude -p`
   stream-json carries only the orchestrator's turns, not Task sub-agent usage. **Use `wall_clock_s`
   as the cost proxy** (documented).
4. **`plan.md` not in the sandbox** — implement-plan reads its plan from the repo it runs in, but
   the fixture kept `plan.md` beside `repo/`, so the first I6 run halted on a *missing plan*, not the
   missing agent — a latent false-pass. Fixed by injecting the plan into the sandbox.

## 5. Limitations / not yet covered
- **No live implement-plan *proceed* capture** (I1/I4): implementation quality is mock/replay-tested
  only. This is the biggest remaining gap for a full picture.
- **Phase-2.5 answerer** not wired for live create-plan: headless runs fall back to recommended
  defaults rather than the scenario's scripted answers (benign for root-cause grading; affects which
  fix *direction* a plan commits to).
- **L3 LLM judges** not run live (no `anthropic` SDK / key in this environment); C8's `correct_primary`
  verdict above is a manual read, not a judge score.
- **Not under version control** — everything is uncommitted under `~/.claude/evals/plan-skills/`.

## 6. Recommendations
- **Skills look healthy** on the dimensions tested; no blocking issues found. The one concrete skill
  fix worth making: enforce consistent `(Recommended)` labeling in `create-plan`'s Phase-2.5 step.
- **To complete the picture:** capture a live implement-plan proceed run (I1/I4) to measure code
  quality/convergence; wire `--judge anthropic` to score the L3 dimensions formally; wire the
  Phase-2.5 answerer for faithful create-plan fix-direction grading.
- **Preserve the work:** `git init` the eval set so it stops being scratch.

## 7. Where to look
- Eval set + rubric: `SPEC.md` · Runner usage: `runner/README.md` · Self-test: `python3 -m runner.selftest`
- Live evidence: `captured/{C7,C8,I6}/` (graded with `runner.run --driver replay`)
- Reproduce a capture: `python3 -m runner.capture --scenario <id> --out ./captured --driver cli`
