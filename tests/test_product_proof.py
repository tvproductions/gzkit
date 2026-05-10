"""Tests for product proof gate in quality module."""

import tempfile
import textwrap
import unittest
from pathlib import Path

from gzkit.quality import (
    ObpiProofStatus,
    _check_closeout_artifact_proof,
    _check_command_doc_proof,
    _check_concepts_page_proof,
    _check_docstring_proof,
    _check_governance_artifact_proof,
    _check_release_artifact_proof,
    _check_runbook_proof,
    _extract_allowed_paths,
    _extract_obpi_slug,
    check_product_proof,
)
from gzkit.traceability import covers


class TestExtractAllowedPaths(unittest.TestCase):
    """Tests for _extract_allowed_paths."""

    @covers("REQ-0.23.0-02-01")
    def test_extracts_paths_from_brief(self) -> None:
        brief = textwrap.dedent("""\
            ## OBJECTIVE

            Do something useful.

            ## ALLOWED PATHS

            - `src/gzkit/quality.py`
            - `src/gzkit/cli.py`
            - `tests/test_product_proof.py`
            - `docs/user/manpages/closeout.md`

            ## REQUIREMENTS
            """)
        paths = _extract_allowed_paths(brief)
        self.assertEqual(
            paths,
            [
                "src/gzkit/quality.py",
                "src/gzkit/cli.py",
                "tests/test_product_proof.py",
                "docs/user/manpages/closeout.md",
            ],
        )

    @covers("REQ-0.23.0-02-01")
    def test_no_allowed_paths_section(self) -> None:
        brief = "## OBJECTIVE\n\nDo something.\n"
        self.assertEqual(_extract_allowed_paths(brief), [])

    @covers("REQ-0.23.0-02-01")
    def test_paths_with_descriptions(self) -> None:
        brief = textwrap.dedent("""\
            ## ALLOWED PATHS

            - `src/foo.py` — the main module
            - `tests/test_foo.py` — tests for foo

            ## NEXT SECTION
            """)
        paths = _extract_allowed_paths(brief)
        self.assertEqual(paths, ["src/foo.py", "tests/test_foo.py"])


class TestExtractObpiSlug(unittest.TestCase):
    """Tests for _extract_obpi_slug."""

    @covers("REQ-0.23.0-02-01")
    def test_standard_id(self) -> None:
        self.assertEqual(
            _extract_obpi_slug("OBPI-0.23.0-02-product-proof-gate"),
            "product-proof-gate",
        )

    @covers("REQ-0.23.0-02-01")
    def test_short_id(self) -> None:
        self.assertEqual(_extract_obpi_slug("OBPI-0.1.0-01"), "OBPI-0.1.0-01")


class TestCheckRunbookProof(unittest.TestCase):
    """Tests for _check_runbook_proof."""

    @covers("REQ-0.23.0-02-04")
    def test_id_match(self) -> None:
        runbook = "See OBPI-0.23.0-02 for details.\n"
        self.assertTrue(_check_runbook_proof("OBPI-0.23.0-02", "product-proof-gate", runbook))

    @covers("REQ-0.23.0-02-04")
    def test_slug_keyword_match(self) -> None:
        runbook = "The product proof gate validates documentation.\n"
        self.assertTrue(_check_runbook_proof("OBPI-0.23.0-02", "product-proof-gate", runbook))

    @covers("REQ-0.23.0-02-04")
    def test_no_match(self) -> None:
        runbook = "Nothing relevant here.\n"
        self.assertFalse(_check_runbook_proof("OBPI-0.23.0-02", "product-proof-gate", runbook))

    @covers("REQ-0.23.0-02-04")
    def test_case_insensitive_slug(self) -> None:
        runbook = "The Product Proof Gate is important.\n"
        self.assertTrue(_check_runbook_proof("OBPI-0.23.0-02", "product-proof-gate", runbook))


