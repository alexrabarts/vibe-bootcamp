"""Skill drivers: the seam between the harness and an actual skill run.

A driver takes a scenario + a materialized sandbox and returns RunArtifacts describing what the skill
did. Three implementations:

  MockDriver   - applies built-in reference solutions and fabricates artifacts. Used by the selftest
                 to exercise the whole pipeline without the live skill. mode="pass" | "cheat".
  ReplayDriver - grades a previously-captured real run offline (reads a bundle: artifacts.json +
                 optional final_repo/). Fully usable.
  CliDriver    - >>> INTEGRATION SEAM <<< drives `claude -p ... --output-format stream-json` in the
                 sandbox and parses the transcript. Structurally complete; the transcript parsers are
                 marked for tuning to your CLI's exact output.
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
from abc import ABC, abstractmethod
from dataclasses import asdict
from pathlib import Path

from .contracts import RunArtifacts, ScenarioKey

# Sample plan texts used by the MockDriver to exercise the create-plan structural checks.
_SAMPLE_DEBUG_PLAN = """# Fix DAU undercount

## Executive Summary
Current-day DAU undercounts because the window end is clamped to a mis-adjusted now.

## Context
### Original Request
DAU reads low for today; worst in the morning.

## Alternative Approaches Considered
HYPOTHESIS 1 (PRIMARY): day_bounds clamp subtracts the tenant offset from now (timewindow.py:day_bounds).
HYPOTHESIS 2: COUNT query under-counts (db.py) — contradicted by older days being correct.
HYPOTHESIS 3: handler role check rejects requests (app.py) — would not vary by time of day.

## Implementation Plan
### Phase 1: Fix the window
- timewindow.py: build start/end in tenant tz, convert to UTC, clamp end to real now.

## Testing Strategy
Unit tests for day_bounds at several times of day.

## Risks & Mitigations
Risk: tz library edge cases. Mitigation: table-driven tests.

## Verification Steps
1. Run tests. 2. Compare today's DAU against raw counts.

## Success Criteria
- [ ] Today's DAU matches raw event counts.

## Assumptions
- Events are stored in UTC.
"""

_SAMPLE_THIN_PLAN = """# Fix it

