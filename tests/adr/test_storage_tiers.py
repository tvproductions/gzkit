"""Storage tier verification for ADR-0.0.10.

Verifies that Tier A artifacts are git-tracked and Tier B rebuilds succeed.
Uses git ls-files and the live working tree to avoid expensive clone operations.

@covers REQ-0.0.10-04-01 REQ-0.0.10-04-02 REQ-0.0.10-04-03
"""

import subprocess
import unittest
from pathlib import Path


def _repo_root() -> Path:
    """Return the project root by walking up from this file."""
    current = Path(__file__).resolve().parent
    while current != current.parent:
        if (current / ".gzkit").is_dir():
            return current
        current = current.parent
    raise RuntimeError("Could not find project root (.gzkit directory)")


def _run(args: list[str], cwd: Path, *, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        cwd=cwd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=check,
    )


class TestGitCloneRecovery(unittest.TestCase):
    """Verify Tier A + B state is intact."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.root = _repo_root()
        result = _run(["git", "ls-files"], cwd=cls.root)
        cls.tracked = set(result.stdout.splitlines())

    def test_tier_a_artifacts_present_after_clone(self) -> None:
        """REQ-0.0.10-04-02: All Tier A artifacts are git-tracked."""
        tracked = self.tracked

        # Tier A: governance core
        self.assertIn(".gzkit/ledger.jsonl", tracked, "Tier A: ledger.jsonl not tracked")
        self.assertIn(".gzkit/manifest.json", tracked, "Tier A: manifest.json not tracked")
        self.assertIn(".gzkit.json", tracked, "Tier A: .gzkit.json not tracked")

        # Tier A: agent contracts
        self.assertIn("AGENTS.md", tracked, "Tier A: AGENTS.md not tracked")
        self.assertIn("CLAUDE.md", tracked, "Tier A: CLAUDE.md not tracked")

        # Tier A: project metadata
        self.assertIn("pyproject.toml", tracked, "Tier A: pyproject.toml not tracked")

        # Tier A: at least one ADR exists
        adr_files = [f for f in tracked if f.startswith("docs/design/adr/") and "ADR-" in f]
        self.assertGreater(len(adr_files), 0, "Tier A: no ADR markdown files tracked")

    def test_tier_b_rebuild_and_gz_state(self) -> None:
        """REQ-0.0.10-04-01/03: Tier B state resolves — gz state succeeds."""
        # Verify Tier B: control surface mirrors exist
        rules_dir = self.root / ".claude" / "rules"
        if rules_dir.exists():
            self.assertGreater(
                len(list(rules_dir.iterdir())),
                0,
                "Tier B: .claude/rules/ empty",
            )

        # gz state succeeds — all entities resolve from the live working tree
        result = _run(["uv", "run", "gz", "state"], cwd=self.root, check=False)
        self.assertEqual(
            result.returncode,
            0,
            f"gz state failed (exit {result.returncode}):\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}",
        )


if __name__ == "__main__":
    unittest.main()
