"""Scenario keys, run artifacts, and trial records.

Answer keys live as a fenced ```yaml block inside each fixture's answer-key.md. The core schema is
documented in ../SPEC.md; scenario-specific extras are carried verbatim in `.raw`.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

import yaml

_FENCE_RE = re.compile(r"```ya?ml\n(.*?)```", re.DOTALL)


def extract_yaml(md_text: str) -> dict:
    """Pull the first fenced ```yaml block out of a markdown doc."""
    m = _FENCE_RE.search(md_text)
    if not m:
        return {}
    return yaml.safe_load(m.group(1)) or {}


@dataclass
class ScenarioKey:
    scenario_id: str
    skill: str  # "create-plan" | "implement-plan"
    fixture_dir: Path  # dir containing answer-key.md
    repo_dir: Path  # dir to materialize into the sandbox
    raw: dict = field(default_factory=dict)

    # common
    agents_required: list = field(default_factory=list)
    agents_withheld: list = field(default_factory=list)
    expected_gate: str = "proceed"  # proceed | stop

    # create-plan
    mode_expected: str | None = None
    checkpoint_expected: str | None = None  # fires | skip | n/a
    input_path: Path | None = None
    scripted_answers_path: Path | None = None

    # implement-plan
    exec_mode_expected: str | None = None
    reviewers_expected: list = field(default_factory=list)
    test_cmd_expected: str | None = None
    status_expected: str | None = None
    iterations_expected: str | None = None
    seeded_tests: list = field(default_factory=list)
    acceptance_suite: object = None  # str | list[str] | None (relative to fixture_dir)

    plan_path: Path | None = None

    @property
    def expected_setup_cmd(self) -> str | None:
        return self.raw.get("expected_setup_cmd")

    def acceptance_files(self) -> list[Path]:
        """Absolute paths of held-out acceptance suites (empty if none)."""
        a = self.acceptance_suite
        if not a:
            return []
        names = a if isinstance(a, list) else [a]
        return [self.fixture_dir / n for n in names]

    def accepted_exec_modes(self) -> set[str]:
        """Parse exec_mode_expected, which may be 'A or B'."""
        if not self.exec_mode_expected:
            return set()
        return {p.strip().upper() for p in re.split(r"\bor\b|/|,", self.exec_mode_expected)}


def _key_from_block(scenario_id, skill, fixture_dir, repo_dir, raw, **over) -> ScenarioKey:
    k = ScenarioKey(
        scenario_id=scenario_id,
        skill=skill,
        fixture_dir=fixture_dir,
        repo_dir=repo_dir,
        raw=raw,
        agents_required=raw.get("agents_required", []) or [],
        agents_withheld=raw.get("agents_withheld", []) or [],
        expected_gate=raw.get("expected_gate", "proceed"),
        mode_expected=raw.get("mode_expected"),
        checkpoint_expected=raw.get("checkpoint_expected"),
        exec_mode_expected=raw.get("exec_mode_expected"),
        reviewers_expected=raw.get("reviewers_expected", []) or [],
        test_cmd_expected=raw.get("test_cmd_expected"),
        status_expected=raw.get("status_expected"),
        iterations_expected=str(raw.get("iterations_expected")) if raw.get("iterations_expected") is not None else None,
        seeded_tests=raw.get("seeded_tests", []) or [],
        acceptance_suite=raw.get("acceptance_suite"),
    )
    for kk, vv in over.items():
        setattr(k, kk, vv)
    return k


def load_scenarios(fixtures_root: Path) -> list[ScenarioKey]:
    """Discover every scenario under fixtures_root (one per answer-key.md).

    A key with a `variants:` list (I7) expands into one ScenarioKey per variant.
    """
    fixtures_root = Path(fixtures_root)
    out: list[ScenarioKey] = []
    for ak in sorted(fixtures_root.glob("**/answer-key.md")):
        fixture_dir = ak.parent
        # skill = the path segment right under fixtures/
        rel = fixture_dir.relative_to(fixtures_root).parts
        skill = rel[0]
        base_id = raw_id = (extract_yaml(ak.read_text()).get("scenario_id") or fixture_dir.name)
        raw = extract_yaml(ak.read_text())
        base_id = raw.get("scenario_id") or fixture_dir.name

        common = dict(
            input_path=(fixture_dir / "input.md") if (fixture_dir / "input.md").exists() else None,
            scripted_answers_path=(fixture_dir / "scripted-answers.json")
            if (fixture_dir / "scripted-answers.json").exists()
            else None,
            plan_path=(fixture_dir / "plan.md") if (fixture_dir / "plan.md").exists() else None,
        )

        variants = raw.get("variants")
        if variants:
            for v in variants:
                vdir = fixture_dir / v["dir"]
                out.append(
                    _key_from_block(
                        f"{base_id}/{Path(v['dir']).name}",
                        skill,
                        fixture_dir,
                        vdir,
                        raw,
                        test_cmd_expected=v.get("test_cmd_expected"),
                        exec_mode_expected=v.get("exec_mode_expected"),
                        **common,
                    )
                )
        else:
            out.append(
                _key_from_block(base_id, skill, fixture_dir, fixture_dir / "repo", raw, **common)
            )
    return out


@dataclass
class RunArtifacts:
    """What a SkillDriver must produce after driving the skill once."""

    transcript: str = ""
    output_tokens: int = 0
    wall_clock_s: float = 0.0

    # gate
    halted_with_setup_cmd: bool = False
    setup_cmd_text: str = ""

    # create-plan
    reported_mode: str | None = None
    plan_file: str | None = None  # path (relative to sandbox or absolute), or None
    plan_text: str = ""
    used_checkpoint: bool = False
    checkpoint_questions: list = field(default_factory=list)  # [{"options": [...], "single_decision": bool}]

    # implement-plan
    exec_mode: str | None = None
    reviewers_invoked: list = field(default_factory=list)
    test_cmd: str | None = None
    iterations: int = 0
    reported_status: str | None = None  # SUCCESS | PARTIAL | FAILED


@dataclass
class TrialRecord:
    scenario: str
    skill: str
    skill_version: str
    trial: int
    l1: dict = field(default_factory=dict)
    l2: dict = field(default_factory=dict)
    l3: dict = field(default_factory=dict)
    l1_pass: bool = False
    score: float = 0.0
    cost: dict = field(default_factory=dict)
    status_reported: str | None = None
    status_expected: str | None = None
    notes: list = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "scenario": self.scenario,
            "skill": self.skill,
            "skill_version": self.skill_version,
            "trial": self.trial,
            "l1": self.l1,
            "l1_pass": self.l1_pass,
            "l2": self.l2,
            "l3": self.l3,
            "score": round(self.score, 4),
            "cost": self.cost,
            "status_reported": self.status_reported,
            "status_expected": self.status_expected,
            "notes": self.notes,
        }
