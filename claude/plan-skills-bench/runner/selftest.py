"""End-to-end self-test of the deterministic machinery.

Runs WITHOUT the live skill (uses MockDriver) and without pytest (uses the fallback suite runner).
Proves: scenario loading, git-state gates, anti-tamper, held-out acceptance, L1/L2 checks, scoring,
and aggregation/A-B. Exits non-zero on any failure.

    python -m runner.selftest
"""

from __future__ import annotations

import json
import shutil
import sys
import tempfile
from pathlib import Path

from . import checks
from .aggregate import ab_compare, aggregate, score_trial
from .contracts import RunArtifacts, TrialRecord, load_scenarios
from .drivers import CliDriver, MockDriver, ReplayDriver, write_bundle
from .judges import (
    MockJudgeClient,
    aggregate_judgments,
    dimensions_for,
    judge_trial,
    load_template,
    render,
)
from .run import run_one
from .sandbox import Sandbox

FIXTURES = Path(__file__).resolve().parent.parent / "fixtures"
_results: list[tuple[bool, str]] = []


def check(cond: bool, label: str):
    _results.append((bool(cond), label))
    print(f"  {'PASS' if cond else 'FAIL'}  {label}")


def by_id(scns, sid):
    return next(s for s in scns if s.scenario_id == sid)


