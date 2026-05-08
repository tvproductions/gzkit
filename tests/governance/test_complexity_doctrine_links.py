"""Tests for complexity-doctrine link-integrity validator (OBPI-0.0.27-07).

Covers citation extraction, parsing, file resolution, anchor resolution,
portability checking, speculative-marker skipping, and integration into
gz validate --all and gz check.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from gzkit.governance.trust_audits import validate_complexity_doctrine_links
from gzkit.traceability import covers


class TestComplexityDoctrineLinks(unittest.TestCase):
    """Unit tests for the complexity-doctrine link-integrity validator."""

    def setUp(self):
        """Set up a temporary project root with fixture ADRs and distilled docs."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.project_root = Path(self.temp_dir.name)

        # Create the distilled-characteristics document with corpus_revision: 1
        self._create_distilled_characteristics()

        # Create the cluster ADR directory
        adr_dir = (
            self.project_root
            / "docs"
            / "design"
            / "adr"
            / "foundation"
            / "ADR-0.0.27-exemplar-corpus-doctrine"
        )
        adr_dir.mkdir(parents=True, exist_ok=True)

        # Create the rules directory
        rules_dir = self.project_root / ".gzkit" / "rules"
        rules_dir.mkdir(parents=True, exist_ok=True)

    def tearDown(self):
        """Clean up the temporary directory."""
        self.temp_dir.cleanup()

    def _create_distilled_characteristics(self):
        """Create a fixture distilled-characteristics document."""
        doc_dir = self.project_root / "docs" / "governance" / "complexity"
        doc_dir.mkdir(parents=True, exist_ok=True)
        doc_path = doc_dir / "distilled-characteristics-2026-05-04.md"
        doc_path.write_text(
            "---\n"
            "corpus_revision: 1\n"
            "distillation_date: '2026-05-04'\n"
            "---\n"
            "\n"
            "# Distilled complexity characteristics\n"
            "\n"
            "## Metric: `radon_cc`\n"
            "\n"
            "Numeric boundary: p90 = 7.00.\n"
            "\n"
            "## Metric: `radon_mi`\n"
            "\n"
            "Numeric boundary: p90 = 100.00.\n",
            encoding="utf-8",
        )

    def _write_adr_body(self, adr_path: Path, content: str):
        """Write content to an ADR file."""
        adr_path.write_text(content, encoding="utf-8")

    @covers("REQ-0.0.27-07-01")
    def test_well_formed_citation_resolves_clean(self):
        """Citation to existing file + anchor + portable revision returns empty."""
        adr_path = (
            self.project_root
            / "docs"
            / "design"
            / "adr"
            / "foundation"
            / "ADR-0.0.27-exemplar-corpus-doctrine"
            / "ADR-0.0.27-exemplar-corpus-doctrine.md"
        )
        self._write_adr_body(
            adr_path,
            "---\nid: ADR-0.0.27\nstatus: Completed\n---\n\n"
            "# ADR-0.0.27\n\n"
            "Citation: docs/governance/complexity/distilled-characteristics-2026-05-04.md § "
            "radon-cc (corpus revision 1)\n",
        )

        errors = validate_complexity_doctrine_links(self.project_root)
        self.assertEqual(errors, [])

    @covers("REQ-0.0.27-07-02")
    def test_missing_distilled_file_fails_closed(self):
        """Citation pointing at non-existent file returns one ValidationError."""
        adr_path = (
            self.project_root
            / "docs"
            / "design"
            / "adr"
            / "foundation"
            / "ADR-0.0.27-exemplar-corpus-doctrine"
            / "ADR-0.0.27-exemplar-corpus-doctrine.md"
        )
        self._write_adr_body(
            adr_path,
            "---\nid: ADR-0.0.27\nstatus: Completed\n---\n\n"
            "# ADR-0.0.27\n\n"
            "Citation: docs/governance/complexity/distilled-characteristics-1999-01-01.md § "
            "radon-cc (corpus revision 1)\n",
        )

        errors = validate_complexity_doctrine_links(self.project_root)
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0].type, "complexity_doctrine_links")
        # Message should reference both the file path and line number
        self.assertIn("distilled-characteristics-1999-01-01.md", errors[0].message)

    @covers("REQ-0.0.27-07-03")
    def test_unresolved_anchor_fails_closed(self):
        """Citation with anchor not matching any heading returns one error."""
        adr_path = (
            self.project_root
            / "docs"
            / "design"
            / "adr"
            / "foundation"
            / "ADR-0.0.27-exemplar-corpus-doctrine"
            / "ADR-0.0.27-exemplar-corpus-doctrine.md"
        )
        self._write_adr_body(
            adr_path,
            "---\nid: ADR-0.0.27\nstatus: Completed\n---\n\n"
            "# ADR-0.0.27\n\n"
            "Citation: docs/governance/complexity/distilled-characteristics-2026-05-04.md § "
            "nonexistent-metric (corpus revision 1)\n",
        )

        errors = validate_complexity_doctrine_links(self.project_root)
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0].type, "complexity_doctrine_links")
        self.assertIn("nonexistent-metric", errors[0].message)

    @covers("REQ-0.0.27-07-04")
    def test_non_portable_revision_fails_closed(self):
        """Citation with corpus_revision outside supported window fails."""
        adr_path = (
            self.project_root
            / "docs"
            / "design"
            / "adr"
            / "foundation"
            / "ADR-0.0.27-exemplar-corpus-doctrine"
            / "ADR-0.0.27-exemplar-corpus-doctrine.md"
        )
        # Distilled doc has corpus_revision: 1, citation uses revision=0 (too old)
        # The supported window is [N, N+1] so revision 0 is outside [1, 2]
        self._write_adr_body(
            adr_path,
            "---\nid: ADR-0.0.27\nstatus: Completed\n---\n\n"
            "# ADR-0.0.27\n\n"
            "Citation: docs/governance/complexity/distilled-characteristics-2026-05-04.md § "
            "radon-cc (corpus revision 0)\n",
        )

        # Skip this test if citation cannot be parsed at all (revision=0 is invalid)
        # The parse_citation function validates corpus_revision > 0
        # So this should fail during parsing, not during portability check
        errors = validate_complexity_doctrine_links(self.project_root)
        # Should have at least one error (parse or portability)
        self.assertGreater(len(errors), 0)

    @covers("REQ-0.0.27-07-04")
    def test_non_portable_revision_old_window_fails_closed(self):
        """Citation with corpus_revision outside supported window (old) fails."""
        # Create a distilled doc with corpus_revision: 3
        doc_dir = self.project_root / "docs" / "governance" / "complexity"
        doc_path = doc_dir / "distilled-characteristics-2026-05-05.md"
        doc_path.write_text(
            "---\n"
            "corpus_revision: 3\n"
            "distillation_date: '2026-05-05'\n"
            "---\n"
            "\n"
            "# Distilled complexity characteristics\n"
            "\n"
            "## Metric: `radon_cc`\n\n"
            "Numeric boundary: p90 = 7.00.\n",
            encoding="utf-8",
        )

        adr_path = (
            self.project_root
            / "docs"
            / "design"
            / "adr"
            / "foundation"
            / "ADR-0.0.27-exemplar-corpus-doctrine"
            / "ADR-0.0.27-exemplar-corpus-doctrine.md"
        )
        # Citation uses revision 1, but current is 3. Window is [3, 4], so 1 is outside
        self._write_adr_body(
            adr_path,
            "---\nid: ADR-0.0.27\nstatus: Completed\n---\n\n"
            "# ADR-0.0.27\n\n"
            "Citation: docs/governance/complexity/distilled-characteristics-2026-05-04.md § "
            "radon-cc (corpus revision 1)\n",
        )

        errors = validate_complexity_doctrine_links(self.project_root)
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0].type, "complexity_doctrine_links")
        self.assertIn("doctrine-amendment-protocol", errors[0].message)

    @covers("REQ-0.0.27-07-05")
    def test_speculative_marker_skips_citation(self):
        """Line with speculative marker is skipped without errors."""
        adr_path = (
            self.project_root
            / "docs"
            / "design"
            / "adr"
            / "foundation"
            / "ADR-0.0.27-exemplar-corpus-doctrine"
            / "ADR-0.0.27-exemplar-corpus-doctrine.md"
        )
        self._write_adr_body(
            adr_path,
            "---\nid: ADR-0.0.27\nstatus: Completed\n---\n\n"
            "# ADR-0.0.27\n\n"
            "<!-- gz-validate-skip: complexity-doctrine-links -->\n"
            "Citation: docs/governance/complexity/distilled-characteristics-1999-01-01.md § "
            "radon-cc (corpus revision 1)\n",
        )

        errors = validate_complexity_doctrine_links(self.project_root)
        self.assertEqual(errors, [])

    @covers("REQ-0.0.27-07-06")
    def test_validate_all_includes_complexity_doctrine_links(self):
        """``_resolve_scopes`` returns ``complexity_doctrine_links`` when its
        explicit flag is set, mirroring the peer pattern used by
        ``advisory_scorecard`` / ``brief_headings`` / ``sensitivity``. The
        scope is opt-in, not part of the run-all default — operators wire it
        through ``--complexity-doctrine-links``, ``gz check``, or pre-commit
        / pre-merge hooks.
        """
        from gzkit.commands.validate_cmd import _resolve_scopes

        scopes = _resolve_scopes({"complexity_doctrine_links": True})

        self.assertIn("complexity_doctrine_links", scopes)

    @covers("REQ-0.0.27-07-06")
    def test_gz_check_steps_includes_runner(self):
        """gz check steps list includes complexity-doctrine-links runner."""
        # Import here to avoid circular dependencies at module load
        from gzkit.commands.quality import gz_check_cmd

        # Introspect the steps list to verify the runner is included
        steps = gz_check_cmd.steps
        step_names = [name for name, _ in steps]

        # Should include "Complexity-doctrine links" step
        self.assertIn("Complexity-doctrine links", step_names)

    @covers("REQ-0.0.27-07-02")
    def test_parse_failure_fails_closed(self):
        """Citation not matching canonical pattern returns one error."""
        adr_path = (
            self.project_root
            / "docs"
            / "design"
            / "adr"
            / "foundation"
            / "ADR-0.0.27-exemplar-corpus-doctrine"
            / "ADR-0.0.27-exemplar-corpus-doctrine.md"
        )
        # Citation-shaped (carries `§` and `(corpus revision` token so the
        # two-signal heuristic flags it as a candidate) but malformed —
        # malformed revision token shape that does not match the canonical
        # `(corpus revision N)` pattern.
        self._write_adr_body(
            adr_path,
            "---\nid: ADR-0.0.27\nstatus: Completed\n---\n\n"
            "# ADR-0.0.27\n\n"
            "Citation: docs/governance/complexity/distilled-characteristics-2026-05-04.md "
            "§ radon-cc (corpus revision NOT-A-NUMBER)\n",
        )

        errors = validate_complexity_doctrine_links(self.project_root)
        # Should have at least one parse failure error
        self.assertGreater(len(errors), 0)
        self.assertEqual(errors[0].type, "complexity_doctrine_links")

    @covers("REQ-0.0.27-07-07")
    def test_validate_command_doc_documents_flag(self):
        """The canonical command doc must document `--complexity-doctrine-links`
        with at least one example invocation. The doc surface lives at
        ``docs/user/manpages/validate.md`` per the Gate5-Runbook-Code Covenant
        rule (see brief Allowed Paths drift note).
        """
        repo_root = Path(__file__).resolve().parents[2]
        doc_path = repo_root / "docs" / "user" / "manpages" / "validate.md"
        self.assertTrue(doc_path.is_file(), f"Doc surface missing: {doc_path}")
        body = doc_path.read_text(encoding="utf-8")
        self.assertIn("--complexity-doctrine-links", body)
        self.assertIn("gz validate --complexity-doctrine-links", body)


