"""Repo-content scanners read git's file list, never the raw filesystem (GHI #902).

Two pre-commit hooks scan the repository for a string: the validator-reachability
ratchet looks for ``gz validate --`` invocations to tier each scope, and the
pytest guard looks for ``import pytest``. Both walked ``root.rglob("*")`` and
discarded excluded directories only AFTER visiting them.

Measured 2026-08-28 against this repo: 367,088 paths walked against **7,241
tracked files**, and 324,827 of those were extensionless entries under the
gitignored ``.ruff_cache/``. The ratchet's suffix filter excludes only
``.pyc/.png/.jpg/.gz/.zip``, so it READ every one of them looking for a string a
ruff cache entry cannot contain. Per-commit cost of the two hooks: 54.0s of 59.0s.

The correctness half matters more than the speed. A ratchet that tiers a scope by
what mentions it must not count **gitignored derived artifacts** -- and it was:
``.gzkit/cache/``, candidate renditions, and ARB receipts under
``artifacts/receipts/`` supplied the only caller for several scopes. An ARB receipt
records a command that was RUN, so running a validator once left an artifact that
then made the scope look reachable forever. That is the instrument manufacturing
its own evidence, and the module's own ``_SELF_DIRS`` comment names the same hazard
for its own surfaces.
"""

from __future__ import annotations

import importlib.util
import subprocess
import tempfile
import unittest
from pathlib import Path
from types import ModuleType

from gzkit.commands.common import get_project_root
from gzkit.hooks import guards

_RATCHET = (
    get_project_root()
    / ".gzkit"
    / "chores"
    / "control-surface-validator-reachability"
    / "check_reachability.py"
)


def _load_ratchet() -> ModuleType:
    """Import the chore script by path; its directory name is not an identifier."""
    spec = importlib.util.spec_from_file_location("_reachability_walk", _RATCHET)
    if spec is None or spec.loader is None:
        raise unittest.SkipTest(f"cannot load {_RATCHET}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _git_repo(root: Path) -> None:
    """Initialize a repo quiet enough to run in a sandbox."""
    for args in (
        ["init", "--quiet"],
        ["config", "user.email", "t@example.invalid"],
        ["config", "user.name", "t"],
    ):
        subprocess.run(["git", *args], cwd=root, capture_output=True, check=True)


class RepoContentWalkTest(unittest.TestCase):
    """Both scanners must see tracked content and must not see ignored output."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory(prefix="gzkit-walk-")
        self.root = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)
        _git_repo(self.root)
        (self.root / ".gitignore").write_text(".ruff_cache/\ncache/\n", encoding="utf-8")
        (self.root / "kept.py").write_text("x = 1\n", encoding="utf-8")
        for rel in (".ruff_cache/0.15.20/entry", "cache/derived.py"):
            target = self.root / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text("import pytest  # gz validate --some-scope\n", encoding="utf-8")

    def test_ratchet_walk_excludes_gitignored_output(self) -> None:
        """A gitignored cache entry is not repo content and cannot tier a scope."""
        names = {p.name for p in _load_ratchet()._repo_files(self.root)}

        self.assertIn("kept.py", names, "tracked content must still be scanned")
        self.assertNotIn("entry", names, ".ruff_cache/ entry reached the caller scan")
        self.assertNotIn("derived.py", names, "gitignored derived file reached the caller scan")

    def test_guard_walk_excludes_gitignored_output(self) -> None:
        """The pytest guard must not flag a violation inside gitignored output."""
        names = {p.name for p in guards.iter_files(self.root)}

        self.assertIn("kept.py", names)
        self.assertNotIn("derived.py", names, "gitignored file reached the pytest guard")

    def test_untracked_but_unignored_file_is_still_scanned(self) -> None:
        """Not-yet-added work is repo content; a guard blind to it is useless.

        ``--others --exclude-standard`` is what buys this. Plain ``git ls-files``
        would return the index alone, so a newly written file carrying a
        violation would pass every gate until someone staged it -- the guard
        silently deferring to the one moment nobody re-reads.
        """
        (self.root / "brand_new.py").write_text("import pytest\n", encoding="utf-8")

        self.assertIn("brand_new.py", {p.name for p in guards.iter_files(self.root)})
        self.assertIn("brand_new.py", {p.name for p in _load_ratchet()._repo_files(self.root)})

    def test_walk_falls_back_outside_a_repository(self) -> None:
        """Degrade to slow, never to empty — a scanner reading nothing reads green."""
        with tempfile.TemporaryDirectory(prefix="gzkit-norepo-") as bare:
            root = Path(bare)
            (root / "loose.py").write_text("import pytest\n", encoding="utf-8")

            self.assertIn("loose.py", {p.name for p in guards.iter_files(root)})
            self.assertIn("loose.py", {p.name for p in _load_ratchet()._repo_files(root)})


if __name__ == "__main__":
    unittest.main()
