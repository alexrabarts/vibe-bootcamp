"""L3 judge dispatch: render the prompts in ../judges/ against a model and aggregate scores.

Mirrors the driver pattern: a JudgeClient interface, a MockJudgeClient for self-testing, and an
AnthropicJudgeClient stub for live use. Per SPEC, run N judges per dimension; take the median score
and majority `matches_answer_key`. Scores are normalized to 0..1 before they enter TrialRecord.l3
(which always holds 0..1, alongside the deterministic acceptance_pass).
"""

from __future__ import annotations

import json
import re
import statistics
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path

from .contracts import RunArtifacts, ScenarioKey

_JUDGE_DIR = Path(__file__).resolve().parent.parent / "judges"

# Which L3 dimensions apply, by create-plan mode. acceptance_pass / convergence_efficiency are
# deterministic (computed in checks.py), so they are NOT judged here.
_CREATE_DIMS = {
    "DEBUGGING": ["distinctness", "evidence_grounding", "correct_primary", "checkpoint_leverage", "actionability", "coupled_site_coverage", "load_bearing_coverage", "proof_adequacy", "premise_verification"],
    "FEATURE": ["distinctness", "evidence_grounding", "correct_primary", "checkpoint_leverage", "actionability", "coupled_site_coverage", "load_bearing_coverage", "proof_adequacy", "premise_verification"],
    "REFACTOR": ["distinctness", "evidence_grounding", "correct_primary", "checkpoint_leverage", "actionability", "coupled_site_coverage", "load_bearing_coverage", "proof_adequacy", "premise_verification"],
    # INVESTIGATION plans propose no change, so they carry no success criteria to prove — and they
    # select no hypothesis and design no fix, so there is no ranking for a discriminating premise to
    # reorder and nothing that collapses if a belief is false. What an investigation asserts about the
    # current system is already graded by `evidence_grounding` against `ground_truth_flow`; judging
    # `premise_verification` here would score the same claims twice under a second name.
    "INVESTIGATION": ["evidence_grounding", "actionability"],
}


# ---------------------------------------------------------------------------
# template parsing + rendering
# ---------------------------------------------------------------------------
@dataclass
class Template:
    preamble: str
    dims: dict  # dimension -> prompt body


_PREAMBLE_RE = re.compile(r"Shared preamble.*?```\n(.*?)```", re.DOTALL)
_DIM_RE = re.compile(r"^##\s+([a-z_]+)\s*\n+```\n(.*?)```", re.DOTALL | re.MULTILINE)


def load_template(skill: str) -> Template:
    path = _JUDGE_DIR / f"{skill}-quality.md"
    text = path.read_text()
    pre = _PREAMBLE_RE.search(text)
    preamble = pre.group(1).strip() if pre else ""
    dims = {name: body.strip() for name, body in _DIM_RE.findall(text)}
    return Template(preamble=preamble, dims=dims)


def render(template: Template, dimension: str, context: dict) -> str:
    body = f"{template.preamble}\n\n{template.dims[dimension]}"
    # explicit replacement (not str.format) so stray braces in prompts never crash rendering
    for key, val in context.items():
        body = body.replace("{" + key + "}", str(val))
    return body


# ---------------------------------------------------------------------------
# judge clients
# ---------------------------------------------------------------------------
class JudgeClient(ABC):
    @abstractmethod
    def judge(self, dimension: str, prompt: str) -> dict:
        """Return an object matching ../judges/schema.json (dimension, score 1-5, verdict,
        evidence, refutation_attempt, matches_answer_key)."""


def validate_judgment(obj: dict, dimension: str) -> dict:
    score = int(round(float(obj.get("score", 3))))
    score = max(1, min(5, score))
    return {
        "dimension": obj.get("dimension", dimension),
        "score": score,
        "verdict": obj.get("verdict", ""),
        "evidence": obj.get("evidence", []),
        "refutation_attempt": obj.get("refutation_attempt", ""),
        "matches_answer_key": obj.get("matches_answer_key"),
    }