class TestCheckCommandDocProof(unittest.TestCase):
    """Tests for _check_command_doc_proof."""

    @covers("REQ-0.23.0-02-05")
    def test_existing_doc_with_content(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            doc_dir = root / "docs" / "user" / "manpages"
            doc_dir.mkdir(parents=True)
            doc = doc_dir / "closeout.md"
            doc.write_text("# gz closeout\n\n" + "x" * 200, encoding="utf-8")

            allowed = ["docs/user/manpages/closeout.md", "src/gzkit/cli.py"]
            self.assertTrue(_check_command_doc_proof(allowed, root))

    @covers("REQ-0.23.0-02-05")
    def test_missing_doc_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            allowed = ["docs/user/manpages/closeout.md"]
            self.assertFalse(_check_command_doc_proof(allowed, root))

    @covers("REQ-0.23.0-02-05")
    def test_empty_doc(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            doc_dir = root / "docs" / "user" / "manpages"
            doc_dir.mkdir(parents=True)
            doc = doc_dir / "closeout.md"
            doc.write_text("# Title\n", encoding="utf-8")

            allowed = ["docs/user/manpages/closeout.md"]
            self.assertFalse(_check_command_doc_proof(allowed, root))

    @covers("REQ-0.23.0-02-05")
    def test_no_command_docs_in_allowed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            allowed = ["src/gzkit/quality.py"]
            self.assertFalse(_check_command_doc_proof(allowed, root))


class TestCheckDocstringProof(unittest.TestCase):
    """Tests for _check_docstring_proof."""

    @covers("REQ-0.23.0-02-06")
    def test_public_function_with_docstring(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            src_dir = root / "src" / "gzkit"
            src_dir.mkdir(parents=True)
            py_file = src_dir / "quality.py"
            py_file.write_text(
                textwrap.dedent("""\
                    def check_product_proof(adr_id):
                        \"\"\"Validate product proof for an ADR.\"\"\"
                        pass
                    """),
                encoding="utf-8",
            )
            allowed = ["src/gzkit/quality.py"]
            self.assertTrue(_check_docstring_proof(allowed, root))

    @covers("REQ-0.23.0-02-06")
    def test_only_private_functions(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            src_dir = root / "src" / "gzkit"
            src_dir.mkdir(parents=True)
            py_file = src_dir / "quality.py"
            py_file.write_text(
                textwrap.dedent("""\
                    def _private_helper():
                        \"\"\"Private helper function.\"\"\"
                        pass
                    """),
                encoding="utf-8",
            )
            allowed = ["src/gzkit/quality.py"]
            self.assertFalse(_check_docstring_proof(allowed, root))

    @covers("REQ-0.23.0-02-06")
    def test_no_docstrings(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            src_dir = root / "src" / "gzkit"
            src_dir.mkdir(parents=True)
            py_file = src_dir / "quality.py"
            py_file.write_text("def run():\n    pass\n", encoding="utf-8")
            allowed = ["src/gzkit/quality.py"]
            self.assertFalse(_check_docstring_proof(allowed, root))

    @covers("REQ-0.23.0-02-06")
    def test_non_src_paths_ignored(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            allowed = ["tests/test_foo.py"]
            self.assertFalse(_check_docstring_proof(allowed, root))

    @covers("REQ-0.23.0-02-06")
    def test_class_with_docstring(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            src_dir = root / "src" / "gzkit"
            src_dir.mkdir(parents=True)
            py_file = src_dir / "models.py"
            py_file.write_text(
                textwrap.dedent("""\
                    class ProofResult:
                        \"\"\"Result of proof validation check.\"\"\"
                        pass
                    """),
                encoding="utf-8",
            )
            allowed = ["src/gzkit/models.py"]
            self.assertTrue(_check_docstring_proof(allowed, root))


class TestCheckGovernanceArtifactProof(unittest.TestCase):
    """Tests for _check_governance_artifact_proof."""

    @covers("REQ-0.23.0-02-01")
    def test_existing_artifact_with_content(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            gzkit_dir = root / ".gzkit" / "personas"
            gzkit_dir.mkdir(parents=True)
            artifact = gzkit_dir / "main-session.md"
            artifact.write_text("---\nname: main-session\n---\n" + "x" * 200, encoding="utf-8")

            allowed = [".gzkit/personas/main-session.md"]
            self.assertTrue(_check_governance_artifact_proof(allowed, root))

    @covers("REQ-0.23.0-02-01")
    def test_missing_artifact_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            allowed = [".gzkit/personas/main-session.md"]
            self.assertFalse(_check_governance_artifact_proof(allowed, root))

    @covers("REQ-0.23.0-02-01")
    def test_empty_artifact(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            gzkit_dir = root / ".gzkit" / "personas"
            gzkit_dir.mkdir(parents=True)
            artifact = gzkit_dir / "empty.md"
            artifact.write_text("# Title\n", encoding="utf-8")

            allowed = [".gzkit/personas/empty.md"]
            self.assertFalse(_check_governance_artifact_proof(allowed, root))

    @covers("REQ-0.23.0-02-01")
    def test_non_gzkit_paths_ignored(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            allowed = ["src/gzkit/quality.py", "docs/user/runbook.md"]
            self.assertFalse(_check_governance_artifact_proof(allowed, root))

    @covers("REQ-0.23.0-02-01")
    def test_no_allowed_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.assertFalse(_check_governance_artifact_proof([], root))

    def test_docs_governance_artifact_with_content_post_440(self) -> None:
        """GHI #440: foundation doctrine OBPIs editing docs/governance/* satisfy
        the governance_artifact proof type. Pre-#440, only .gzkit/ paths were
        accepted, silently classifying every doctrine OBPI as MISSING.
        """
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            gov_dir = root / "docs" / "governance"
            gov_dir.mkdir(parents=True)
            artifact = gov_dir / "trust-doctrine.md"
            artifact.write_text(
                "# Trust Doctrine\n\n" + "T0 invariant body. " * 20,
                encoding="utf-8",
            )

            allowed = ["docs/governance/trust-doctrine.md"]
            self.assertTrue(_check_governance_artifact_proof(allowed, root))


class TestCheckReleaseArtifactProof(unittest.TestCase):
    """GHI-118: docs/releases/PATCH-vX.Y.Z.md is valid product proof."""

    @covers("REQ-0.23.0-02-01")
    def test_existing_release_manifest_with_content(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            releases_dir = root / "docs" / "releases"
            releases_dir.mkdir(parents=True)
            manifest = releases_dir / "PATCH-v0.24.3.md"
            manifest.write_text(
                "# Patch Release v0.24.3\n\n"
                "**Date:** 2026-04-08\n\n"
                "## Qualifying GHIs\n\n"
                "| # | Title | Status |\n|---|---|---|\n"
                "| 100 | sample | qualified |\n",
                encoding="utf-8",
            )

            allowed = ["docs/releases/PATCH-v0.24.3.md"]
            self.assertTrue(_check_release_artifact_proof(allowed, root))

    @covers("REQ-0.23.0-02-01")
    def test_missing_release_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            allowed = ["docs/releases/PATCH-v0.24.3.md"]
            self.assertFalse(_check_release_artifact_proof(allowed, root))

    @covers("REQ-0.23.0-02-01")
    def test_empty_release_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            releases_dir = root / "docs" / "releases"
            releases_dir.mkdir(parents=True)
            (releases_dir / "PATCH-v0.0.0.md").write_text("# stub\n", encoding="utf-8")
            allowed = ["docs/releases/PATCH-v0.0.0.md"]
            self.assertFalse(_check_release_artifact_proof(allowed, root))

    @covers("REQ-0.23.0-02-01")
    def test_non_releases_paths_ignored(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            allowed = ["docs/user/runbook.md", "src/gzkit/quality.py"]
            self.assertFalse(_check_release_artifact_proof(allowed, root))


class TestCheckConceptsPageProof(unittest.TestCase):
    """GHI #265: Foundation-doctrine ADRs that land concepts pages need proof coverage."""

    @covers("REQ-0.23.0-02-01")
    def test_existing_concepts_page_with_content(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            concepts_dir = root / "docs" / "user" / "concepts"
            concepts_dir.mkdir(parents=True)
            page = concepts_dir / "adr-taxonomy.md"
            page.write_text("# ADR taxonomy\n\n" + "x" * 200, encoding="utf-8")
            allowed = [
                "docs/user/concepts/adr-taxonomy.md",
                "docs/user/index.md",
            ]
            self.assertTrue(_check_concepts_page_proof(allowed, root))

    @covers("REQ-0.23.0-02-01")
    def test_missing_concepts_page(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            allowed = ["docs/user/concepts/adr-taxonomy.md"]
            self.assertFalse(_check_concepts_page_proof(allowed, root))

    @covers("REQ-0.23.0-02-01")
    def test_empty_concepts_page(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            concepts_dir = root / "docs" / "user" / "concepts"
            concepts_dir.mkdir(parents=True)
            (concepts_dir / "stub.md").write_text("# stub\n", encoding="utf-8")
            allowed = ["docs/user/concepts/stub.md"]
            self.assertFalse(_check_concepts_page_proof(allowed, root))

    @covers("REQ-0.23.0-02-01")
    def test_non_concepts_paths_ignored(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            allowed = ["docs/user/runbook.md", "src/gzkit/quality.py"]
            self.assertFalse(_check_concepts_page_proof(allowed, root))


class TestCheckCloseoutArtifactProof(unittest.TestCase):
    """Closeout-kind OBPIs cite ADR-CLOSEOUT-FORM / EVALUATION_SCORECARD as proof."""

    @covers("REQ-0.0.20-05-11")
    def test_existing_closeout_form_with_content(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            adr_dir = root / "docs" / "design" / "adr" / "foundation" / "ADR-X"
            adr_dir.mkdir(parents=True)
            (adr_dir / "ADR-CLOSEOUT-FORM.md").write_text(
                "# Closeout\n\n" + "x" * 200, encoding="utf-8"
            )
            allowed = ["docs/design/adr/foundation/ADR-X/ADR-CLOSEOUT-FORM.md"]
            self.assertTrue(_check_closeout_artifact_proof(allowed, root))

    @covers("REQ-0.0.20-05-13")
    def test_existing_evaluation_scorecard_with_content(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            adr_dir = root / "docs" / "design" / "adr" / "foundation" / "ADR-X"
            adr_dir.mkdir(parents=True)
            (adr_dir / "EVALUATION_SCORECARD.md").write_text(
                "# Scorecard\n\n" + "x" * 200, encoding="utf-8"
            )
            allowed = ["docs/design/adr/foundation/ADR-X/EVALUATION_SCORECARD.md"]
            self.assertTrue(_check_closeout_artifact_proof(allowed, root))

    @covers("REQ-0.0.20-05-11")
    def test_missing_closeout_artifact(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            allowed = ["docs/design/adr/foundation/ADR-X/ADR-CLOSEOUT-FORM.md"]
            self.assertFalse(_check_closeout_artifact_proof(allowed, root))

    @covers("REQ-0.0.20-05-11")
    def test_empty_closeout_artifact(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            adr_dir = root / "docs" / "design" / "adr" / "foundation" / "ADR-X"
            adr_dir.mkdir(parents=True)
            (adr_dir / "ADR-CLOSEOUT-FORM.md").write_text("# stub\n", encoding="utf-8")
            allowed = ["docs/design/adr/foundation/ADR-X/ADR-CLOSEOUT-FORM.md"]
            self.assertFalse(_check_closeout_artifact_proof(allowed, root))

    @covers("REQ-0.0.20-05-11")
    def test_non_closeout_filename_ignored(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            adr_dir = root / "docs" / "design" / "adr" / "foundation" / "ADR-X"
            adr_dir.mkdir(parents=True)
            (adr_dir / "ADR-X.md").write_text("x" * 200, encoding="utf-8")
            allowed = ["docs/design/adr/foundation/ADR-X/ADR-X.md"]
            self.assertFalse(_check_closeout_artifact_proof(allowed, root))

    @covers("REQ-0.0.20-05-11")
    def test_non_adr_paths_ignored(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            allowed = ["docs/user/runbook.md", "src/gzkit/quality.py"]
            self.assertFalse(_check_closeout_artifact_proof(allowed, root))


class TestCheckRunbookProofRelaxed(unittest.TestCase):
    """GHI #265: runbook.md in allowed paths satisfies proof when runbook has content."""

    @covers("REQ-0.23.0-02-04")
    def test_runbook_in_allowed_paths_accepts_without_slug_match(self) -> None:
        """OBPI-02 'runbook-prd-to-adr' with section '## PRD → ADR Derivation'
        (no literal slug phrase) should pass because runbook.md is in allowed paths."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "docs" / "user").mkdir(parents=True)
            runbook = root / "docs" / "user" / "runbook.md"
            runbook.write_text("## PRD → ADR Derivation\n\n" + "x" * 200, encoding="utf-8")
            brief_dir = root / "briefs"
            brief_dir.mkdir()
            brief = brief_dir / "OBPI-0.0.18-02-runbook-prd-to-adr.md"
            brief.write_text(
                "## ALLOWED PATHS\n\n- `docs/user/runbook.md`\n\n## NEXT\n",
                encoding="utf-8",
            )
            obpi_files = {"OBPI-0.0.18-02-runbook-prd-to-adr": brief}
            result = check_product_proof("ADR-0.0.18", obpi_files, root)
            self.assertTrue(result.success, "runbook-in-allowed-paths should pass")
            self.assertEqual(result.obpi_proofs[0].proof_type, "runbook")

    @covers("REQ-0.23.0-02-04")
    def test_empty_runbook_not_sufficient(self) -> None:
        """An empty runbook file in allowed paths does not satisfy proof."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "docs" / "user").mkdir(parents=True)
            (root / "docs" / "user" / "runbook.md").write_text("# stub\n", encoding="utf-8")
            brief_dir = root / "briefs"
            brief_dir.mkdir()
            brief = brief_dir / "OBPI-0.0.18-02-runbook-prd-to-adr.md"
            brief.write_text(
                "## ALLOWED PATHS\n\n- `docs/user/runbook.md`\n\n## NEXT\n",
                encoding="utf-8",
            )
            obpi_files = {"OBPI-0.0.18-02-runbook-prd-to-adr": brief}
            result = check_product_proof("ADR-0.0.18", obpi_files, root)
            self.assertFalse(result.success)


class TestConceptsPageIntegration(unittest.TestCase):
    """GHI #265: concepts_page proof wired into check_product_proof."""

    @covers("REQ-0.23.0-02-01")
    def test_concepts_page_satisfies_check_product_proof(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            concepts_dir = root / "docs" / "user" / "concepts"
            concepts_dir.mkdir(parents=True)
            (concepts_dir / "adr-taxonomy.md").write_text(
                "# ADR taxonomy\n\n" + "x" * 500, encoding="utf-8"
            )
            (root / "docs" / "user" / "runbook.md").write_text("empty\n", encoding="utf-8")
            brief_dir = root / "briefs"
            brief_dir.mkdir()
            brief = brief_dir / "OBPI-0.0.18-01-concepts-page.md"
            brief.write_text(
                "## ALLOWED PATHS\n\n"
                "- `docs/user/concepts/adr-taxonomy.md`\n"
                "- `docs/user/index.md`\n"
                "- `mkdocs.yml`\n"
                "\n## NEXT\n",
                encoding="utf-8",
            )
            obpi_files = {"OBPI-0.0.18-01-concepts-page": brief}
            result = check_product_proof("ADR-0.0.18", obpi_files, root)
            self.assertTrue(result.success)
            self.assertEqual(result.obpi_proofs[0].proof_type, "concepts_page")


class TestObpiProofStatus(unittest.TestCase):
    """Tests for ObpiProofStatus model."""

    @covers("REQ-0.23.0-02-01")
    def test_has_proof_runbook(self) -> None:
        status = ObpiProofStatus(obpi_id="OBPI-0.1.0-01", runbook_found=True)
        self.assertTrue(status.has_proof)
        self.assertEqual(status.proof_type, "runbook")

    @covers("REQ-0.23.0-02-01")
    def test_has_proof_command_doc(self) -> None:
        status = ObpiProofStatus(obpi_id="OBPI-0.1.0-01", command_doc_found=True)
        self.assertTrue(status.has_proof)
        self.assertEqual(status.proof_type, "command_doc")

    @covers("REQ-0.23.0-02-01")
    def test_has_proof_docstring(self) -> None:
        status = ObpiProofStatus(obpi_id="OBPI-0.1.0-01", docstring_found=True)
        self.assertTrue(status.has_proof)
        self.assertEqual(status.proof_type, "docstring")

    @covers("REQ-0.23.0-02-01")
    def test_has_proof_governance_artifact(self) -> None:
        status = ObpiProofStatus(obpi_id="OBPI-0.1.0-01", governance_artifact_found=True)
        self.assertTrue(status.has_proof)
        self.assertEqual(status.proof_type, "governance_artifact")

    @covers("REQ-0.23.0-02-01")
    def test_missing(self) -> None:
        status = ObpiProofStatus(obpi_id="OBPI-0.1.0-01")
        self.assertFalse(status.has_proof)
        self.assertEqual(status.proof_type, "MISSING")

    @covers("REQ-0.23.0-02-01")
    def test_priority_order(self) -> None:
        """Runbook takes priority over command_doc over docstring over governance_artifact."""
        status = ObpiProofStatus(
            obpi_id="OBPI-0.1.0-01",
            runbook_found=True,
            command_doc_found=True,
            docstring_found=True,
            governance_artifact_found=True,
        )
        self.assertEqual(status.proof_type, "runbook")

    @covers("REQ-0.23.0-02-01")
    def test_governance_artifact_lowest_priority(self) -> None:
        status = ObpiProofStatus(obpi_id="OBPI-0.1.0-01", governance_artifact_found=True)
        self.assertEqual(status.proof_type, "governance_artifact")

    @covers("REQ-0.23.0-02-01")
    def test_has_proof_release_artifact(self) -> None:
        status = ObpiProofStatus(obpi_id="OBPI-0.1.0-01", release_artifact_found=True)
        self.assertTrue(status.has_proof)
        self.assertEqual(status.proof_type, "release_artifact")

    @covers("REQ-0.23.0-02-01")
    def test_has_proof_concepts_page(self) -> None:
        status = ObpiProofStatus(obpi_id="OBPI-0.1.0-01", concepts_page_found=True)
        self.assertTrue(status.has_proof)
        self.assertEqual(status.proof_type, "concepts_page")


class TestCheckProductProof(unittest.TestCase):
    """Integration tests for check_product_proof."""

    def _make_project(self, tmp: str) -> Path:
        root = Path(tmp)
        (root / "docs" / "user").mkdir(parents=True)
        (root / "docs" / "user" / "manpages").mkdir(parents=True)
        (root / "src" / "gzkit").mkdir(parents=True)
        return root

    def _make_brief(self, root: Path, obpi_id: str, allowed_paths: list[str]) -> Path:
        brief_dir = root / "briefs"
        brief_dir.mkdir(exist_ok=True)
        brief_path = brief_dir / f"{obpi_id}.md"
        paths_section = "\n".join(f"- `{p}`" for p in allowed_paths)
        brief_path.write_text(
            f"# {obpi_id}\n\n## ALLOWED PATHS\n\n{paths_section}\n\n## REQUIREMENTS\n",
            encoding="utf-8",
        )
        return brief_path

    @covers("REQ-0.23.0-02-01")
    @covers("REQ-0.23.0-02-04")
    def test_all_proof_types_present(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = self._make_project(tmp)
            # Create runbook mentioning the OBPI
            (root / "docs" / "user" / "runbook.md").write_text(
                "## Pipeline\n\nUse OBPI-0.1.0-01 for the pipeline check.\n",
                encoding="utf-8",
            )
            brief = self._make_brief(
                root,
                "OBPI-0.1.0-01-pipeline-check",
                ["src/gzkit/pipeline.py", "docs/user/manpages/pipeline.md"],
            )
            obpi_files = {"OBPI-0.1.0-01-pipeline-check": brief}
            result = check_product_proof("ADR-0.1.0", obpi_files, root)
            self.assertTrue(result.success)
            self.assertEqual(result.missing_count, 0)
            self.assertEqual(result.obpi_proofs[0].proof_type, "runbook")

    @covers("REQ-0.23.0-02-01")
    def test_missing_proof(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = self._make_project(tmp)
            (root / "docs" / "user" / "runbook.md").write_text(
                "Nothing relevant here.\n", encoding="utf-8"
            )
            brief = self._make_brief(
                root, "OBPI-0.1.0-01-something-obscure", ["src/gzkit/obscure.py"]
            )
            obpi_files = {"OBPI-0.1.0-01-something-obscure": brief}
            result = check_product_proof("ADR-0.1.0", obpi_files, root)
            self.assertFalse(result.success)
            self.assertEqual(result.missing_count, 1)
            self.assertEqual(result.obpi_proofs[0].proof_type, "MISSING")

    @covers("REQ-0.23.0-02-01")
    @covers("REQ-0.23.0-02-06")
    def test_docstring_only_proof(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = self._make_project(tmp)
            (root / "docs" / "user" / "runbook.md").write_text("Empty.\n", encoding="utf-8")
            # Create source file with docstring
            src_file = root / "src" / "gzkit" / "checker.py"
            src_file.write_text(
                'def validate_proof(adr_id):\n    """Validate proof for ADR."""\n    pass\n',
                encoding="utf-8",
            )
            brief = self._make_brief(root, "OBPI-0.1.0-01-checker", ["src/gzkit/checker.py"])
            obpi_files = {"OBPI-0.1.0-01-checker": brief}
            result = check_product_proof("ADR-0.1.0", obpi_files, root)
            self.assertTrue(result.success)
            self.assertEqual(result.obpi_proofs[0].proof_type, "docstring")

    @covers("REQ-0.23.0-02-01")
    def test_empty_obpi_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = self._make_project(tmp)
            result = check_product_proof("ADR-0.1.0", {}, root)
            self.assertTrue(result.success)
            self.assertEqual(result.missing_count, 0)
            self.assertEqual(result.obpi_proofs, [])

    @covers("REQ-0.23.0-02-01")
    def test_multiple_obpis_mixed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = self._make_project(tmp)
            (root / "docs" / "user" / "runbook.md").write_text(
                "Use the pipeline check feature.\n", encoding="utf-8"
            )
            # OBPI 1: has runbook proof (slug = "pipeline-check")
            brief1 = self._make_brief(
                root, "OBPI-0.1.0-01-pipeline-check", ["src/gzkit/pipeline.py"]
            )
            # OBPI 2: no proof at all
            brief2 = self._make_brief(root, "OBPI-0.1.0-02-secret-thing", ["src/gzkit/secret.py"])
            obpi_files = {
                "OBPI-0.1.0-01-pipeline-check": brief1,
                "OBPI-0.1.0-02-secret-thing": brief2,
            }
            result = check_product_proof("ADR-0.1.0", obpi_files, root)
            self.assertFalse(result.success)
            self.assertEqual(result.missing_count, 1)

    @covers("REQ-0.23.0-02-01")
    @covers("REQ-0.23.0-02-06")
    def test_no_runbook_file(self) -> None:
        """Product proof works even when runbook doesn't exist."""
        with tempfile.TemporaryDirectory() as tmp:
            root = self._make_project(tmp)
            # Create source file with docstring
            src_file = root / "src" / "gzkit" / "checker.py"
            src_file.write_text(
                'def validate_proof(adr_id):\n    """Validate proof for ADR."""\n    pass\n',
                encoding="utf-8",
            )
            brief = self._make_brief(root, "OBPI-0.1.0-01-checker", ["src/gzkit/checker.py"])
            obpi_files = {"OBPI-0.1.0-01-checker": brief}
            result = check_product_proof("ADR-0.1.0", obpi_files, root)
            self.assertTrue(result.success)

    @covers("REQ-0.23.0-02-01")
    def test_governance_artifact_proof(self) -> None:
        """OBPIs with .gzkit/ allowed paths pass via governance artifact proof."""
        with tempfile.TemporaryDirectory() as tmp:
            root = self._make_project(tmp)
            (root / "docs" / "user" / "runbook.md").write_text("Empty.\n", encoding="utf-8")
            # Create governance artifact
            personas_dir = root / ".gzkit" / "personas"
            personas_dir.mkdir(parents=True)
            persona = personas_dir / "main-session.md"
            persona.write_text("---\nname: main-session\n---\n" + "x" * 200, encoding="utf-8")
            brief = self._make_brief(
                root,
                "OBPI-0.0.12-01-main-session-persona",
                [".gzkit/personas/main-session.md"],
            )
            obpi_files = {"OBPI-0.0.12-01-main-session-persona": brief}
            result = check_product_proof("ADR-0.0.12", obpi_files, root)
            self.assertTrue(result.success)
            self.assertEqual(result.obpi_proofs[0].proof_type, "governance_artifact")


class TestDataOrSchemaArtifactProof(unittest.TestCase):
    """Tests for data/registry and JSON-schema artifact proof (GHI #363)."""

    def _make_project(self, tmp: str) -> Path:
        root = Path(tmp)
        (root / "docs" / "user").mkdir(parents=True)
        (root / "src" / "gzkit").mkdir(parents=True)
        (root / "data").mkdir(parents=True)
        (root / "src" / "gzkit" / "schemas").mkdir(parents=True)
        return root

    def _make_brief(self, root: Path, obpi_id: str, allowed_paths: list[str]) -> Path:
        brief_dir = root / "briefs"
        brief_dir.mkdir(exist_ok=True)
        brief_path = brief_dir / f"{obpi_id}.md"
        paths_section = "\n".join(f"- `{p}`" for p in allowed_paths)
        brief_path.write_text(
            f"# {obpi_id}\n\n## ALLOWED PATHS\n\n{paths_section}\n\n## REQUIREMENTS\n",
            encoding="utf-8",
        )
        return brief_path

    def test_data_registry_artifact_satisfies_proof(self) -> None:
        """An OBPI authoring data/<file>.json passes via data_or_schema_artifact proof."""
        with tempfile.TemporaryDirectory() as tmp:
            root = self._make_project(tmp)
            (root / "docs" / "user" / "runbook.md").write_text("Empty.\n", encoding="utf-8")
            registry = root / "data" / "security_surfaces.json"
            registry.write_text("{" + '"surfaces": []' + "}\n" + "x" * 200, encoding="utf-8")
            brief = self._make_brief(
                root,
                "OBPI-0.0.22-02-security-surface-registry",
                ["data/security_surfaces.json"],
            )
            obpi_files = {"OBPI-0.0.22-02-security-surface-registry": brief}
            result = check_product_proof("ADR-0.0.22", obpi_files, root)
            self.assertTrue(result.success)
            self.assertEqual(result.obpi_proofs[0].proof_type, "data_or_schema_artifact")

    def test_json_schema_artifact_satisfies_proof(self) -> None:
        """An OBPI authoring src/gzkit/schemas/*.json passes via data_or_schema proof."""
        with tempfile.TemporaryDirectory() as tmp:
            root = self._make_project(tmp)
            (root / "docs" / "user" / "runbook.md").write_text("Empty.\n", encoding="utf-8")
            schema = root / "src" / "gzkit" / "schemas" / "obpi.json"
            schema.write_text(
                '{"$schema": "https://json-schema.org/draft/2020-12/schema",'
                ' "type": "object"}\n' + "x" * 200,
                encoding="utf-8",
            )
            brief = self._make_brief(
                root,
                "OBPI-0.0.22-01-schema-frontmatter-field",
                ["src/gzkit/schemas/obpi.json"],
            )
            obpi_files = {"OBPI-0.0.22-01-schema-frontmatter-field": brief}
            result = check_product_proof("ADR-0.0.22", obpi_files, root)
            self.assertTrue(result.success)
            self.assertEqual(result.obpi_proofs[0].proof_type, "data_or_schema_artifact")

    def test_empty_data_file_not_substantive(self) -> None:
        """Empty data/registry file does not satisfy proof."""
        with tempfile.TemporaryDirectory() as tmp:
            root = self._make_project(tmp)
            (root / "docs" / "user" / "runbook.md").write_text("Empty.\n", encoding="utf-8")
            (root / "data" / "x.json").write_text("{}", encoding="utf-8")
            brief = self._make_brief(root, "OBPI-0.0.22-02-empty-registry", ["data/x.json"])
            obpi_files = {"OBPI-0.0.22-02-empty-registry": brief}
            result = check_product_proof("ADR-0.0.22", obpi_files, root)
            self.assertFalse(result.success)
            self.assertEqual(result.obpi_proofs[0].proof_type, "MISSING")


class TestGlobAllowedPathsExpansion(unittest.TestCase):
    """Glob entries in ALLOWED PATHS expand to concrete files before classification (GHI #363)."""

    def _make_project(self, tmp: str) -> Path:
        root = Path(tmp)
        (root / "docs" / "user").mkdir(parents=True)
        (root / "src" / "gzkit").mkdir(parents=True)
        (root / "tests" / "governance").mkdir(parents=True)
        return root

    def _make_brief(self, root: Path, obpi_id: str, allowed_paths: list[str]) -> Path:
        brief_dir = root / "briefs"
        brief_dir.mkdir(exist_ok=True)
        brief_path = brief_dir / f"{obpi_id}.md"
        paths_section = "\n".join(f"- `{p}`" for p in allowed_paths)
        brief_path.write_text(
            f"# {obpi_id}\n\n## ALLOWED PATHS\n\n{paths_section}\n\n## REQUIREMENTS\n",
            encoding="utf-8",
        )
        return brief_path

    def test_test_glob_expands_to_real_test_file(self) -> None:
        """`tests/governance/**` expands to a real `.py` file under that dir."""
        with tempfile.TemporaryDirectory() as tmp:
            root = self._make_project(tmp)
            (root / "docs" / "user" / "runbook.md").write_text("Empty.\n", encoding="utf-8")
            test_file = root / "tests" / "governance" / "test_foo.py"
            test_file.write_text(
                "import unittest\nclass T(unittest.TestCase):\n"
                "    def test_x(self):\n        self.assertTrue(True)\n" + "# " + "x" * 200,
                encoding="utf-8",
            )
            brief = self._make_brief(root, "OBPI-0.0.22-01-glob", ["tests/governance/**"])
            obpi_files = {"OBPI-0.0.22-01-glob": brief}
            result = check_product_proof("ADR-0.0.22", obpi_files, root)
            self.assertTrue(result.success)
            self.assertEqual(result.obpi_proofs[0].proof_type, "test_evidence")

    def test_src_glob_expands_to_real_module_with_docstring(self) -> None:
        """`src/gzkit/models/**` expands to a real `.py` file inside that dir."""
        with tempfile.TemporaryDirectory() as tmp:
            root = self._make_project(tmp)
            (root / "src" / "gzkit" / "models").mkdir(parents=True)
            (root / "docs" / "user" / "runbook.md").write_text("Empty.\n", encoding="utf-8")
            module = root / "src" / "gzkit" / "models" / "frontmatter.py"
            module.write_text(
                'def public_function():\n    """Public function with docstring."""\n    pass\n',
                encoding="utf-8",
            )
            brief = self._make_brief(root, "OBPI-0.0.22-01-models-glob", ["src/gzkit/models/**"])
            obpi_files = {"OBPI-0.0.22-01-models-glob": brief}
            result = check_product_proof("ADR-0.0.22", obpi_files, root)
            self.assertTrue(result.success)
            self.assertEqual(result.obpi_proofs[0].proof_type, "docstring")


if __name__ == "__main__":
    unittest.main()
