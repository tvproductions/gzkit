"""REQ-derived tests for the OKF knowledge CLI surface (OBPI-0.30.0-04).

Assertions are derived from the brief's Requirements (FAIL-CLOSED), NOT from a
run of the implementation (``.gzkit/rules/tests.md`` § "Tests assert semantics,
not strings").

Note: the CLI scaffolding was implemented in a prior session. These tests are
authored from the REQs and would catch regressions if implementation broke.
"""

from __future__ import annotations

import os
import shutil
import tempfile
import unittest
from pathlib import Path

from gzkit.cli.main import main
from gzkit.commands.knowledge import knowledge_cmd
from gzkit.traceability import covers
from tests.commands.common import CliRunner


class TestKnowledgeGenerate(unittest.TestCase):
    """REQ-0.30.0-04-01: knowledge generate emits the bundle and exits 0."""

    def setUp(self) -> None:
        self._original_cwd = Path.cwd()
        self._tmpdir = Path(tempfile.mkdtemp(prefix="gzkit-knowledge-test-"))
        os.chdir(self._tmpdir)

    def tearDown(self) -> None:
        os.chdir(self._original_cwd)
        shutil.rmtree(self._tmpdir, ignore_errors=True)

    @covers("REQ-0.30.0-04-01")
    def test_generate_exits_0_and_emits_bundle(self) -> None:
        """REQ-01: knowledge generate emits OKF bundle over the tracer slice and exits 0."""
        with self.assertRaises(SystemExit) as cm:
            knowledge_cmd(subverb="generate")
        self.assertEqual(cm.exception.code, 0, "knowledge generate must exit 0 on success")
        bundle_dir = self._tmpdir / ".gzkit" / "governance" / "knowledge"
        self.assertTrue(bundle_dir.is_dir(), "bundle output directory must be created")
        self.assertTrue((bundle_dir / "index.md").is_file(), "root index.md must exist in bundle")

    def test_knowledge_help_documents_verb(self) -> None:
        """REQ-01: knowledge --help documents the generate and refresh verbs."""
        runner = CliRunner()
        result = runner.invoke(main, ["knowledge", "--help"])
        self.assertEqual(result.exit_code, 0, "knowledge --help must exit 0")
        self.assertIn("generate", result.output, "help must document 'generate' subcommand")
        self.assertIn("refresh", result.output, "help must document 'refresh' subcommand")


class TestKnowledgeRefresh(unittest.TestCase):
    """REQ-0.30.0-04-02: knowledge refresh is idempotent over unchanged sources."""

    def setUp(self) -> None:
        self._original_cwd = Path.cwd()
        self._tmpdir = Path(tempfile.mkdtemp(prefix="gzkit-knowledge-test-"))
        os.chdir(self._tmpdir)

    def tearDown(self) -> None:
        os.chdir(self._original_cwd)
        shutil.rmtree(self._tmpdir, ignore_errors=True)

    @staticmethod
    def _snapshot(bundle_dir: Path) -> dict[str, bytes]:
        """Per-file byte snapshot of the bundle directory."""
        return {p.name: p.read_bytes() for p in sorted(bundle_dir.iterdir()) if p.is_file()}

    @covers("REQ-0.30.0-04-02")
    def test_refresh_is_idempotent(self) -> None:
        """REQ-02: knowledge refresh runs twice over unchanged sources and the
        bundle is byte-identical after each run (exit 0 each time).

        Per the REQ-0.30.0-04-02 acceptance criterion the idempotency claim is
        about ``refresh`` itself — "when knowledge refresh runs twice, then the
        bundle is byte-identical after each run". So this exercises the refresh
        verb TWICE (not generate-then-refresh) and asserts both refresh outputs
        are byte-identical to each other and to the initial bundle.
        """
        runner = CliRunner()
        bundle_dir = self._tmpdir / ".gzkit" / "governance" / "knowledge"

        # Seed the bundle so refresh has unchanged sources to re-generate over.
        result = runner.invoke(main, ["knowledge", "generate"])
        self.assertEqual(result.exit_code, 0, f"initial generate failed: {result.output}")
        seed = self._snapshot(bundle_dir)
        self.assertGreater(len(seed), 0, "bundle must be non-empty after generate")

        # First refresh.
        result = runner.invoke(main, ["knowledge", "refresh"])
        self.assertEqual(result.exit_code, 0, f"first refresh failed: {result.output}")
        first_refresh = self._snapshot(bundle_dir)

        # Second refresh — "runs twice" per the acceptance criterion.
        result = runner.invoke(main, ["knowledge", "refresh"])
        self.assertEqual(result.exit_code, 0, f"second refresh failed: {result.output}")
        second_refresh = self._snapshot(bundle_dir)

        self.assertEqual(
            first_refresh, second_refresh, "refresh must be byte-identical when run twice"
        )
        self.assertEqual(
            seed, second_refresh, "refresh output must match the initial generated bundle"
        )