class MockJudgeClient(JudgeClient):
    """Deterministic judge for self-testing. score_map/match_map keyed by dimension."""

    def __init__(self, score_map: dict | None = None, match_map: dict | None = None, default_score: int = 4):
        self.score_map = score_map or {}
        self.match_map = match_map or {}
        self.default_score = default_score

    def judge(self, dimension: str, prompt: str) -> dict:
        return validate_judgment(
            {
                "dimension": dimension,
                "score": self.score_map.get(dimension, self.default_score),
                "verdict": "mock",
                "evidence": [],
                "refutation_attempt": "mock: none",
                "matches_answer_key": self.match_map.get(dimension),
            },
            dimension,
        )


class AnthropicJudgeClient(JudgeClient):
    """Live judge. Requires the `anthropic` SDK + ANTHROPIC_API_KEY. Forces the schema via tool use.

    Not exercised by the selftest. Use a different model than the skill under test (SPEC).
    """

    def __init__(self, model: str = "claude-sonnet-4-6", max_tokens: int = 1024):
        self.model = model
        self.max_tokens = max_tokens
        self._schema = json.loads((_JUDGE_DIR / "schema.json").read_text())

    def judge(self, dimension: str, prompt: str) -> dict:
        import anthropic  # imported lazily so the harness has no hard dependency

        client = anthropic.Anthropic()
        tool = {
            "name": "record_judgment",
            "description": "Record the structured judgment.",
            "input_schema": self._schema,
        }
        resp = client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            tools=[tool],
            tool_choice={"type": "tool", "name": "record_judgment"},
            messages=[{"role": "user", "content": prompt}],
        )
        for block in resp.content:
            if getattr(block, "type", None) == "tool_use":
                return validate_judgment(block.input, dimension)
        raise RuntimeError("judge did not return a tool_use block")


# ---------------------------------------------------------------------------
# aggregation + dispatch
# ---------------------------------------------------------------------------
def aggregate_judgments(results: list[dict]) -> dict:
    """Median score + majority matches_answer_key across N judges (SPEC)."""
    scores = [r["score"] for r in results]
    med = statistics.median(scores)
    matches = [r["matches_answer_key"] for r in results if r.get("matches_answer_key") is not None]
    majority = (sum(1 for m in matches if m) * 2 > len(matches)) if matches else None
    return {
        "score": med,
        "score_norm": round((med - 1) / 4, 4),  # 1..5 -> 0..1
        "matches_answer_key": majority,
        "n": len(results),
        "refutations": [r.get("refutation_attempt", "") for r in results],
    }


def judge_dimension(client: JudgeClient, dimension: str, prompt: str, n_judges: int = 3) -> dict:
    return aggregate_judgments([client.judge(dimension, prompt) for _ in range(n_judges)])


_PREMISES_SECTION_RE = re.compile(r"^##\s+Premises\s*$", re.MULTILINE)


def _plan_has_premises(scenario: ScenarioKey) -> bool:
    """Does the plan handed to this run carry a `## Premises` section to re-check? This is the skill's
    own trigger condition, so it is the honest gate for `premises_rechecked`."""
    if not scenario.plan_path or not scenario.plan_path.exists():
        return False
    return bool(_PREMISES_SECTION_RE.search(scenario.plan_path.read_text()))


