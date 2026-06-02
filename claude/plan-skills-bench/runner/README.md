# Runner

Executable harness for the eval set in `../SPEC.md`. The deterministic machinery (sandboxing,
git-state gates, anti-tamper, held-out acceptance, L1/L2 checks, scoring, aggregation, A/B) is real
and self-tested. The one environment-specific piece — driving the live skill — sits behind the
`SkillDriver` interface (`drivers.py`).

## Layout

| module | role |
|--------|------|
| `contracts.py` | `ScenarioKey` / `RunArtifacts` / `TrialRecord`; loads answer keys from fixtures (parses the fenced ```yaml block in each `answer-key.md`) |
| `sandbox.py`   | materialize a fixture repo into a temp git sandbox; `is_pristine` / `orphan_worktrees` / `temp_branches` / `tampered_seeded_tests` |
| `suites.py`    | run held-out acceptance suites (pytest in prod; dependency-free fallback otherwise) |
| `checks.py`    | `l1_create` / `l2_create` / `l1_implement` / `l2_implement` / `acceptance_pass` |
| `judges.py`    | L3 quality judges: parse `../judges/*.md`, render prompts, `JudgeClient` ABC + `MockJudgeClient` / `AnthropicJudgeClient`, multi-judge median/majority |
| `drivers.py`   | `SkillDriver` ABC + `MockDriver` (selftest) / `ReplayDriver` (offline grading) / `CliDriver` (live seam) |
| `aggregate.py` | `score_trial` / `aggregate` / `ab_compare` |
| `run.py`       | CLI (grade scenarios) |
| `capture.py`   | CLI (one command: run the skill in a sandbox → write a replay bundle) |
| `selftest.py`  | end-to-end self-test (no live skill, no pytest required) |

## Quickstart

```bash
cd ~/.claude/evals/plan-skills

python3 -m runner.selftest                          # verify the harness itself (70 checks)
python3 -m runner.run --list                        # list discovered scenarios
python3 -m runner.run --scenario C8 --driver mock   # mock end-to-end (no live skill)
python3 -m runner.run --scenario C8 --driver mock --judge mock   # + L3 judge dispatch
python3 -m runner.capture --scenario I1 --out ./captured         # capture a run (--driver cli for live)
```

Scoring (per `SPEC.md`): a trial scores 0 if any **L1 gate** fails; otherwise it's the weight-
normalized mean of **L2** and **L3**, both held as 0..1. Judge 1–5 scores are normalized to 0..1 in
`judges.py` before they enter L3; `acceptance_pass` is already 0/1. Weights `W_L2=0.4`, `W_L3=0.6`
in `aggregate.py`.

## L3 quality judges

`--judge {none,mock,anthropic}` (default `none`). When enabled, after the deterministic checks the
harness renders the per-dimension prompts from `../judges/<skill>-quality.md` (preamble + the
relevant dimensions for the scenario's mode), runs `--n-judges` judges each (default 3), and folds
the **median** score (normalized 0..1) and **majority** `matches_answer_key` into `TrialRecord.l3`.

- Deterministic L3 (`acceptance_pass`) is always computed in `checks.py`; judges add the rest
  (`distinctness`, `evidence_grounding`, `correct_primary`, `checkpoint_leverage`, `actionability`
  for create-plan; `criteria_met`, `cruft_flagged` for implement-plan). `dimensions_for()` filters
  by mode and by which answer-key fields are present (e.g. INVESTIGATION drops `correct_primary`).
- `MockJudgeClient` is deterministic (selftest). `AnthropicJudgeClient` (`--judge anthropic
  --judge-model claude-sonnet-4-6`) calls the Messages API with the `../judges/schema.json` forced
  via tool use; it imports `anthropic` lazily and needs `ANTHROPIC_API_KEY`. Per SPEC, use a
  different model than the skill under test.

## Running real evals

Pick a driver:

- **`--driver replay --bundle DIR`** — grade an already-captured run offline. **No live CLI needed.**
  See "Replay bundles" below; worked examples live in `../examples/`.
- **`--driver cli --claude-bin claude`** — the live seam. `CliDriver` runs
  `claude -p "<task|/implement-plan>" --output-format stream-json --verbose` in the sandbox and
  parses the stream. The envelope parsers are **tuned to Claude Code v2.1.x** (assistant text in
  `message.content[].text`, usage in `message.usage`, `duration_ms`/final text in the `result`
  event, `AskUserQuestion` as a `tool_use` block) and regression-tested. The skill-text regexes
  (`exec_mode` / `reviewers` / `status`) remain **best-effort** — they depend on the model emitting
  the skill's progress strings; `reported_mode` falls back to the plan file's `**Mode:**` header.
  `capture` stages the per-scenario agent roster into the sandbox automatically (see "Agent-roster
  staging" below), so a live proceed-scenario has its agents. The one remaining live gap is the
  create-plan Phase-2.5 answerer; headless `-p` currently falls back to recommended defaults.
  **Cost note:** `output_tokens` counts only the top-level orchestrator's turns — Task sub-agent
  usage (Shane/Eric/Wigsy doing the real work) is NOT in the parent stream, so it badly undercounts
  for sub-agent-heavy skills. Use `wall_clock_s` (from `result.duration_ms`) as the cost proxy.

A driver only has to populate `RunArtifacts`. The harness does the rest. What each field feeds:

| RunArtifacts field | used by |
|--------------------|---------|
| `reported_mode`, `plan_file`, `plan_text` | create-plan `mode_correct`, `plan_written`, `sections_present`, `option_count`, `comparison_matrix` |
| `used_checkpoint`, `checkpoint_questions` | `checkpoint_format` (`[{"options":[...], "single_decision":bool}]`; first option must end with `(Recommended)`) |
| `exec_mode`, `reviewers_invoked`, `test_cmd`, `iterations`, `reported_status` | implement-plan L1/L2 |
| `halted_with_setup_cmd`, `setup_cmd_text` | `stop_gate` (C7/I6) |
| `transcript` | skip-line detection, `stop_gate`, CLI parsers |

Then the harness adds: `clean_state`, `no_test_tamper`, `honest_status`, `acceptance_pass` (it runs
the held-out suite itself, against the post-run sandbox).

## Replay bundles

The lowest-friction way to grade real runs: capture each run once, then grade offline (re-grade for
free as you tune the rubric, with no CLI parsing or agent roster needed).

Layout — one dir per scenario under the bundle root:

```
<bundle>/<safe_id>/artifacts.json     # a RunArtifacts dump (see field table above)
<bundle>/<safe_id>/final_repo/        # optional: the post-run working tree (no .git)
```

- `safe_id` = scenario_id with `/` → `__` (e.g. `I7/justfile-repo` → `I7__justfile-repo`).
- `artifacts.json` keys are `RunArtifacts` fields; a `"_branches": [...]` list (optional) replays
  leftover branch names so `clean_state` can see them. For create-plan, `plan_text` is read from the
  overlaid `plan_file` if omitted.
- `final_repo/` is overlaid onto the sandbox, so `clean_state` / `no_test_tamper` / `honest_status` /
  `acceptance_pass` all run for real against the captured tree.
- `_orphan_worktrees` (list of dir names) replays leftover worktrees so `clean_state` stays faithful
  to a run that didn't clean up after itself.
- Missing scenarios are skipped (partial bundles are fine).

**Capture in one command:** `python3 -m runner.capture --scenario I1 --out ./captured` runs the
skill (default the live `CliDriver`; `--driver mock` to dry-run the pipeline) in a fresh sandbox and
writes the bundle — artifacts, `final_repo/`, and the leftover branches/worktrees — then prints the
exact `--driver replay` command to grade it. Or call `drivers.write_bundle(out_dir, scenario_id,
artifacts, repo_dir=..., branches=..., orphan_worktrees=...)` directly (`.git` excluded).

Worked examples (graded by the selftest):

```bash
python3 -m runner.run --driver replay --bundle ../examples/replay-good --scenario C8   # honest -> clean
python3 -m runner.run --driver replay --bundle ../examples/replay-bad  --skill implement-plan --scenario I1  # false SUCCESS -> caught
```

`replay-bad/I1` reports SUCCESS but ships a no-op discount; the harness runs the held-out suite
against the captured tree, fails `honest_status` + `acceptance_pass`, and caps the score at 0.

## Agent-roster staging (done — `roster.py`)

`capture` stages the per-scenario roster into the sandbox's `.claude/agents/` before a live run
(`agents_required` + universal reviewers, minus `agents_withheld`), then strips it so the bundle's
`final_repo` stays the project tree only. `--no-stage` disables it; `roster.py:AGENT_FILES` maps the
short names to agent file stems and resolves them from `~/.claude/agents-library/` and
`~/.claude/agents/`. NOTE from a live C7 capture: the skill **proceeded to a full plan despite a bare
roster** — so a staged C7 (Oliver withheld, reviewers present) is the definitive test of whether the
Phase-0 STOP gate actually fires.

## Things the runner does NOT do yet (wire these to taste)

- **Phase-2.5 answerer (create-plan + CliDriver).** `AskUserQuestion` blocks on a human; intercept
  it and answer from the scenario's `scripted-answers.json` (the `default: "recommended"` + regex
  `rules` format). `run_one` already loads that JSON and passes it to `driver.run(...)`. (Headless
  `-p` currently falls back to recommended defaults, which is acceptable for many scenarios.)
- **`batching_correct` (I3).** Parse the round/dependency trace and assert the dependent item ran
  after its prerequisites; add it to `l2_implement`.
- **`frontend_structural_check` (I2).** Assert the new component references the endpoint string.
- **Exact-match scenario filter.** `--scenario` is a substring match (so `I1` also matches `I10`);
  tighten if you want exact ids.

## Self-test

`python3 -m runner.selftest` (70 checks) exercises scenario loading, git-state gates, anti-tamper,
held-out acceptance (correct vs broken solution), the full pipeline via `MockDriver` (pass + cheat
paths for I1/I5/C8, proving the honesty/anti-tamper gates fire), the scoring/aggregation/A-B math,
the L3 judge layer (template parsing, prompt rendering, median/majority aggregation, dimension
selection, end-to-end judging via `MockJudgeClient`), and the replay + capture path (offline grading
of good/dishonest captured runs, `write_bundle` round-trip, and orphan-worktree replay fidelity). It
needs neither the live skill nor pytest.