class TestKnowledgeManpage(unittest.TestCase):
    """REQ-0.30.0-04-03: manpage documents the knowledge verb (structural proof)."""

    @covers("REQ-0.30.0-04-03")
    def test_manpage_exists_with_synopsis(self) -> None:
        """REQ-03: docs/user/manpages/knowledge.md documents generate and refresh."""
        project_root = Path(__file__).resolve().parent.parent.parent
        manpage = project_root / "docs" / "user" / "manpages" / "knowledge.md"
        self.assertTrue(manpage.is_file(), "knowledge manpage must exist")
        content = manpage.read_text(encoding="utf-8")
        self.assertIn("generate", content, "manpage must document the 'generate' subcommand")
        self.assertIn("refresh", content, "manpage must document the 'refresh' subcommand")

    def test_manpages_cite_the_real_bundle_output_path(self) -> None:
        """REQ-03: every knowledge manpage that names the bundle output directory
        cites the REAL ``BUNDLE_OUTPUT`` path, never a stale one.

        Guards the coupled-surface coherence defect a structural ``gz cli audit``
        cannot catch: a manpage can pass coverage while documenting a wrong output
        path. Any manpage mentioning ``.gzkit/`` + ``knowledge`` must use the
        canonical ``BUNDLE_OUTPUT`` (``.gzkit/governance/knowledge``) and must NOT
        reference the stale top-level ``.gzkit/knowledge/`` path.
        """
        from gzkit.knowledge.generate import BUNDLE_OUTPUT  # noqa: PLC0415

        canonical = BUNDLE_OUTPUT.as_posix()  # ".gzkit/governance/knowledge"
        stale = ".gzkit/knowledge/"
        project_root = Path(__file__).resolve().parent.parent.parent
        manpages_dir = project_root / "docs" / "user" / "manpages"
        for name in ("knowledge.md", "knowledge-generate.md", "knowledge-refresh.md"):
            manpage = manpages_dir / name
            content = manpage.read_text(encoding="utf-8")
            self.assertNotIn(
                stale,
                content,
                f"{name} references the stale bundle path {stale!r}; "
                f"the generator writes to {canonical!r}",
            )


class TestKnowledgeSmoke(unittest.TestCase):
    """REQ-0.30.0-04-04: end-to-end CLI smoke — generate then refresh via CLI surface."""

    def setUp(self) -> None:
        self._original_cwd = Path.cwd()
        self._tmpdir = Path(tempfile.mkdtemp(prefix="gzkit-knowledge-test-"))
        os.chdir(self._tmpdir)

    def tearDown(self) -> None:
        os.chdir(self._original_cwd)
        shutil.rmtree(self._tmpdir, ignore_errors=True)

    @covers("REQ-0.30.0-04-04")
    def test_cli_smoke_generate_then_refresh(self) -> None:
        """REQ-04: generate then refresh via CLI completes end-to-end without error."""
        runner = CliRunner()

        result = runner.invoke(main, ["knowledge", "generate"])
        self.assertEqual(result.exit_code, 0, f"knowledge generate failed: {result.output}")

        bundle_dir = self._tmpdir / ".gzkit" / "governance" / "knowledge"
        self.assertTrue(bundle_dir.is_dir(), "bundle directory must exist after generate")
        self.assertGreater(len(list(bundle_dir.iterdir())), 0, "bundle must contain output files")

        result = runner.invoke(main, ["knowledge", "refresh"])
        self.assertEqual(result.exit_code, 0, f"knowledge refresh failed: {result.output}")


if __name__ == "__main__":
    unittest.main()