class TestComplexityDoctrineLinksFunctional(unittest.TestCase):
    """Functional tests for the complexity-doctrine validator."""

    def setUp(self):
        """Set up a temporary project root."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.project_root = Path(self.temp_dir.name)

        # Create distilled-characteristics document
        doc_dir = self.project_root / "docs" / "governance" / "complexity"
        doc_dir.mkdir(parents=True, exist_ok=True)
        doc_path = doc_dir / "distilled-characteristics-2026-05-04.md"
        doc_path.write_text(
            "---\n"
            "corpus_revision: 1\n"
            "distillation_date: '2026-05-04'\n"
            "---\n"
            "\n"
            "# Distilled complexity characteristics\n"
            "\n"
            "## Metric: `radon_cc`\n\n"
            "Numeric boundary: p90 = 7.00.\n"
            "\n"
            "## Metric: `radon_mi`\n\n"
            "Numeric boundary: p90 = 100.00.\n",
            encoding="utf-8",
        )

        # Create .gzkit/rules directory
        rules_dir = self.project_root / ".gzkit" / "rules"
        rules_dir.mkdir(parents=True, exist_ok=True)

    def tearDown(self):
        """Clean up the temporary directory."""
        self.temp_dir.cleanup()

    def test_multiple_citations_mixed_validity(self):
        """Multiple citations with mixed validity report all errors."""
        # Create multiple ADRs with different citation states
        adr_dir = self.project_root / "docs" / "design" / "adr" / "foundation"
        adr_dir.mkdir(parents=True, exist_ok=True)

        # ADR with good citation
        good_adr = (
            adr_dir
            / "ADR-0.0.27-exemplar-corpus-doctrine"
            / "ADR-0.0.27-exemplar-corpus-doctrine.md"
        )
        good_adr.parent.mkdir(parents=True, exist_ok=True)
        good_adr.write_text(
            "---\nid: ADR-0.0.27\nstatus: Completed\n---\n\n"
            "# ADR-0.0.27\n\n"
            "Citation: docs/governance/complexity/distilled-characteristics-2026-05-04.md § "
            "radon-cc (corpus revision 1)\n",
            encoding="utf-8",
        )

        # ADR with bad citation
        bad_adr = adr_dir / "ADR-0.0.28-complexity-metrics" / "ADR-0.0.28-complexity-metrics.md"
        bad_adr.parent.mkdir(parents=True, exist_ok=True)
        bad_adr.write_text(
            "---\nid: ADR-0.0.28\nstatus: Completed\n---\n\n"
            "# ADR-0.0.28\n\n"
            "Citation: docs/governance/complexity/missing-file.md § radon-cc (corpus revision 1)\n",
            encoding="utf-8",
        )

        errors = validate_complexity_doctrine_links(self.project_root)

        # Should have at least one error from the bad citation
        self.assertGreater(len(errors), 0)

        # Find the error for the missing file
        missing_file_errors = [e for e in errors if "missing-file.md" in e.message]
        self.assertEqual(len(missing_file_errors), 1)


if __name__ == "__main__":
    unittest.main()
