"""Run acceptance suites against a post-run sandbox.

Production uses pytest. When pytest is unavailable we fall back to a dependency-free runner that
imports the test module and calls its ``test_*`` functions — sufficient for every held-out suite in
this fixture set (all use plain ``assert``, no parametrize). Anything that needs pytest and can't
import is reported as "not green", which is the correct conservative outcome.
"""

from __future__ import annotations

import importlib.util
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass
class SuiteResult:
    passed: bool
    detail: str


def _have_pytest() -> bool:
    return importlib.util.find_spec("pytest") is not None


def run_acceptance(sandbox_path: Path, suite_files: list[Path]) -> SuiteResult:
    """Copy each held-out suite into the sandbox and run it. Green iff every suite passes."""
    if not suite_files:
        return SuiteResult(True, "no acceptance suite")
    sandbox_path = Path(sandbox_path)
    copied = []
    for src in suite_files:
        dst = sandbox_path / Path(src).name
        shutil.copyfile(src, dst)
        copied.append(dst)
    try:
        if _have_pytest():
            return _run_pytest(sandbox_path, copied)
        return _run_fallback(sandbox_path, copied)
    finally:
        for c in copied:
            c.unlink(missing_ok=True)


def _run_pytest(sandbox_path: Path, files: list[Path]) -> SuiteResult:
    r = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", *[str(f) for f in files]],
        cwd=str(sandbox_path),
        capture_output=True,
        text=True,
        env={"PYTHONPATH": str(sandbox_path), "PATH": _path()},
        timeout=600,
    )
    return SuiteResult(r.returncode == 0, (r.stdout + r.stderr).strip()[-2000:])


def _run_fallback(sandbox_path: Path, files: list[Path]) -> SuiteResult:
    """Import each suite (with the sandbox on sys.path) and run its test_* functions."""
    sp = str(sandbox_path)
    added = sp not in sys.path
    if added:
        sys.path.insert(0, sp)
    before = set(sys.modules)  # so we can purge everything imported during this call
    failures = []
    try:
        for f in files:
            modname = f"_acc_{f.stem}"
            spec = importlib.util.spec_from_file_location(modname, f)
            try:
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)  # import errors (e.g. missing pytest) land here
            except Exception as e:  # noqa: BLE001
                failures.append(f"{f.name}: import error: {e!r}")
                continue
            for name in dir(mod):
                if name.startswith("test"):
                    fn = getattr(mod, name)
                    if callable(fn):
                        try:
                            fn()
                        except Exception as e:  # noqa: BLE001
                            failures.append(f"{f.name}::{name}: {e!r}")
    finally:
        # Purge the test module AND any solution modules (pricing, report, ...) imported here,
        # so a later run with a different/broken solution is not masked by a cached import.
        for m in set(sys.modules) - before:
            sys.modules.pop(m, None)
        if added and sp in sys.path:
            sys.path.remove(sp)
    return SuiteResult(not failures, "; ".join(failures) if failures else "ok (fallback runner)")


def _path() -> str:
    import os

    return os.environ.get("PATH", "")