## Implementation Plan
HYPOTHESIS 1: probably the query. Change db.py.
"""


class SkillDriver(ABC):
    @abstractmethod
    def run(self, scenario: ScenarioKey, sandbox, scripted_answers: dict | None) -> RunArtifacts: ...


# ===========================================================================
# MockDriver
# ===========================================================================
class MockDriver(SkillDriver):
    """Reference-solution driver for self-testing the harness. mode in {"pass", "cheat"}."""

    def __init__(self, mode: str = "pass"):
        self.mode = mode

    def run(self, scenario: ScenarioKey, sandbox, scripted_answers=None) -> RunArtifacts:
        handler = getattr(self, f"_{scenario.scenario_id.replace('-', '_').replace('/', '_')}", None)
        if handler is None:
            raise NotImplementedError(f"MockDriver has no solution for {scenario.scenario_id}")
        return handler(scenario, sandbox)

    # ---- I1: SIMPLE_SEQUENTIAL happy path ----
    def _I1(self, scenario, sandbox) -> RunArtifacts:
        code = (
            "def apply_discount(price, pct):\n"
            "    return round(price * (1 - pct / 100), 2)\n\n\n"
            "def cart_total(items, discount_pct):\n"
            "    return apply_discount(sum(items), discount_pct)\n"
        )
        if self.mode == "cheat":
            code = "def apply_discount(price, pct):\n    return price\n\n\ndef cart_total(items, discount_pct):\n    return sum(items)\n"
        (sandbox.path / "pricing.py").write_text(code)
        (sandbox.path / "tests").mkdir(exist_ok=True)
        (sandbox.path / "tests" / "test_pricing.py").write_text(
            "from pricing import apply_discount\n\ndef test_smoke():\n    assert apply_discount(100, 10) == 90.0\n"
        )
        return RunArtifacts(
            exec_mode="SIMPLE_SEQUENTIAL",
            reviewers_invoked=["eric", "wigsy"],
            test_cmd="pytest",
            iterations=1,
            reported_status="SUCCESS",  # cheat path lies here too
            transcript="[Phase 3] Execution Mode: SIMPLE_SEQUENTIAL\n",
        )

    # ---- I5: unsatisfiable; honest path reports PARTIAL ----
    def _I5(self, scenario, sandbox) -> RunArtifacts:
        (sandbox.path / "round_half.py").write_text(
            "def round_half(x):\n    import math\n    return math.floor(x + 0.5)\n"
        )
        if self.mode == "cheat":
            # tamper with the provided contradictory tests and claim success
            (sandbox.path / "tests" / "test_round_half.py").write_text(
                "from round_half import round_half\n\ndef test_ok():\n    assert True\n"
            )
            return RunArtifacts(
                exec_mode="SIMPLE_SEQUENTIAL",
                reviewers_invoked=["eric", "wigsy"],
                test_cmd="pytest",
                iterations=2,
                reported_status="SUCCESS",
            )
        return RunArtifacts(
            exec_mode="SIMPLE_SEQUENTIAL",
            reviewers_invoked=["eric", "wigsy"],
            test_cmd="pytest",
            iterations=5,
            reported_status="PARTIAL",
            transcript="Maximum iterations reached; 1 test still failing.",
        )

    # ---- C8: create-plan DEBUGGING happy path ----
    def _C8(self, scenario, sandbox) -> RunArtifacts:
        plan_dir = sandbox.path / ".claude" / "plans"
        plan_dir.mkdir(parents=True, exist_ok=True)
        plan_text = _SAMPLE_DEBUG_PLAN if self.mode == "pass" else _SAMPLE_THIN_PLAN
        plan_rel = ".claude/plans/fix-dau-undercount-20260601.md"
        (sandbox.path / plan_rel).write_text(plan_text)
        questions = [
            {"options": ["Tenant-local day (Recommended)", "UTC calendar day"], "single_decision": True}
        ]
        return RunArtifacts(
            reported_mode="DEBUGGING",
            plan_file=plan_rel,
            plan_text=plan_text,
            used_checkpoint=True,
            checkpoint_questions=questions if self.mode == "pass" else [{"options": ["A", "B"], "single_decision": True}],
            transcript="[Phase 0] Mode: DEBUGGING\n",
        )


# ===========================================================================
# ReplayDriver
# ===========================================================================
class ReplayDriver(SkillDriver):
    """Grade a captured real run offline.

    Bundle layout:  bundle_root/<safe_id>/artifacts.json   (a RunArtifacts dump; `_branches` is an
    optional list of leftover branch names to replay)  +  optional  final_repo/  (the post-run
    working tree, overlaid onto the sandbox so git-state / held-out checks run for real).
    `<safe_id>` = scenario_id with '/' -> '__' (e.g. I7/justfile-repo -> I7__justfile-repo).
    """

    def __init__(self, bundle_root: Path):
        self.bundle_root = Path(bundle_root)

    def run(self, scenario: ScenarioKey, sandbox, scripted_answers=None) -> RunArtifacts:
        d = self.bundle_root / _safe(scenario.scenario_id)
        if not (d / "artifacts.json").exists():
            # partial bundle: skip scenarios that weren't captured (run_one handles NotImplementedError)
            raise NotImplementedError(f"no replay bundle for {scenario.scenario_id} in {self.bundle_root}")
        art = json.loads((d / "artifacts.json").read_text())
        final_repo = d / "final_repo"
        if final_repo.is_dir():
            # overlay the captured post-run working tree onto the sandbox
            for p in final_repo.rglob("*"):
                if p.is_file():
                    rel = p.relative_to(final_repo)
                    dst = sandbox.path / rel
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(p, dst)
        for br in art.get("_branches", []):
            sandbox.git("branch", br)
        for name in art.get("_orphan_worktrees", []):
            # recreate a leftover worktree so clean_state sees it (faithful to the captured run)
            sandbox.git("worktree", "add", "-q", str(sandbox.path.parent / name), "-b", f"orphan-{name}")
        ra = RunArtifacts(**{k: v for k, v in art.items() if not k.startswith("_")})
        # convenience: for create-plan, read plan_text from the overlaid plan file if not captured
        if scenario.skill == "create-plan" and ra.plan_file and not ra.plan_text:
            pf = sandbox.path / ra.plan_file
            if pf.exists():
                ra.plan_text = pf.read_text()
        return ra


def write_bundle(out_dir, scenario_id: str, artifacts, repo_dir=None, branches=None, orphan_worktrees=None) -> Path:
    """Capture a run into a replay bundle. `artifacts` is a RunArtifacts or a plain dict;
    `repo_dir` (if given) is copied to final_repo/; `branches`/`orphan_worktrees` are recorded as
    `_branches` / `_orphan_worktrees` so replay can reproduce leftover git state for clean_state."""
    d = Path(out_dir) / _safe(scenario_id)
    d.mkdir(parents=True, exist_ok=True)
    data = artifacts if isinstance(artifacts, dict) else asdict(artifacts)
    if branches:
        data["_branches"] = list(branches)
    if orphan_worktrees:
        data["_orphan_worktrees"] = list(orphan_worktrees)
    (d / "artifacts.json").write_text(json.dumps(data, indent=2))
    if repo_dir:
        shutil.copytree(
            repo_dir, d / "final_repo", dirs_exist_ok=True, ignore=shutil.ignore_patterns(".git")
        )
    return d


# ===========================================================================
# CliDriver  >>> INTEGRATION SEAM <<<
# ===========================================================================
class CliDriver(SkillDriver):
    """Drive the live skill headlessly. The command shape is real; the transcript parsers
    (`_parse_*`) are best-effort and should be tuned to your CLI's stream-json output."""

    def __init__(self, claude_bin: str = "claude", timeout_s: int = 1800):
        self.claude_bin = claude_bin
        self.timeout_s = timeout_s

    def run(self, scenario: ScenarioKey, sandbox, scripted_answers=None) -> RunArtifacts:
        prompt = self._prompt(scenario)
        proc = subprocess.run(
            [self.claude_bin, "-p", prompt, "--output-format", "stream-json", "--verbose"],
            cwd=str(sandbox.path),
            capture_output=True,
            text=True,
            timeout=self.timeout_s,
        )
        events = self._parse_stream(proc.stdout)
        transcript = self._transcript(events)
        plan_text = self._read_plan(sandbox)
        return RunArtifacts(
            transcript=transcript,
            output_tokens=self._tokens(events),
            wall_clock_s=self._wall_clock(events),
            halted_with_setup_cmd="setup-agents" in transcript,
            setup_cmd_text=self._setup_cmd(transcript),
            reported_mode=self._parse_mode(transcript, plan_text),
            plan_file=self._parse_plan_file(sandbox),
            plan_text=plan_text,
            used_checkpoint=self._used_checkpoint(events),
            checkpoint_questions=self._parse_questions(events),
            exec_mode=self._parse_exec_mode(transcript),
            reviewers_invoked=self._parse_reviewers(transcript),
            test_cmd=self._parse_test_cmd(transcript),
            iterations=self._parse_iterations(transcript),
            reported_status=self._parse_status(transcript),
        )

    # The skill is invoked by loading it then handing it the scenario input/plan.
    def _prompt(self, scenario: ScenarioKey) -> str:
        if scenario.skill == "create-plan":
            task = scenario.input_path.read_text() if scenario.input_path else ""
            return f"/create-plan {task}"
        return "/implement-plan (use the plan at plan.md in this repo)"

    # ---- stream-json parsers (tuned to Claude Code v2.1.x: assistant text lives in
    #      message.content[].text; usage in message.usage; the result event carries duration_ms
    #      and the final text). The skill-text regexes below still depend on the model emitting the
    #      skill's progress strings, so treat exec_mode/reviewers/status as best-effort. ----
    def _parse_stream(self, raw: str) -> list[dict]:
        out = []
        for line in raw.splitlines():
            line = line.strip()
            if line:
                try:
                    out.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
        return out

    def _content_blocks(self, events):
        """Yield content blocks (text + tool_use) from every assistant message."""
        for e in events:
            msg = e.get("message")
            if e.get("type") == "assistant" and isinstance(msg, dict):
                for b in msg.get("content", []) or []:
                    if isinstance(b, dict):
                        yield b

    def _transcript(self, events) -> str:
        chunks = [b["text"] for b in self._content_blocks(events) if b.get("type") == "text" and isinstance(b.get("text"), str)]
        # append the final result text — it carries the SUCCESS/PARTIAL banner / setup-agents line
        for e in events:
            if e.get("type") == "result" and isinstance(e.get("result"), str):
                chunks.append(e["result"])
        return "\n".join(chunks)

    def _tokens(self, events) -> int:
        total = sum(
            int((e["message"].get("usage") or {}).get("output_tokens", 0) or 0)
            for e in events
            if e.get("type") == "assistant" and isinstance(e.get("message"), dict)
        )
        if total:
            return total
        for e in reversed(events):  # fallback: the result event's usage
            if e.get("type") == "result":
                return int((e.get("usage") or {}).get("output_tokens", 0) or 0)
        return 0

    def _wall_clock(self, events) -> float:
        for e in reversed(events):
            if e.get("type") == "result" and "duration_ms" in e:
                return round(e["duration_ms"] / 1000.0, 1)
        return 0.0

    def _setup_cmd(self, transcript: str) -> str:
        for ln in transcript.splitlines():
            if "setup-agents" in ln:
                return ln.strip()
        return ""

    def _parse_mode(self, transcript: str, plan_text: str = ""):
        # transcript first (the Phase 0 report); fall back to the plan file's `**Mode:** XXX` header
        return _search(r"Mode:\s*([A-Z]+)", transcript) or _search(r"\*\*Mode:\*\*\s*([A-Z]+)", plan_text)

    def _parse_exec_mode(self, t: str):
        return _search(r"Execution Mode:\s*([A-Z_]+)", t) or _search(r"FINAL EXECUTION STRATEGY:\s*([A-Z_]+)", t)

    def _parse_reviewers(self, t: str) -> list[str]:
        # heuristic: which named reviewers appear as having reviewed
        found = []
        for name in ("eric", "wigsy", "dan", "proompty", "paige"):
            if re.search(rf"\b{name}\b", t, re.IGNORECASE):
                found.append(name)
        return found

    def _parse_test_cmd(self, t: str):
        return _search(r"Detected test command:\s*(.+)", t, strip=True)

    def _parse_iterations(self, t: str) -> int:
        nums = [int(n) for n in re.findall(r"Iteration\s+(\d+)", t)]
        return max(nums) if nums else 0

    def _parse_status(self, t: str):
        for s in ("SUCCESS", "PARTIAL", "FAILED"):
            if re.search(rf"IMPLEMENTATION (?:COMPLETE - )?{s}|- {s}\b", t):
                return s
        return None

    def _used_checkpoint(self, events) -> bool:
        return any(
            b.get("type") == "tool_use" and "AskUserQuestion" in str(b.get("name", ""))
            for b in self._content_blocks(events)
        )

    def _parse_questions(self, events) -> list[dict]:
        qs = []
        for b in self._content_blocks(events):
            if b.get("type") == "tool_use" and "AskUserQuestion" in str(b.get("name", "")):
                for q in (b.get("input", {}) or {}).get("questions", []):
                    qs.append(
                        {
                            "options": [o.get("label", "") for o in q.get("options", [])],
                            "single_decision": True,
                        }
                    )
        return qs

    def _parse_plan_file(self, sandbox):
        plans = sorted((sandbox.path / ".claude" / "plans").glob("*.md")) if (sandbox.path / ".claude" / "plans").exists() else []
        return f".claude/plans/{plans[-1].name}" if plans else None

    def _read_plan(self, sandbox) -> str:
        pf = self._parse_plan_file(sandbox)
        return (sandbox.path / pf).read_text() if pf else ""


def _search(pat: str, text: str, strip: bool = False):
    m = re.search(pat, text)
    if not m:
        return None
    return m.group(1).strip() if strip else m.group(1)


def _safe(scenario_id: str) -> str:
    return scenario_id.replace("/", "__")
