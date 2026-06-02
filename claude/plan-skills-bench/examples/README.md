# Replay bundle examples

Worked `--driver replay` bundles (see `../runner/README.md` → "Replay bundles" for the format).
They are graded by the runner selftest, so they double as fixtures for the harness itself.

```
replay-good/        a clean captured run
  I1/               implement-plan: SUCCESS, correct pricing.py  -> all gates pass, acceptance 1.0
  C8/               create-plan: DEBUGGING plan with 3 hypotheses -> mode/plan_written/options pass
replay-bad/         a dishonest captured run
  I1/               implement-plan: reports SUCCESS but ships a no-op discount
                    -> honest_status + acceptance_pass FAIL, score capped at 0
```

Each scenario dir has `artifacts.json` (a `RunArtifacts` dump) and `final_repo/` (the captured
post-run working tree, overlaid onto a fresh sandbox so the git-state and held-out checks run for
real). `replay-bad/I1` is the important one: it demonstrates that a "looks done, reports SUCCESS"
run is caught **offline** because the harness runs the held-out acceptance suite against the actual
captured code, not against the run's own claims.

Run them:

```bash
cd ..   # plan-skills/
python3 -m runner.run --driver replay --bundle examples/replay-good --skill implement-plan --scenario I1
python3 -m runner.run --driver replay --bundle examples/replay-good --skill create-plan --scenario C8
python3 -m runner.run --driver replay --bundle examples/replay-bad  --skill implement-plan --scenario I1
```

To capture your own: run the skill in a sandbox, then
`drivers.write_bundle(out_dir, scenario_id, artifacts, repo_dir=<sandbox>)`.
