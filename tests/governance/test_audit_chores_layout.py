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
    def test_bare_proof_file_under_ops_chores_is_flagged(self) -> None:
        """A proof file under ``ops/chores/`` with no ``CHORE.md`` must flag.

        The legacy ``ops/chores/`` root MUST NOT exist (ADR-0.0.21 Decision
        #9). Filename-only matching missed bare proof debris (GHI #605): a
        chore body that wrote proofs to ``ops/chores/<slug>/proofs/``
        re-created the forbidden tree, and the audit passed because no
        ``CHORE.md``/``acceptance.json`` sat beside it. The forbidden root
        is the vector, not the filename.
        """
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            stray = (
                root
                / "ops"
                / "chores"
                / "test-isolation-compliance"
                / "proofs"
                / "health-report.json"
            )
            stray.parent.mkdir(parents=True, exist_ok=True)
            stray.write_text("{}\n", encoding="utf-8")

            errors = audit_chores_layout(root)

            self.assertEqual(len(errors), 1, msg=f"got: {errors}")
            self.assertEqual(errors[0].type, "chores_layout")
            self.assertIn(
                "ops/chores/test-isolation-compliance/proofs/health-report.json",
                errors[0].artifact,
            )

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
    """``audit_chores_layout`` runs to completion over the real repo tree."""

    @covers("REQ-0.0.21-08-07")
    def test_audit_runs_to_completion_on_repo_root(self) -> None:
        """``audit_chores_layout`` completes over the real repo and returns a list.

        Formerly a wall-clock budget (``elapsed < 10.0s``, widened 2.0s->5.0s->
        10.0s under GHI #443/#535). The ceiling measured host/suite load — not
        the audit's own cost — and flaked under concurrent suite IO while never
        catching a real regression. The timing assertion is abandoned per
        operator directive (2026-06-02; GHI #535 resolved in favour of abandon
        over a median-of-K ceiling). The durable invariant is structural: the
        audit runs to completion over the real tree and returns its findings.
        """
        repo_root = Path(__file__).resolve().parents[2]
        errors = audit_chores_layout(repo_root)
        self.assertIsInstance(errors, list)


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
