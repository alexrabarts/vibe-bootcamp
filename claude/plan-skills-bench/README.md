# Plan-skills bench

Evidence that two Claude Code planning skills — `/create-plan` and `/implement-plan` —
actually change outcomes, not just vibes. An eval set, a self-tested harness, and three
real skill runs graded against ground truth.

Open **`REPORT.html`** for the findings (or `REPORT.md` for the plain version).

## What's here

| Path | What it is |
|------|------------|
| `REPORT.html` / `REPORT.md` | The findings write-up — method, scorecard, limitations |
| `SPEC.md` | The eval set: 22 scenarios + the L1/L2/L3 grading rubric |
| `runner/` | A self-tested harness (deterministic gates, LLM-judge dispatch, replay + capture). `python3 -m runner.selftest` → **78/78** |
| `fixtures/` | The scenarios — synthetic repos + ground-truth answer keys |
| `judges/` | Adversarial LLM-judge prompts for the quality dimensions |
| `examples/` | Worked replay bundles — an honest run and a dishonest one |
| `captured/` | Three real, live-graded skill runs — the evidence |

## Headline findings

- **create-plan honours its anti-surface-level mandate.** On a planted "surface trap" — a bug
  report dangling two decoys over a deeper cause — it traced inward, picked the deep root cause,
  and refuted both decoys (C8, score **1.0**).
- **The two skills handle a missing required agent differently, by design.** `create-plan` degrades
  gracefully when a read-only *explorer* is absent (substitutes a generic agent, notes the
  deviation, proceeds); `implement-plan` *hard-stops* when an *implementer* is absent (won't write
  code with a substitute). Risk-appropriate — C7 **0.8** / I6 **1.0**.
- **The live runs also caught four bugs in the harness itself** (all fixed + regression-tested) —
  the benchmark debugging itself is part of the evidence that live measurement beats assumptions.

## How it grades

Each run scores 0 if any **L1** gate fails (correctness / honesty / safety), else the weighted mean
of **L2** deterministic structural checks and **L3** LLM-judge quality dimensions. The harness runs
the skill in a sandbox, then grades from the captured bundle — so runs can be re-graded offline as
the rubric evolves. See `SPEC.md` and `runner/README.md`.

## Honest scope

The live captures so far are the two missing-agent scenarios and the surface-trap.
`implement-plan`'s actual implementation quality (correct code, convergence, cleanup) is validated
by the harness via mock/replay but not yet on a live proceed run. See the report's limitations.
