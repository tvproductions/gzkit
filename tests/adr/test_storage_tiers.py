"""Git clone recovery test for ADR-0.0.10 storage tiers.

Verifies that all Tier A + Tier B state survives a git clone from scratch.
Uses a local bare repo to avoid network access.

@covers REQ-0.0.10-04-01 REQ-0.0.10-04-02 REQ-0.0.10-04-03
"""

import subprocess
import tempfile
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
    """Verify Tier A + B state survives git clone from scratch."""

    def test_tier_a_artifacts_present_after_clone(self) -> None:
        """REQ-0.0.10-04-02: All Tier A artifacts present after clone."""
        root = _repo_root()
        with tempfile.TemporaryDirectory() as tmpdir:
            bare = Path(tmpdir) / "bare.git"
            clone = Path(tmpdir) / "clone"

            # Create local bare repo — no network access
            _run(["git", "clone", "--bare", str(root), str(bare)], cwd=Path(tmpdir))

            # Clone from bare into fresh directory
            _run(["git", "clone", str(bare), str(clone)], cwd=Path(tmpdir))

            # Tier A: governance core
            self.assertTrue(
                (clone / ".gzkit" / "ledger.jsonl").exists(),
                "Tier A: ledger.jsonl missing after clone",
            )
            self.assertTrue(
                (clone / ".gzkit" / "manifest.json").exists(),
                "Tier A: manifest.json missing after clone",
            )
            self.assertTrue(
                (clone / ".gzkit.json").exists(),
                "Tier A: .gzkit.json config missing after clone",
            )

            # Tier A: agent contracts
            self.assertTrue(
                (clone / "AGENTS.md").exists(),
                "Tier A: AGENTS.md missing after clone",
            )
            self.assertTrue(
                (clone / "CLAUDE.md").exists(),
                "Tier A: CLAUDE.md missing after clone",
            )

            # Tier A: project metadata
            self.assertTrue(
                (clone / "pyproject.toml").exists(),
                "Tier A: pyproject.toml missing after clone",
            )

            # Tier A: at least one ADR exists
            adr_files = list((clone / "docs" / "design" / "adr").rglob("ADR-*.md"))
            self.assertGreater(len(adr_files), 0, "Tier A: no ADR markdown files found after clone")

    def test_tier_b_rebuild_and_gz_state(self) -> None:
        """REQ-0.0.10-04-01/03: Clone, rebuild Tier B, gz state succeeds."""
        root = _repo_root()
        with tempfile.TemporaryDirectory() as tmpdir:
            bare = Path(tmpdir) / "bare.git"
            clone = Path(tmpdir) / "clone"

            _run(["git", "clone", "--bare", str(root), str(bare)], cwd=Path(tmpdir))
            _run(["git", "clone", str(bare), str(clone)], cwd=Path(tmpdir))

            # Rebuild Tier B: hydrate environment
            _run(["uv", "sync"], cwd=clone)

            # Rebuild Tier B: regenerate control surface mirrors
            _run(
                ["uv", "run", "gz", "agent", "sync", "control-surfaces"],
                cwd=clone,
            )

            # Tier B rebuilt: .claude/rules/ should have content
            rules_dir = clone / ".claude" / "rules"
            if rules_dir.exists():
                self.assertGreater(
                    len(list(rules_dir.iterdir())),
                    0,
                    "Tier B: .claude/rules/ empty after rebuild",
                )

            # gz state succeeds — all entities resolve
            result = _run(["uv", "run", "gz", "state"], cwd=clone, check=False)
            self.assertEqual(
                result.returncode,
                0,
                f"gz state failed after clone recovery (exit {result.returncode}):\n"
                f"stdout: {result.stdout}\nstderr: {result.stderr}",
            )


if __name__ == "__main__":
    unittest.main()
