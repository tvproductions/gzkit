"""Fixture-level tests for ``audit_chores_layout`` (REQ-0.0.21-08-*).

These tests exercise the layout validator added by OBPI-0.0.21-08
against synthetic temp trees, isolating each scenario from repo-wide state.
Repo-state coverage lives in ``test_promoted_advisory_audits.py`` once the
scope is added to ``gz validate --all``.

Covers ADR-0.0.21 Decision #9 — `gz validate --chores-layout` fail-closes
on any ``CHORE.md`` or ``acceptance.json`` outside the canonical roots
(``src/gzkit/chores/`` and the project-scoped ``paths.chores``).
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from gzkit.governance.trust_audits import audit_chores_layout
from gzkit.traceability import covers


class StrayLayoutFlaggedTests(unittest.TestCase):
    """Stray ``CHORE.md`` / ``acceptance.json`` outside canonical roots fail."""

    @covers("REQ-0.0.21-08-03")
    def test_stray_chore_md_under_ops_chores_is_flagged(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            stray = root / "ops" / "chores" / "bogus" / "CHORE.md"
            stray.parent.mkdir(parents=True, exist_ok=True)
            stray.write_text("# bogus\n", encoding="utf-8")

            errors = audit_chores_layout(root)

            self.assertEqual(len(errors), 1, msg=f"got: {errors}")
            self.assertEqual(errors[0].type, "chores_layout")
            self.assertIn("ops/chores/bogus/CHORE.md", errors[0].artifact)

    @covers("REQ-0.0.21-08-03")
    def test_stray_acceptance_json_is_flagged(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            stray = root / "legacy" / "acceptance.json"
            stray.parent.mkdir(parents=True, exist_ok=True)
            stray.write_text("{}\n", encoding="utf-8")

            errors = audit_chores_layout(root)

            self.assertEqual(len(errors), 1)
            self.assertEqual(errors[0].type, "chores_layout")
            self.assertIn("legacy/acceptance.json", errors[0].artifact)


class CanonicalRootsAcceptedTests(unittest.TestCase):
    """Files under ``src/gzkit/chores/`` and ``.gzkit/chores/`` pass."""

    @covers("REQ-0.0.21-08-02")
    def test_src_gzkit_chores_root_accepts_chore_md(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = root / "src" / "gzkit" / "chores" / "x" / "CHORE.md"
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text("# canonical\n", encoding="utf-8")

            errors = audit_chores_layout(root)

            self.assertEqual(errors, [])

    @covers("REQ-0.0.21-08-02")
    def test_dot_gzkit_chores_root_accepts_acceptance_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = root / ".gzkit" / "chores" / "x" / "acceptance.json"
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text("{}\n", encoding="utf-8")

            errors = audit_chores_layout(root)

            self.assertEqual(errors, [])

    @covers("REQ-0.0.21-08-01")
    def test_clean_tree_returns_empty(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "src").mkdir()
            (root / "docs").mkdir()
            (root / "README.md").write_text("# project\n", encoding="utf-8")

            errors = audit_chores_layout(root)

            self.assertEqual(errors, [])


class WaiversAndExclusionsTests(unittest.TestCase):
    """Waiver file exempts paths; dotfile/cache trees are not walked."""

    @covers("REQ-0.0.21-08-05")
    def test_waivers_exempt_listed_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            stray = root / "legacy" / "CHORE.md"
            stray.parent.mkdir(parents=True, exist_ok=True)
            stray.write_text("# legacy\n", encoding="utf-8")

            data_dir = root / "data"
            data_dir.mkdir()
            (data_dir / "chores_layout_waivers.json").write_text(
                json.dumps(["legacy/CHORE.md"]),
                encoding="utf-8",
            )

            errors = audit_chores_layout(root)

            self.assertEqual(errors, [])

    @covers("REQ-0.0.21-08-06")
    def test_excluded_paths_are_skipped(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for relpath in (
                ".git/objects/CHORE.md",
                "__pycache__/CHORE.md",
                ".venv/lib/CHORE.md",
                "node_modules/pkg/CHORE.md",
                "dist/CHORE.md",
                "build/CHORE.md",
                ".some-hidden/CHORE.md",
            ):
                target = root / relpath
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text("# excluded\n", encoding="utf-8")

            errors = audit_chores_layout(root)

            self.assertEqual(errors, [])


class PerformanceBudgetTests(unittest.TestCase):
    """``audit_chores_layout`` must complete within budget on a typical tree."""

    @covers("REQ-0.0.21-08-07")
    def test_audit_completes_under_budget_on_repo_root(self) -> None:
        """GHI #535 follow-up: budget widened 5.0s → 10.0s.

        Same root cause as GHI #443's prior 2.0s → 5.0s widening: the ceiling
        sat too close to the suite-concurrent runtime ceiling (~5.0–5.13s on
        macOS under `gz git-sync --test`), producing intermittent flakes when
        the audit competed with concurrent suite IO. 10.0s still catches the
        kind of regression this guards against (a 2-3x scaling-factor change)
        without firing on host/load jitter. Structural follow-up tracked in
        GHI #535 (percentile/median-of-K-runs vs. absolute-seconds ceiling).
        """
        import time

        repo_root = Path(__file__).resolve().parents[2]
        start = time.perf_counter()
        errors = audit_chores_layout(repo_root)
        elapsed = time.perf_counter() - start

        self.assertLess(
            elapsed,
            10.0,
            msg=f"audit took {elapsed:.3f}s; budget is <10s; errors={len(errors)}",
        )


class CliExitCodeTests(unittest.TestCase):
    """``gz validate --chores-layout`` exits 3 on drift, 0 on clean."""

    @covers("REQ-0.0.21-08-04")
    def test_cli_exits_3_on_stray_chore_md(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            stray = root / "ops" / "chores" / "bogus" / "CHORE.md"
            stray.parent.mkdir(parents=True, exist_ok=True)
            stray.write_text("# bogus\n", encoding="utf-8")

            result = subprocess.run(
                [sys.executable, "-m", "gzkit", "validate", "--chores-layout"],
                cwd=root,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(
                result.returncode,
                3,
                msg=f"stdout={result.stdout!r} stderr={result.stderr!r}",
            )

    @covers("REQ-0.0.21-08-04")
    def test_cli_exits_0_on_clean_tree(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "src" / "gzkit" / "chores" / "x").mkdir(parents=True)
            (root / "src" / "gzkit" / "chores" / "x" / "CHORE.md").write_text(
                "# canonical\n", encoding="utf-8"
            )

            result = subprocess.run(
                [sys.executable, "-m", "gzkit", "validate", "--chores-layout"],
                cwd=root,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(
                result.returncode,
                0,
                msg=f"stdout={result.stdout!r} stderr={result.stderr!r}",
            )


if __name__ == "__main__":
    unittest.main()
