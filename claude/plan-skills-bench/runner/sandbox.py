"""Temp git sandbox: materialize a fixture repo, then assert on its post-run git state."""

from __future__ import annotations

import hashlib
import shutil
import subprocess
import tempfile
from pathlib import Path

_GIT_ID = ["-c", "user.email=eval@local", "-c", "user.name=eval-harness"]


class Sandbox:
    def __init__(self, path: Path, baseline_branch: str, baseline_tree: str):
        self.path = Path(path)
        self.baseline_branch = baseline_branch
        self.baseline_tree = baseline_tree
        self._seeded_baseline: dict[str, str] = {}

    # ---- construction ----------------------------------------------------
    @classmethod
    def materialize(cls, repo_dir: Path, seeded_tests: list[str] | None = None) -> "Sandbox":
        """Copy repo_dir into a fresh temp dir, git init + commit a baseline."""
        repo_dir = Path(repo_dir)
        tmp = Path(tempfile.mkdtemp(prefix="evalsbx-"))
        dst = tmp / "repo"
        shutil.copytree(repo_dir, dst)
        subprocess.run(["git", "-c", "init.defaultBranch=main", "init", "-q", str(dst)], check=True)
        sb = cls(dst, "main", "")
        sb.git("add", "-A")
        sb.git("commit", "-q", "-m", "baseline")
        sb.baseline_branch = sb.git("rev-parse", "--abbrev-ref", "HEAD").strip()
        sb.baseline_tree = sb.git("rev-parse", "HEAD^{tree}").strip()
        for rel in seeded_tests or []:
            p = sb.path / rel
            if p.exists():
                sb._seeded_baseline[rel] = _sha(p)
        return sb

    # ---- git plumbing ----------------------------------------------------
    def git(self, *args: str) -> str:
        r = subprocess.run(
            ["git", *_GIT_ID, "-C", str(self.path), *args],
            capture_output=True,
            text=True,
        )
        if r.returncode != 0 and args[:1] not in (("status",),):
            # status/porcelain etc. are read-only; only raise on mutating failures we care about
            if args[0] in ("add", "commit", "worktree", "branch", "checkout", "init"):
                raise RuntimeError(f"git {' '.join(args)} failed: {r.stderr.strip()}")
        return r.stdout

    # ---- state assertions ------------------------------------------------
    def is_dirty(self) -> bool:
        return bool(self.git("status", "--porcelain").strip())

    def current_branch(self) -> str:
        return self.git("rev-parse", "--abbrev-ref", "HEAD").strip()

    def current_tree(self) -> str:
        return self.git("rev-parse", "HEAD^{tree}").strip()

    def worktrees(self) -> list[str]:
        """All worktree paths registered for this repo."""
        out, paths = self.git("worktree", "list", "--porcelain"), []
        for line in out.splitlines():
            if line.startswith("worktree "):
                paths.append(line[len("worktree ") :])
        return paths

    def orphan_worktrees(self) -> list[str]:
        """Worktrees other than the main one (e.g. leftover impl-* trees)."""
        main = str(self.path.resolve())
        return [w for w in self.worktrees() if Path(w).resolve() != Path(main)]

    def branches(self) -> list[str]:
        return [b.strip() for b in self.git("branch", "--format=%(refname:short)").splitlines() if b.strip()]

    def temp_branches(self) -> list[str]:
        """Branches other than the baseline (work-item / *-merged-batch* / impl-* leftovers)."""
        return [b for b in self.branches() if b != self.baseline_branch]

    def tampered_seeded_tests(self) -> list[str]:
        """Seeded test files whose content changed vs the baseline hash."""
        bad = []
        for rel, h in self._seeded_baseline.items():
            p = self.path / rel
            if (not p.exists()) or _sha(p) != h:
                bad.append(rel)
        return bad

    def is_pristine(self) -> bool:
        """No changes at all (for STOP-gate scenarios that must not touch the repo)."""
        return (
            not self.is_dirty()
            and not self.orphan_worktrees()
            and not self.temp_branches()
            and self.current_tree() == self.baseline_tree
        )

    def diff(self) -> str:
        """Full diff of the post-run working tree vs baseline, including new files.

        Stages everything into the index first so untracked files appear. Call AFTER the
        clean_state gate (which relies on the unstaged porcelain status).
        """
        self.git("add", "-A")
        return self.git("diff", "--cached", "HEAD")

    def cleanup(self) -> None:
        # remove the temp root (parent of repo)
        shutil.rmtree(self.path.parent, ignore_errors=True)


def _sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()
