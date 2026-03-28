"""Tests for product proof gate in quality module."""

import tempfile
import textwrap
import unittest
from pathlib import Path

from gzkit.quality import (
    ObpiProofStatus,
    _check_command_doc_proof,
    _check_docstring_proof,
    _check_runbook_proof,
    _extract_allowed_paths,
    _extract_obpi_slug,
    check_product_proof,
)


class TestExtractAllowedPaths(unittest.TestCase):
    """Tests for _extract_allowed_paths."""

    def test_extracts_paths_from_brief(self) -> None:
        brief = textwrap.dedent("""\
            ## OBJECTIVE

            Do something useful.

            ## ALLOWED PATHS

            - `src/gzkit/quality.py`
            - `src/gzkit/cli.py`
            - `tests/test_product_proof.py`
            - `docs/user/commands/closeout.md`

            ## REQUIREMENTS
            """)
        paths = _extract_allowed_paths(brief)
        self.assertEqual(
            paths,
            [
                "src/gzkit/quality.py",
                "src/gzkit/cli.py",
                "tests/test_product_proof.py",
                "docs/user/commands/closeout.md",
            ],
        )

    def test_no_allowed_paths_section(self) -> None:
        brief = "## OBJECTIVE\n\nDo something.\n"
        self.assertEqual(_extract_allowed_paths(brief), [])

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

    def test_standard_id(self) -> None:
        self.assertEqual(
            _extract_obpi_slug("OBPI-0.23.0-02-product-proof-gate"),
            "product-proof-gate",
        )

    def test_short_id(self) -> None:
        self.assertEqual(_extract_obpi_slug("OBPI-0.1.0-01"), "OBPI-0.1.0-01")


class TestCheckRunbookProof(unittest.TestCase):
    """Tests for _check_runbook_proof."""

    def test_id_match(self) -> None:
        runbook = "See OBPI-0.23.0-02 for details.\n"
        self.assertTrue(_check_runbook_proof("OBPI-0.23.0-02", "product-proof-gate", runbook))

    def test_slug_keyword_match(self) -> None:
        runbook = "The product proof gate validates documentation.\n"
        self.assertTrue(_check_runbook_proof("OBPI-0.23.0-02", "product-proof-gate", runbook))

    def test_no_match(self) -> None:
        runbook = "Nothing relevant here.\n"
        self.assertFalse(_check_runbook_proof("OBPI-0.23.0-02", "product-proof-gate", runbook))

    def test_case_insensitive_slug(self) -> None:
        runbook = "The Product Proof Gate is important.\n"
        self.assertTrue(_check_runbook_proof("OBPI-0.23.0-02", "product-proof-gate", runbook))


class TestCheckCommandDocProof(unittest.TestCase):
    """Tests for _check_command_doc_proof."""

    def test_existing_doc_with_content(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            doc_dir = root / "docs" / "user" / "commands"
            doc_dir.mkdir(parents=True)
            doc = doc_dir / "closeout.md"
            doc.write_text("# gz closeout\n\n" + "x" * 200, encoding="utf-8")

            allowed = ["docs/user/commands/closeout.md", "src/gzkit/cli.py"]
            self.assertTrue(_check_command_doc_proof(allowed, root))

    def test_missing_doc_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            allowed = ["docs/user/commands/closeout.md"]
            self.assertFalse(_check_command_doc_proof(allowed, root))

    def test_empty_doc(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            doc_dir = root / "docs" / "user" / "commands"
            doc_dir.mkdir(parents=True)
            doc = doc_dir / "closeout.md"
            doc.write_text("# Title\n", encoding="utf-8")

            allowed = ["docs/user/commands/closeout.md"]
            self.assertFalse(_check_command_doc_proof(allowed, root))

    def test_no_command_docs_in_allowed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            allowed = ["src/gzkit/quality.py"]
            self.assertFalse(_check_command_doc_proof(allowed, root))


class TestCheckDocstringProof(unittest.TestCase):
    """Tests for _check_docstring_proof."""

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

    def test_no_docstrings(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            src_dir = root / "src" / "gzkit"
            src_dir.mkdir(parents=True)
            py_file = src_dir / "quality.py"
            py_file.write_text("def run():\n    pass\n", encoding="utf-8")
            allowed = ["src/gzkit/quality.py"]
            self.assertFalse(_check_docstring_proof(allowed, root))

    def test_non_src_paths_ignored(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            allowed = ["tests/test_foo.py"]
            self.assertFalse(_check_docstring_proof(allowed, root))

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


class TestObpiProofStatus(unittest.TestCase):
    """Tests for ObpiProofStatus model."""

    def test_has_proof_runbook(self) -> None:
        status = ObpiProofStatus(obpi_id="OBPI-0.1.0-01", runbook_found=True)
        self.assertTrue(status.has_proof)
        self.assertEqual(status.proof_type, "runbook")

    def test_has_proof_command_doc(self) -> None:
        status = ObpiProofStatus(obpi_id="OBPI-0.1.0-01", command_doc_found=True)
        self.assertTrue(status.has_proof)
        self.assertEqual(status.proof_type, "command_doc")

    def test_has_proof_docstring(self) -> None:
        status = ObpiProofStatus(obpi_id="OBPI-0.1.0-01", docstring_found=True)
        self.assertTrue(status.has_proof)
        self.assertEqual(status.proof_type, "docstring")

    def test_missing(self) -> None:
        status = ObpiProofStatus(obpi_id="OBPI-0.1.0-01")
        self.assertFalse(status.has_proof)
        self.assertEqual(status.proof_type, "MISSING")

    def test_priority_order(self) -> None:
        """Runbook takes priority over command_doc over docstring."""
        status = ObpiProofStatus(
            obpi_id="OBPI-0.1.0-01",
            runbook_found=True,
            command_doc_found=True,
            docstring_found=True,
        )
        self.assertEqual(status.proof_type, "runbook")


class TestCheckProductProof(unittest.TestCase):
    """Integration tests for check_product_proof."""

    def _make_project(self, tmp: str) -> Path:
        root = Path(tmp)
        (root / "docs" / "user").mkdir(parents=True)
        (root / "docs" / "user" / "commands").mkdir(parents=True)
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
                ["src/gzkit/pipeline.py", "docs/user/commands/pipeline.md"],
            )
            obpi_files = {"OBPI-0.1.0-01-pipeline-check": brief}
            result = check_product_proof("ADR-0.1.0", obpi_files, root)
            self.assertTrue(result.success)
            self.assertEqual(result.missing_count, 0)
            self.assertEqual(result.obpi_proofs[0].proof_type, "runbook")

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

    def test_empty_obpi_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = self._make_project(tmp)
            result = check_product_proof("ADR-0.1.0", {}, root)
            self.assertTrue(result.success)
            self.assertEqual(result.missing_count, 0)
            self.assertEqual(result.obpi_proofs, [])

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


if __name__ == "__main__":
    unittest.main()