def dimensions_for(scenario: ScenarioKey, artifacts: RunArtifacts) -> list[str]:
    """Which L3 dimensions to judge for this scenario (deterministic ones excluded)."""
    if scenario.expected_gate == "stop":
        return []
    if scenario.skill == "create-plan":
        mode = (scenario.mode_expected or "").upper()
        dims = list(_CREATE_DIMS.get(mode, _CREATE_DIMS["FEATURE"]))
        if not scenario.raw.get("true_primary"):
            dims = [d for d in dims if d != "correct_primary"]
        if "checkpoint_leverage" in dims and not (artifacts.used_checkpoint or scenario.checkpoint_expected == "fires"):
            dims = [d for d in dims if d != "checkpoint_leverage"]
        return dims
    # implement-plan. proof_discharged is unconditional: every run claims its criteria are met, so
    # every run owes proof. A run that reports none scores it 1 — that is the measurement, not a gap.
    dims = ["criteria_met", "proof_discharged"]
    # premises_rechecked is NOT unconditional, and the asymmetry with proof is deliberate. Proof is
    # owed by every run because every run makes claims. A premise re-check is owed only where the plan
    # carries premises: with no `## Premises` section the correct behavior is a clean skip — inventing
    # premises from a finished plan would ratify it rather than test it — so judging every scenario
    # would score a correct no-op as if it were a discipline, or punish it as if it were a lapse.
    if _plan_has_premises(scenario) or scenario.raw.get("premise_expectations"):
        dims.append("premises_rechecked")
    if scenario.raw.get("cruft_to_find"):
        dims.append("cruft_flagged")
    if scenario.raw.get("coupled_sites"):
        dims.append("drift_caught")
    return dims


def build_context(scenario: ScenarioKey, artifacts: RunArtifacts, sandbox, test_results: str = "") -> dict:
    answer_key = (scenario.fixture_dir / "answer-key.md").read_text()
    if scenario.skill == "create-plan":
        plan = artifacts.plan_text or ""
        questions = "\n".join(
            f"- options: {q.get('options')}" for q in (artifacts.checkpoint_questions or [])
        ) or "(no questions asked)"
        return {"answer_key": answer_key, "plan": plan, "questions_asked": questions}
    plan = scenario.plan_path.read_text() if scenario.plan_path else ""
    diff = sandbox.diff() if sandbox else ""
    return {
        "answer_key": answer_key,
        "plan": plan,
        "diff": diff,
        "test_results": test_results or "(not provided)",
        "reported_status": artifacts.reported_status or "(none)",
        "proof_report": _proof_report(artifacts),
        "premise_report": _premise_report(artifacts),
    }


def _proof_report(artifacts: RunArtifacts) -> str:
    """What the run offered as proof. Falls back to the transcript when the driver did not isolate a
    proof section (older bundles, best-effort parsers) so the judge grades what was actually said —
    and to an explicit "none" when the run offered nothing, which is itself the finding."""
    if artifacts.proof_report:
        return artifacts.proof_report
    if artifacts.transcript:
        return (
            "(no proof section was isolated from this run; the full transcript follows — if it "
            "contains no obligations, methods, or raw evidence, the run reported no proof)\n"
            f"{artifacts.transcript}"
        )
    return "(the run reported no proof: no obligations, no methods, no evidence)"


def _premise_report(artifacts: RunArtifacts) -> str:
    """What the run offered as its re-check of the plan's premises. The dimension only fires when the
    plan HAS premises, so inside that gate an empty report is not ambiguous: the run implemented
    without re-checking what the plan rests on. Say that plainly rather than handing the judge a
    silence it might read as a clean skip."""
    if artifacts.premise_report:
        return artifacts.premise_report
    if artifacts.transcript:
        return (
            "(no premise re-check was isolated from this run; the full transcript follows — if it "
            "contains no premise methods, evidence, or verdicts, the run implemented without "
            "re-checking the premises the plan rests on)\n"
            f"{artifacts.transcript}"
        )
    return "(the run reported no premise re-check: no methods, no evidence, no verdicts)"


def judge_trial(
    scenario: ScenarioKey,
    artifacts: RunArtifacts,
    sandbox,
    client: JudgeClient,
    n_judges: int = 3,
    test_results: str = "",
) -> dict:
    """Run all applicable L3 dimensions. Returns dim -> aggregated judgment (incl. score_norm)."""
    dims = dimensions_for(scenario, artifacts)
    if not dims:
        return {}
    template = load_template(scenario.skill)
    context = build_context(scenario, artifacts, sandbox, test_results)
    out = {}
    for dim in dims:
        if dim not in template.dims:
            continue
        prompt = render(template, dim, context)
        out[dim] = judge_dimension(client, dim, prompt, n_judges)
    return out