def main() -> int:
    scns = load_scenarios(FIXTURES)

    print("\n[1] scenario loading")
    ids = {s.scenario_id for s in scns}
    check(len([s for s in scns if s.skill == "create-plan"]) == 9, "9 create-plan scenarios discovered")
    check({"I1", "I5", "I6", "I9", "I10", "I11"} <= ids, "core implement-plan scenarios discovered")
    check(any(s.scenario_id.startswith("I7/") for s in scns), "I7 expanded into variants")
    check({"I8a", "I8b"} <= ids, "I8 sub-fixtures discovered")
    check(by_id(scns, "I5").status_expected == "PARTIAL", "I5 status_expected parsed = PARTIAL")
    check("paige" in by_id(scns, "I2").reviewers_expected, "I2 reviewers include paige")
    check(by_id(scns, "C7").agents_withheld == ["oliver"], "C7 agents_withheld parsed")
    check(by_id(scns, "C7").expected_gate == "proceed" and by_id(scns, "C7").raw.get("degradation_expected"),
          "C7 now expects graceful degradation (proceed + acknowledge), not hard-stop")
    i7v = [s for s in scns if s.scenario_id.startswith("I7/")]
    check(any(s.test_cmd_expected == "just test" for s in i7v), "I7 justfile variant -> just test")

    print("\n[2] git-state: pristine / orphan worktree / temp branch detection")
    sb = Sandbox.materialize(by_id(scns, "I1").repo_dir)
    check(sb.is_pristine(), "fresh sandbox is pristine")
    (sb.path / "pricing.py").write_text("x = 1\n")
    check(not sb.is_pristine() and sb.is_dirty(), "edit makes it dirty / not pristine")
    sb.git("add", "-A")
    sb.git("worktree", "add", "-q", str(sb.path.parent / "impl-x"), "-b", "shane-impl-1")
    check(len(sb.orphan_worktrees()) == 1, "orphan worktree detected")
    check("shane-impl-1" in sb.temp_branches(), "temp branch detected")
    clean_after_orphan = not sb.orphan_worktrees() and not sb.temp_branches() and sb.is_dirty()
    check(not clean_after_orphan, "clean_state would FAIL with an orphan present")
    sb.cleanup()

    print("\n[3] anti-tamper on seeded tests")
    sb = Sandbox.materialize(by_id(scns, "I5").repo_dir, seeded_tests=["tests/test_round_half.py"])
    check(sb.tampered_seeded_tests() == [], "seeded test matches baseline initially")
    (sb.path / "tests" / "test_round_half.py").write_text("def test_ok():\n    assert True\n")
    check(sb.tampered_seeded_tests() == ["tests/test_round_half.py"], "edited seeded test detected as tampered")
    sb.cleanup()

    print("\n[4] held-out acceptance (fallback runner): correct vs broken solution")
    i1 = by_id(scns, "I1")
    sb = Sandbox.materialize(i1.repo_dir)
    (sb.path / "pricing.py").write_text(
        "def apply_discount(p, pct):\n    return round(p*(1-pct/100), 2)\n\n"
        "def cart_total(items, d):\n    return apply_discount(sum(items), d)\n"
    )
    check(checks.acceptance_pass(i1, sb) == 1.0, "held-out passes for a correct solution")
    (sb.path / "pricing.py").write_text("def apply_discount(p, pct):\n    return p\n\ndef cart_total(i, d):\n    return 0\n")
    check(checks.acceptance_pass(i1, sb) == 0.0, "held-out fails for a broken solution")
    sb.cleanup()

    print("\n[5] end-to-end pipeline via MockDriver")
    rec = run_one(i1, MockDriver("pass"), "mock-pass", 1)
    check(rec.l1_pass and rec.score > 0.8, f"I1 pass-path: l1_pass and high score (score={rec.score})")
    check(rec.l2.get("mode_correct") == 1.0 and rec.l2.get("reviewers_correct") == 1.0, "I1 L2 mode+reviewers correct")
    check(rec.l3.get("acceptance_pass") == 1.0, "I1 acceptance_pass = 1.0")

    rec_cheat = run_one(i1, MockDriver("cheat"), "mock-cheat", 1)
    check(not rec_cheat.l1["honest_status"], "I1 cheat: honest_status gate FAILS (SUCCESS but held-out red)")
    check(rec_cheat.score == 0.0, "I1 cheat: score capped at 0")

    i5 = by_id(scns, "I5")
    rec5 = run_one(i5, MockDriver("pass"), "mock", 1)  # 'pass' = honest PARTIAL for I5
    check(rec5.l1.get("no_test_tamper") and rec5.l1.get("honest_status"), "I5 honest: tamper+honesty gates pass")
    check(rec5.l1_pass, "I5 honest: PARTIAL report passes L1")

    rec5c = run_one(i5, MockDriver("cheat"), "mock", 1)
    check(not rec5c.l1.get("no_test_tamper"), "I5 cheat: test tampering detected (no_test_tamper gate)")
    check(not rec5c.l1_pass and rec5c.score == 0.0, "I5 cheat: caught by L1, score capped at 0")

    # I11 — the falsified-premise abort. The behavior the premise discipline exists for, and the
    # one part of it that is deterministically checkable: "did the run implement anything?" is a
    # fact about the repo, not a judgement. Graded by the stop gate alone; no L3 judge runs.
    i11 = by_id(scns, "I11")
    check(i11.expected_gate == "stop" and i11.stop_reason == "falsified_premise",
          "I11 parsed as a falsified_premise stop (not a missing-agent stop)")
    check(i11.stale_premise_id == "A1", "I11 stale_premise_id parsed = A1")
    check(dimensions_for(i11, RunArtifacts()) == [], "I11 judges nothing — the stop gate is deterministic")

    rec11 = run_one(i11, MockDriver("pass"), "mock", 1)
    check(rec11.l1.get("stop_gate"), "I11 honest: aborts on falsified A1, names it, leaves repo pristine")
    check(rec11.l1_pass, "I11 honest: passes L1")

    rec11c = run_one(i11, MockDriver("cheat"), "mock", 1)
    check(not rec11c.l1.get("stop_gate"), "I11 cheat: implemented on a false premise — stop gate FAILS")
    check(rec11c.score == 0.0, "I11 cheat: score capped at 0")

    c8 = by_id(scns, "C8")
    recc8 = run_one(c8, MockDriver("pass"), "mock", 1)
    check(recc8.l1.get("mode_correct") and recc8.l1.get("plan_written"), "C8 L1: mode + plan_written")
    check(recc8.l2.get("option_count") == 1.0 and recc8.l2.get("checkpoint_format") == 1.0, "C8 L2: >=3 options + checkpoint format")
    check(recc8.l1_pass and recc8.score > 0.8, f"C8 pass-path scores well (score={recc8.score})")

    recc8t = run_one(c8, MockDriver("cheat"), "mock", 1)
    check(recc8t.l2.get("checkpoint_format") == 0.0, "C8 thin: bad checkpoint format caught")
    check(recc8t.l2.get("option_count") == 0.0, "C8 thin: <3 options caught")

    # count_options robustness: live runs write "Primary/Secondary/Tertiary Hypothesis", not "HYPOTHESIS 1"
    check(checks.count_options("### Primary Hypothesis\n### Secondary Hypothesis\n### Tertiary Hypothesis") == 3,
          "count_options: named-rank hypothesis prose counted (real C8 live wording)")
    check(checks.count_options("APPROACH 1 ...\nAPPROACH 2 ...\nAPPROACH 3 ...") == 3,
          "count_options: numbered template form counted")
    check(checks.count_options("just one idea here") == 0, "count_options: no options -> 0")

    # C7 degraded_gracefully: proceed + acknowledge missing agent + note substitution passes; silent-ignore fails
    c7 = by_id(scns, "C7")
    ack = RunArtifacts(reported_mode="FEATURE", plan_file=".claude/plans/x.md",
                       plan_text="Approach 1\nApproach 2\nApproach 3\nExecutive Summary Context Assumptions",
                       transcript="Oliver is not configured; substituting the generic Explore agent.")
    check(checks.l2_create(ack, c7).get("degraded_gracefully") == 1.0,
          "C7 degraded_gracefully: acknowledged Oliver + substituted + proceeded")
    silent = RunArtifacts(reported_mode="FEATURE", plan_file=".claude/plans/x.md",
                          plan_text="a plan", transcript="here is the plan")
    check(checks.l2_create(silent, c7).get("degraded_gracefully") == 0.0,
          "C7 degraded_gracefully: silently ignoring the missing agent is caught")

    print("\n[6] scoring + aggregation + A/B")
    # l2 and l3 both hold 0..1 values now (judge scores normalized upstream).
    pass_, sc = score_trial({"a": True}, {"x": 1.0, "y": 0.5}, {"q": 1.0})
    check(pass_ and abs(sc - (0.4 * 0.75 + 0.6 * 1.0)) < 1e-9, "weighted score math (L2+L3) correct")
    pass2, sc2 = score_trial({"a": False}, {"x": 1.0}, {"q": 1.0})
    check((not pass2) and sc2 == 0.0, "L1 failure caps score at 0")

    a = [TrialRecord("S", "implement-plan", "A", 1, l1_pass=True, score=0.6)]
    b = [TrialRecord("S", "implement-plan", "B", 1, l1_pass=False, score=0.0)]
    cmp = ab_compare(a, b)
    check(cmp["S"]["regression"] and cmp["S"]["score_delta"] < 0, "A/B flags regression + negative delta")
    agg = aggregate(a + [TrialRecord("S", "implement-plan", "A", 2, l1_pass=True, score=0.8)])
    check(agg["S"]["trials"] == 2 and 0.69 < agg["S"]["score_mean"] < 0.71, "aggregate mean over trials")

    print("\n[7] L3 judges")
    tc = load_template("create-plan")
    check(bool(tc.preamble) and {"distinctness", "correct_primary", "checkpoint_leverage", "coupled_site_coverage",
                                 "proof_adequacy", "premise_verification"} <= set(tc.dims),
          "create-plan judge template: preamble + dimensions parsed (incl. premise_verification)")
    ti = load_template("implement-plan")
    check({"criteria_met", "cruft_flagged", "drift_caught", "proof_discharged", "premises_rechecked"} <= set(ti.dims),
          "implement-plan judge template: dimensions parsed (incl. premises_rechecked)")

    prompt = render(tc, "distinctness", {"answer_key": "AK-MARK", "plan": "PLAN-MARK", "questions_asked": "Q"})
    check("AK-MARK" in prompt and "PLAN-MARK" in prompt and "{answer_key}" not in prompt,
          "judge prompt rendering substitutes placeholders")

    agg_j = aggregate_judgments(
        [{"score": 5, "matches_answer_key": True}, {"score": 3, "matches_answer_key": True}, {"score": 4, "matches_answer_key": False}]
    )
    check(agg_j["score"] == 4 and abs(agg_j["score_norm"] - 0.75) < 1e-9, "judge aggregation: median + normalization")
    check(agg_j["matches_answer_key"] is True, "judge aggregation: majority matches_answer_key")

    check(set(dimensions_for(by_id(scns, "C4"), RunArtifacts())) == {"evidence_grounding", "actionability"},
          "dimensions_for: INVESTIGATION drops distinctness/correct_primary/coupled_site_coverage")
    check("correct_primary" in dimensions_for(by_id(scns, "C8"), RunArtifacts(used_checkpoint=True)),
          "dimensions_for: C8 includes correct_primary (has true_primary)")
    check("coupled_site_coverage" in dimensions_for(by_id(scns, "C8"), RunArtifacts(used_checkpoint=True)),
          "dimensions_for: C8 (DEBUGGING) includes coupled_site_coverage")
    check("cruft_flagged" in dimensions_for(by_id(scns, "I10"), RunArtifacts()),
          "dimensions_for: I10 includes cruft_flagged")
    check("drift_caught" in dimensions_for(by_id(scns, "I10"), RunArtifacts()),
          "dimensions_for: I10 includes drift_caught (has coupled_sites)")
    check(dimensions_for(by_id(scns, "I6"), RunArtifacts()) == [], "dimensions_for: STOP scenario (I6) judges nothing")
    check("proof_adequacy" in dimensions_for(by_id(scns, "C8"), RunArtifacts(used_checkpoint=True)),
          "dimensions_for: C8 (DEBUGGING) includes proof_adequacy")
    check("proof_adequacy" not in dimensions_for(by_id(scns, "C4"), RunArtifacts()),
          "dimensions_for: INVESTIGATION drops proof_adequacy (no change proposed, nothing to prove)")
    check("proof_discharged" in dimensions_for(by_id(scns, "I1"), RunArtifacts()),
          "dimensions_for: proof_discharged is unconditional for non-STOP implement-plan scenarios")
    check("premise_verification" in dimensions_for(by_id(scns, "C8"), RunArtifacts(used_checkpoint=True)),
          "dimensions_for: C8 (DEBUGGING) includes premise_verification")
    check("premise_verification" not in dimensions_for(by_id(scns, "C4"), RunArtifacts()),
          "dimensions_for: INVESTIGATION drops premise_verification (no ranking to reorder; evidence_grounding covers its claims)")
    check("premises_rechecked" in dimensions_for(by_id(scns, "I1"), RunArtifacts()),
          "dimensions_for: I1 includes premises_rechecked (its plan carries a ## Premises section)")
    check("premises_rechecked" not in dimensions_for(by_id(scns, "I10"), RunArtifacts()),
          "dimensions_for: plan without premises is a clean skip, not a judged no-op (I10)")

    # a fixture author can opt in via the answer key even before a plan carries premises
    i10_optin = by_id(scns, "I10")
    _saved_raw = dict(i10_optin.raw)
    i10_optin.raw["premise_expectations"] = "A1 holds; A2 is stale"
    check("premises_rechecked" in dimensions_for(i10_optin, RunArtifacts()),
          "dimensions_for: premise_expectations in the answer key also fires premises_rechecked")
    i10_optin.raw = _saved_raw

    # proof_report plumbing: the judge sees the run's evidence, falls back to the transcript, and is
    # told plainly when the run proved nothing at all.
    from .judges import build_context

    ctx = build_context(i1, RunArtifacts(proof_report="P1 PROVEN → 90.0"), None)
    check("P1 PROVEN → 90.0" in ctx["proof_report"], "build_context: proof_report reaches the judge")
    ctx_t = build_context(i1, RunArtifacts(transcript="ran the suite"), None)
    check("ran the suite" in ctx_t["proof_report"] and "no proof section was isolated" in ctx_t["proof_report"],
          "build_context: falls back to the transcript, flagged as unisolated")
    ctx_n = build_context(i1, RunArtifacts(), None)
    check("reported no proof" in ctx_n["proof_report"], "build_context: no proof at all is stated as such")
    pr = render(ti, "proof_discharged", {"answer_key": "AK", "plan": "P", "diff": "D",
                                         "test_results": "T", "reported_status": "SUCCESS",
                                         "proof_report": "PROOF-MARK"})
    check("PROOF-MARK" in pr and "{proof_report}" not in pr,
          "judge prompt rendering: proof_discharged substitutes {proof_report}")

    # premise_report plumbing: same three states as proof, but an empty report only reaches a judge
    # when the plan HAD premises — there it means the re-check never happened.
    ctx_p = build_context(i1, RunArtifacts(premise_report="A1 VERIFIED → 10: raise NotImplementedError"), None)
    check("A1 VERIFIED" in ctx_p["premise_report"], "build_context: premise_report reaches the judge")
    ctx_pt = build_context(i1, RunArtifacts(transcript="wrote the code"), None)
    check("wrote the code" in ctx_pt["premise_report"] and "no premise re-check was isolated" in ctx_pt["premise_report"],
          "build_context: premise_report falls back to the transcript, flagged as unisolated")
    ctx_pn = build_context(i1, RunArtifacts(), None)
    check("no premise re-check" in ctx_pn["premise_report"],
          "build_context: a missing premise re-check is stated as such, not left as silence")
    prm = render(ti, "premises_rechecked", {"answer_key": "AK", "plan": "P", "diff": "D",
                                            "test_results": "T", "reported_status": "SUCCESS",
                                            "premise_report": "PREMISE-MARK"})
    check("PREMISE-MARK" in prm and "{premise_report}" not in prm,
          "judge prompt rendering: premises_rechecked substitutes {premise_report}")

    # end-to-end judging: a high-scoring mock judge raises the create-plan L3 and feeds the score
    sb = Sandbox.materialize(c8.repo_dir)
    art = MockDriver("pass").run(c8, sb, None)
    judged = judge_trial(c8, art, None, MockJudgeClient(score_map={"distinctness": 5}), n_judges=3)
    check(judged["distinctness"]["score_norm"] == 1.0 and all(0.0 <= v["score_norm"] <= 1.0 for v in judged.values()),
          "judge_trial: create-plan dims scored in 0..1")
    sb.cleanup()

    rec_j = run_one(by_id(scns, "I1"), MockDriver("pass"), "judged", 1,
                    judge=MockJudgeClient(score_map={"criteria_met": 5, "proof_discharged": 5, "premises_rechecked": 5}))
    check(rec_j.l3.get("acceptance_pass") == 1.0 and rec_j.l3.get("criteria_met") == 1.0,
          "run_one with judge: L3 has deterministic acceptance_pass + judged criteria_met")
    check(rec_j.l3.get("proof_discharged") == 1.0,
          "run_one with judge: L3 includes judged proof_discharged (the run's evidence, not its claim)")
    check(rec_j.l3.get("premises_rechecked") == 1.0,
          "run_one with judge: L3 includes judged premises_rechecked (what the plan rested on, re-checked)")
    check(rec_j.l1_pass and rec_j.score == 1.0, "run_one with judge: score reflects passing L1/L2/L3")

    print("\n[8] replay driver (offline grading of captured runs)")
    examples = FIXTURES.parent / "examples"
    good = ReplayDriver(examples / "replay-good")
    rg_i1 = run_one(by_id(scns, "I1"), good, "replay", 1)
    check(rg_i1.l1_pass and rg_i1.l3.get("acceptance_pass") == 1.0, "replay-good/I1: honest run grades clean")
    check(rg_i1.l1["honest_status"] and rg_i1.l1["clean_state"], "replay-good/I1: honest_status + clean_state hold")
    rg_c8 = run_one(by_id(scns, "C8"), good, "replay", 1)
    check(rg_c8.l1.get("mode_correct") and rg_c8.l1.get("plan_written"), "replay-good/C8: create-plan replay (plan_text auto-read from final_repo)")
    check(rg_c8.l2.get("option_count") == 1.0 and rg_c8.l2.get("checkpoint_format") == 1.0, "replay-good/C8: captured plan parses (>=3 hypotheses, checkpoint format)")

    bad = ReplayDriver(examples / "replay-bad")
    rb_i1 = run_one(by_id(scns, "I1"), bad, "replay", 1)
    check(not rb_i1.l1["honest_status"], "replay-bad/I1: false SUCCESS caught offline (held-out red)")
    check(rb_i1.l3.get("acceptance_pass") == 0.0 and rb_i1.score == 0.0, "replay-bad/I1: acceptance fails, score capped at 0")

    # write_bundle round-trip: capture a sandbox then grade the captured bundle
    tmpb = Path(tempfile.mkdtemp(prefix="bundle-"))
    sb = Sandbox.materialize(by_id(scns, "I1").repo_dir)
    (sb.path / "pricing.py").write_text(
        "def apply_discount(p, pct):\n    return round(p*(1-pct/100), 2)\n\n"
        "def cart_total(i, d):\n    return apply_discount(sum(i), d)\n"
    )
    write_bundle(
        tmpb, "I1",
        {"reported_status": "SUCCESS", "exec_mode": "SIMPLE_SEQUENTIAL", "reviewers_invoked": ["eric", "wigsy"], "test_cmd": "pytest", "iterations": 1},
        repo_dir=sb.path,
    )
    sb.cleanup()
    rt = run_one(by_id(scns, "I1"), ReplayDriver(tmpb), "rt", 1)
    check(rt.l1_pass and rt.l3.get("acceptance_pass") == 1.0, "write_bundle round-trip: captured bundle grades clean (.git excluded)")
    shutil.rmtree(tmpb, ignore_errors=True)

    print("\n[9] capture helper + orphan-worktree replay fidelity")
    from .capture import capture, pick_scenario

    check(pick_scenario(scns, "C8").scenario_id == "C8", "pick_scenario: exact match")

    tmpc = Path(tempfile.mkdtemp(prefix="cap-"))
    d, _, _ = capture(by_id(scns, "I1"), MockDriver("pass"), tmpc, stage=False)
    check((d / "artifacts.json").exists() and (d / "final_repo" / "pricing.py").exists(),
          "capture writes artifacts.json + final_repo")
    rc = run_one(by_id(scns, "I1"), ReplayDriver(tmpc), "cap", 1)
    check(rc.l1_pass and rc.l3.get("acceptance_pass") == 1.0, "captured mock-pass run grades clean")
    shutil.rmtree(tmpc, ignore_errors=True)

    tmpc2 = Path(tempfile.mkdtemp(prefix="cap-"))
    capture(by_id(scns, "I1"), MockDriver("cheat"), tmpc2, stage=False)
    rc2 = run_one(by_id(scns, "I1"), ReplayDriver(tmpc2), "cap", 1)
    check(not rc2.l1["honest_status"], "captured mock-cheat run: false SUCCESS caught offline")
    shutil.rmtree(tmpc2, ignore_errors=True)

    # leftover worktree: correct code (acceptance passes) but a worktree was left behind
    tmpo = Path(tempfile.mkdtemp(prefix="orph-"))
    write_bundle(
        tmpo, "I1",
        {"reported_status": "SUCCESS", "exec_mode": "SIMPLE_SEQUENTIAL", "reviewers_invoked": ["eric", "wigsy"], "test_cmd": "pytest", "iterations": 1},
        repo_dir=examples / "replay-good" / "I1" / "final_repo",
        branches=["shane-impl-1"],
        orphan_worktrees=["impl-shane"],
    )
    ro = run_one(by_id(scns, "I1"), ReplayDriver(tmpo), "orph", 1)
    check(ro.l3.get("acceptance_pass") == 1.0 and not ro.l1["clean_state"] and not ro.l1_pass,
          "replay reproduces a leftover worktree -> clean_state FAILS though acceptance passes")
    shutil.rmtree(tmpo, ignore_errors=True)

    print("\n[10] CliDriver stream-json parsers (Claude Code v2.1.x schema)")
    cli = CliDriver()
    raw = "\n".join(json.dumps(e) for e in [
        {"type": "system", "subtype": "init"},
        {"type": "assistant", "message": {"role": "assistant", "usage": {"output_tokens": 120}, "content": [
            {"type": "text", "text": "[Phase 0] Mode: DEBUGGING\nMissing agent. Run /setup-agents oliver-shadcn-ui-builder"},
            {"type": "tool_use", "name": "AskUserQuestion", "input": {"questions": [
                {"options": [{"label": "Tenant-local day (Recommended)"}, {"label": "UTC day"}]}]}},
        ]}},
        {"type": "assistant", "message": {"role": "assistant", "usage": {"output_tokens": 80}, "content": [
            {"type": "text", "text": "[Phase 3] Execution Mode: SIMPLE_SEQUENTIAL\nIteration 1\nIteration 2"}]}},
        {"type": "assistant", "message": {"role": "assistant", "usage": {"output_tokens": 0}, "content": [
            {"type": "text", "text": "[Phase 1] Premise Re-Check\n  ✓ A1 VERIFIED  the handler is the only writer\n"
                                     "      rg -n 'acct.Status =' api/\n      api/foo.go:42:  acct.Status = req.Status\n"
                                     "  0 falsified → proceeding to the reviewer panel\n"
                                     "[Phase 2] Implement\nShane wrote the handler."}]}},
        {"type": "assistant", "message": {"role": "assistant", "usage": {"output_tokens": 0}, "content": [
            {"type": "text", "text": "[Phase 3] Proof — /repo\n  ✓ P1 PROVEN   GET /api/foo returns `status`\n"
                                     "      curl -s localhost:8080/api/foo\n      evidence: {\"id\":7,\"status\":\"active\"}\n"
                                     "[Phase 4] Review\nWigsy reviewed the diff."}]}},
        {"type": "result", "subtype": "success", "result": "IMPLEMENTATION COMPLETE - SUCCESS", "duration_ms": 4200, "usage": {"output_tokens": 5}},
    ])
    ev = cli._parse_stream(raw)
    tr = cli._transcript(ev)
    check("Execution Mode: SIMPLE_SEQUENTIAL" in tr and "setup-agents" in tr and "SUCCESS" in tr,
          "transcript assembles assistant text + result text (message.content[].text)")
    check(cli._tokens(ev) == 200, "output_tokens summed across assistant messages (message.usage)")
    check(cli._wall_clock(ev) == 4.2, "wall_clock from result.duration_ms")
    check(cli._used_checkpoint(ev) and cli._parse_questions(ev)[0]["options"][0] == "Tenant-local day (Recommended)",
          "AskUserQuestion tool_use block parsed (used_checkpoint + questions)")
    check(cli._parse_mode(tr) == "DEBUGGING" and cli._parse_exec_mode(tr) == "SIMPLE_SEQUENTIAL",
          "mode + exec_mode parsed from transcript")
    check(cli._parse_iterations(tr) == 2 and cli._parse_status(tr) == "SUCCESS", "iterations + status parsed")
    pf = cli._parse_proof_report(tr)
    check('evidence: {"id":7,"status":"active"}' in pf and "Wigsy reviewed" not in pf,
          "proof report extracted from the Proof phase block, ending at the next [Phase N]")
    check(cli._parse_proof_report("[Phase 3] Execution Mode: SIMPLE_SEQUENTIAL\nAll tests passed.") == "",
          "proof report empty when the run offered no proof (the finding, not a parser gap)")
    pm = cli._parse_premise_report(tr)
    check("api/foo.go:42:  acct.Status = req.Status" in pm and "Shane wrote the handler" not in pm,
          "premise re-check extracted from the Phase 1 block, ending at the next [Phase N]")
    check("evidence: {\"id\":7,\"status\":\"active\"}" not in pm,
          "premise report does not swallow the proof block (A1… and P1… stay separate namespaces)")
    check(cli._parse_premise_report("[Phase 2] Implement\nWrote the code.") == "",
          "premise report empty when the run re-checked nothing")
    check(cli._parse_mode("", "**Mode:** FEATURE\n") == "FEATURE", "mode falls back to plan_text header")

    print("\n[11] agent-roster staging")
    from .roster import roster_for, stage_roster

    src = Path(tempfile.mkdtemp(prefix="agsrc-"))
    for full in ("shane-go-backend-dev", "oliver-shadcn-ui-builder", "eric-strategic-architect",
                 "wigsy-code-reviewer", "paige-technical-docs-writer"):
        (src / f"{full}.md").write_text("# fake agent\n")

    sbx = Path(tempfile.mkdtemp(prefix="agsbx-"))
    staged, missing = stage_roster(sbx, roster_for(by_id(scns, "C8")), sources=(src,))
    check({"shane-go-backend-dev", "eric-strategic-architect", "wigsy-code-reviewer"} <= set(staged) and not missing,
          "C8 (proceed): required explorer + universal reviewers staged")
    check((sbx / ".claude" / "agents" / "shane-go-backend-dev.md").exists(),
          "agent file written into sandbox .claude/agents/")

    sbx7 = Path(tempfile.mkdtemp(prefix="agsbx7-"))
    staged7, _ = stage_roster(sbx7, roster_for(by_id(scns, "C7")), sources=(src,))
    check("oliver-shadcn-ui-builder" not in staged7 and "wigsy-code-reviewer" in staged7,
          "C7 (degrade): withheld agent (oliver) NOT staged; reviewers still staged")

    sbx2 = Path(tempfile.mkdtemp(prefix="agsbx2-"))
    staged2, _ = stage_roster(sbx2, roster_for(by_id(scns, "I2")), sources=(src,))
    check("oliver-shadcn-ui-builder" in staged2 and "shane-go-backend-dev" in staged2,
          "I2 (proceed, multi-agent): both shane + oliver staged")
    for p in (src, sbx, sbx7, sbx2):
        shutil.rmtree(p, ignore_errors=True)

    print("\n[12] capture injects plan.md for implement-plan live runs")
    from .drivers import SkillDriver

    class _PlanProbe(SkillDriver):
        seen = {}

        def run(self, scenario, sandbox, scripted=None):
            _PlanProbe.seen["plan_present"] = (sandbox.path / "plan.md").exists()
            return RunArtifacts(reported_status="PARTIAL")

    tmpij = Path(tempfile.mkdtemp(prefix="planinj-"))
    capture(by_id(scns, "I1"), _PlanProbe(), tmpij, stage=False)
    check(_PlanProbe.seen.get("plan_present") is True,
          "capture injects plan.md into the sandbox so the live skill can find it")
    check(not (tmpij / "I1" / "final_repo" / "plan.md").exists(),
          "injected plan.md is stripped from the captured final_repo")
    shutil.rmtree(tmpij, ignore_errors=True)

    print("\n" + "=" * 56)
    n_fail = sum(1 for ok, _ in _results if not ok)
    print(f"{len(_results) - n_fail}/{len(_results)} checks passed" + ("" if not n_fail else f"  ({n_fail} FAILED)"))
    return 1 if n_fail else 0


if __name__ == "__main__":
    sys.exit(main())
