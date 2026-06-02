"""CLI: run the eval set against a skill version and emit per-trial JSON records.

Examples:
  python -m runner.run --list
  python -m runner.run --skill implement-plan --scenario I1 --trials 1 --driver mock
  python -m runner.run --driver replay --bundle ./captured --version v3 --out records.jsonl
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import checks
from .aggregate import aggregate, score_trial
from .contracts import TrialRecord, load_scenarios
from .drivers import CliDriver, MockDriver, ReplayDriver
from .judges import AnthropicJudgeClient, MockJudgeClient, judge_trial
from .sandbox import Sandbox

FIXTURES = Path(__file__).resolve().parent.parent / "fixtures"


def build_driver(name: str, args):
    if name == "mock":
        return MockDriver(mode=args.mock_mode)
    if name == "replay":
        return ReplayDriver(Path(args.bundle))
    if name == "cli":
        return CliDriver(claude_bin=args.claude_bin)
    raise SystemExit(f"unknown driver: {name}")


def build_judge(name: str, args):
    if name == "none":
        return None
    if name == "mock":
        return MockJudgeClient()
    if name == "anthropic":
        return AnthropicJudgeClient(model=args.judge_model)
    raise SystemExit(f"unknown judge: {name}")


def run_one(scenario, driver, version, trial, judge=None, n_judges=3) -> TrialRecord:
    scripted = json.loads(scenario.scripted_answers_path.read_text()) if scenario.scripted_answers_path else None
    sb = Sandbox.materialize(scenario.repo_dir, seeded_tests=scenario.seeded_tests)
    rec = TrialRecord(
        scenario=scenario.scenario_id,
        skill=scenario.skill,
        skill_version=version,
        trial=trial,
        status_expected=scenario.status_expected,
    )
    try:
        art = driver.run(scenario, sb, scripted)
        rec.status_reported = art.reported_status
        rec.cost = {"output_tokens": art.output_tokens, "wall_clock_s": art.wall_clock_s, "iterations": art.iterations}
        test_results = ""
        if scenario.skill == "create-plan":
            rec.l1 = checks.l1_create(art, scenario)
            rec.l2 = checks.l2_create(art, scenario)
        else:
            rec.l1 = checks.l1_implement(art, scenario, sb)  # must run before sb.diff() stages files
            rec.l2 = checks.l2_implement(art, scenario)
            ap = checks.acceptance_pass(scenario, sb)
            if ap is not None:
                rec.l3["acceptance_pass"] = ap
                test_results = f"held-out acceptance: {'PASS' if ap else 'FAIL'}"
        # L3 quality judges (optional)
        if judge is not None and scenario.expected_gate != "stop":
            judged = judge_trial(scenario, art, sb, judge, n_judges=n_judges, test_results=test_results)
            for dim, agg in judged.items():
                rec.l3[dim] = agg["score_norm"]
                rec.notes.append(f"judge {dim}: {agg['score']}/5 matches={agg['matches_answer_key']}")
        rec.l1_pass, rec.score = score_trial(rec.l1, rec.l2, rec.l3)
    except NotImplementedError as e:
        rec.notes.append(f"skipped: {e}")
    finally:
        sb.cleanup()
    return rec


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--skill", choices=["create-plan", "implement-plan"])
    ap.add_argument("--scenario", help="substring filter on scenario_id (e.g. I1, C8)")
    ap.add_argument("--trials", type=int, default=1)
    ap.add_argument("--version", default="dev")
    ap.add_argument("--driver", default="mock", choices=["mock", "replay", "cli"])
    ap.add_argument("--mock-mode", default="pass", choices=["pass", "cheat"])
    ap.add_argument("--bundle", help="bundle dir for replay driver")
    ap.add_argument("--claude-bin", default="claude")
    ap.add_argument("--judge", default="none", choices=["none", "mock", "anthropic"], help="L3 quality judge")
    ap.add_argument("--judge-model", default="claude-sonnet-4-6")
    ap.add_argument("--n-judges", type=int, default=3)
    ap.add_argument("--out", help="write JSONL records here (default stdout)")
    ap.add_argument("--list", action="store_true", help="list discovered scenarios and exit")
    args = ap.parse_args(argv)

    scenarios = load_scenarios(FIXTURES)
    if args.skill:
        scenarios = [s for s in scenarios if s.skill == args.skill]
    if args.scenario:
        scenarios = [s for s in scenarios if args.scenario in s.scenario_id]

    if args.list:
        for s in scenarios:
            print(f"{s.scenario_id:22} {s.skill:15} gate={s.expected_gate}")
        return 0

    driver = build_driver(args.driver, args)
    judge = build_judge(args.judge, args)
    records = []
    for s in scenarios:
        for t in range(1, args.trials + 1):
            records.append(run_one(s, driver, args.version, t, judge=judge, n_judges=args.n_judges))

    lines = [json.dumps(r.to_dict()) for r in records]
    if args.out:
        Path(args.out).write_text("\n".join(lines) + "\n")
    else:
        print("\n".join(lines))

    summary = aggregate(records)
    print("\n=== aggregate ===", file=sys.stderr)
    print(json.dumps(summary, indent=2), file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
