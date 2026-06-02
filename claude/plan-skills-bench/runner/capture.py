"""Capture a live skill run into a replay bundle, in one command.

    python -m runner.capture --scenario I1 --out ./captured                 # live CLI run
    python -m runner.capture --scenario C8 --out ./captured --driver mock   # exercise the pipeline

Materializes the scenario's repo into a fresh sandbox, runs the skill (default: the live CliDriver),
then writes a replay bundle — artifacts.json + final_repo/ + the leftover git state (branches and
orphan worktrees) — that you can grade offline with `--driver replay`. Re-grade for free as you tune
the rubric; no live CLI needed after capture.

Note: for create-plan under the live CliDriver you must still wire the Phase-2.5 answerer (the
scenario's scripted-answers.json is loaded and passed to the driver here).
"""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

from .contracts import load_scenarios
from .drivers import CliDriver, MockDriver, write_bundle
from .roster import roster_for, stage_roster
from .sandbox import Sandbox

FIXTURES = Path(__file__).resolve().parent.parent / "fixtures"


def pick_scenario(scenarios, sid):
    exact = [s for s in scenarios if s.scenario_id == sid]
    if exact:
        return exact[0]
    subs = [s for s in scenarios if sid in s.scenario_id]
    if len(subs) == 1:
        return subs[0]
    if not subs:
        raise SystemExit(f"no scenario matches {sid!r}")
    raise SystemExit(f"{sid!r} is ambiguous: {[s.scenario_id for s in subs]}")


def capture(scenario, driver, out_dir: Path, stage=True):
    """Run the scenario via `driver` in a fresh sandbox and write a replay bundle.

    Returns (bundle_dir, staged, missing). When `stage` is True, the per-scenario agent roster is
    copied into the sandbox's .claude/agents/ before the run (so a live proceed-scenario has its
    agents) and stripped afterward so it doesn't pollute the captured tree.
    """
    scripted = json.loads(scenario.scripted_answers_path.read_text()) if scenario.scripted_answers_path else None
    sb = Sandbox.materialize(scenario.repo_dir, seeded_tests=scenario.seeded_tests)
    staged, missing = [], []
    try:
        if stage:
            staged, missing = stage_roster(sb.path, roster_for(scenario))
        # implement-plan reads plan.md from the repo it runs in; the fixture keeps it beside repo/,
        # so inject it into the sandbox (and strip it after, so final_repo stays the project tree).
        injected_plan = False
        if scenario.skill == "implement-plan" and scenario.plan_path and scenario.plan_path.exists():
            shutil.copyfile(scenario.plan_path, sb.path / "plan.md")
            injected_plan = True
        art = driver.run(scenario, sb, scripted)
        # strip harness scaffolding so the bundle's final_repo is the project tree + skill changes only
        agents_dir = sb.path / ".claude" / "agents"
        if stage and agents_dir.exists():
            shutil.rmtree(agents_dir, ignore_errors=True)
        if injected_plan and (sb.path / "plan.md").exists():
            (sb.path / "plan.md").unlink()
        d = write_bundle(
            out_dir,
            scenario.scenario_id,
            art,
            repo_dir=sb.path,
            branches=sb.temp_branches(),
            orphan_worktrees=[Path(w).name for w in sb.orphan_worktrees()],
        )
        return d, staged, missing
    finally:
        sb.cleanup()


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--scenario", required=True, help="scenario id (exact, or an unambiguous substring)")
    ap.add_argument("--out", required=True, help="bundle root dir")
    ap.add_argument("--driver", default="cli", choices=["cli", "mock"])
    ap.add_argument("--claude-bin", default="claude")
    ap.add_argument("--mock-mode", default="pass", choices=["pass", "cheat"])
    ap.add_argument("--no-stage", action="store_true", help="do not stage the agent roster into the sandbox")
    args = ap.parse_args(argv)

    scenario = pick_scenario(load_scenarios(FIXTURES), args.scenario)
    driver = CliDriver(claude_bin=args.claude_bin) if args.driver == "cli" else MockDriver(mode=args.mock_mode)
    d, staged, missing = capture(scenario, driver, Path(args.out), stage=not args.no_stage)

    if not args.no_stage:
        print(f"staged agents:   {staged or '(none)'}")
        if missing:
            print(f"MISSING sources: {missing}  (not found under ~/.claude/agents-library or ~/.claude/agents)")
    print(f"captured bundle: {d}")
    print(f"grade it:        python3 -m runner.run --driver replay --bundle {args.out} "
          f"--skill {scenario.skill} --scenario {scenario.scenario_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
