"""Tests for `gz validate --okf-conformance` (ADR-0.30.0 / OBPI-0.30.0-03).

@covers OBPI-0.30.0-03-okf-conformance-validator

REQ-derived (brief § Requirements FAIL-CLOSED), not derived from a run of the
implementation (`.gzkit/rules/tests.md` § "Tests assert semantics, not strings").
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from gzkit.governance.trust_audits.okf_conformance import audit_okf_conformance
from gzkit.traceability import covers

_VALID_INDEX = (
    "---\ntitle: Knowledge Index\ndescription: tracer.\ntype: index\n---\n\n# Knowledge Index\n"
)
_VALID_CONCEPT = (
    "---\ntitle: State Doctrine\ndescription: d.\ntype: doctrine\n---\n\n# State Doctrine\n"
)


def _bundle(root: Path, *, domain: str = "governance/knowledge") -> Path:
    """Create a minimal clean OKF bundle root and return it."""
    bundle = root / _GZKIT(domain)
    bundle.mkdir(parents=True, exist_ok=True)
    (bundle / "index.md").write_text(_VALID_INDEX, encoding="utf-8")
    (bundle / "state-doctrine.md").write_text(_VALID_CONCEPT, encoding="utf-8")
    return bundle


def _GZKIT(domain: str) -> str:
    return f".gzkit/{domain}"


class TestCleanBundle(unittest.TestCase):
    @covers("REQ-0.30.0-03-01")
    def test_clean_fixture_bundle_returns_no_errors(self) -> None:
        """A clean generated bundle yields zero findings (exit-0 semantics)."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _bundle(root)
            self.assertEqual(audit_okf_conformance(root), [])

    @covers("REQ-0.30.0-03-01")
    def test_real_repo_bundle_is_clean(self) -> None:
        """The real `.gzkit/governance/knowledge/` bundle conforms."""
        repo_root = Path(__file__).resolve().parents[2]
        self.assertTrue(
            (repo_root / ".gzkit/governance/knowledge/index.md").exists(),
            "the shipped OKF bundle is a repo artifact, not an optional fixture",
        )
        self.assertEqual(audit_okf_conformance(repo_root), [])


class TestMalformedBundle(unittest.TestCase):
    @covers("REQ-0.30.0-03-02")
    def test_unparseable_frontmatter_flags_file_and_field(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            bundle = _bundle(root)
            (bundle / "broken.md").write_text(
                "---\ntype: [unclosed\n---\n\n# broken\n", encoding="utf-8"
            )
            errors = audit_okf_conformance(root)
            self.assertTrue(errors, "expected a conformance error")
            err = errors[0]
            self.assertEqual(err.type, "okf_conformance")
            self.assertIn("broken.md", err.artifact)
            self.assertIn("frontmatter", err.message.lower())

    @covers("REQ-0.30.0-03-02")
    def test_empty_type_flags_file_and_field(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            bundle = _bundle(root)
            (bundle / "empty-type.md").write_text(
                '---\ntitle: x\ntype: ""\n---\n\n# x\n', encoding="utf-8"
            )
            errors = audit_okf_conformance(root)
            self.assertTrue(any("empty-type.md" in e.artifact for e in errors))
            offending = next(e for e in errors if "empty-type.md" in e.artifact)
            self.assertIn("type", offending.message.lower())

    @covers("REQ-0.30.0-03-02")
    def test_missing_type_flags_file_and_field(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            bundle = _bundle(root)
            (bundle / "no-type.md").write_text(
                "---\ntitle: x\ndescription: d.\n---\n\n# x\n", encoding="utf-8"
            )
            errors = audit_okf_conformance(root)
            self.assertTrue(any("no-type.md" in e.artifact for e in errors))
            offending = next(e for e in errors if "no-type.md" in e.artifact)
            self.assertIn("type", offending.message.lower())

    @covers("REQ-0.30.0-03-02")
    def test_concept_doc_with_no_frontmatter_block_flags_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            bundle = _bundle(root)
            # A non-reserved concept doc with no `---` delimiter at all.
            (bundle / "bare.md").write_text("# Bare\n\nNo frontmatter.\n", encoding="utf-8")
            errors = audit_okf_conformance(root)
            self.assertTrue(any("bare.md" in e.artifact for e in errors))
            offending = next(e for e in errors if "bare.md" in e.artifact)
            self.assertIn("frontmatter", offending.message.lower())

    @covers("REQ-0.30.0-03-02")
    def test_all_concept_docs_malformed_still_detected_via_index(self) -> None:
        """A bundle whose concept docs ALL lost their `type` is still recognized
        (via the type-bearing reserved index.md) and its bad docs flagged — the
        worst-malformed case must not go invisible."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            bundle = root / _GZKIT("governance/knowledge")
            bundle.mkdir(parents=True, exist_ok=True)
            (bundle / "index.md").write_text(_VALID_INDEX, encoding="utf-8")
            # Every concept doc stripped of its required `type`.
            (bundle / "a.md").write_text("---\ntitle: A\n---\n\n# A\n", encoding="utf-8")
            (bundle / "b.md").write_text("# B\n\nno frontmatter\n", encoding="utf-8")
            errors = audit_okf_conformance(root)
            flagged = {e.artifact for e in errors}
            self.assertTrue(any("a.md" in f for f in flagged))
            self.assertTrue(any("b.md" in f for f in flagged))

    @covers("REQ-0.30.0-03-02")
    def test_malformed_reserved_index_flags_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            bundle = _bundle(root)
            # Overwrite the reserved index.md with unparseable frontmatter; a
            # valid concept doc remains so the dir is still a detected bundle.
            (bundle / "index.md").write_text(
                "---\ntype: [unclosed\n---\n\n# idx\n", encoding="utf-8"
            )
            errors = audit_okf_conformance(root)
            self.assertTrue(any("index.md" in e.artifact for e in errors))


class TestGeneratedBundleOnly(unittest.TestCase):
    @covers("REQ-0.30.0-03-03")
    def test_authored_source_doc_not_flagged(self) -> None:
        """A source doc under docs/ with no OKF frontmatter is NOT flagged."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _bundle(root)  # clean bundle present
            src = root / "docs/governance"
            src.mkdir(parents=True, exist_ok=True)
            (src / "state-doctrine.md").write_text(
                "# State Doctrine\n\nNo frontmatter here.\n", encoding="utf-8"
            )
            self.assertEqual(audit_okf_conformance(root), [])

    @covers("REQ-0.30.0-03-03")
    def test_domain_named_root_other_than_knowledge(self) -> None:
        """Detection is structural, not keyed to the `knowledge` folder name."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _bundle(root, domain="sales/catalog")
            # malformed concept in the differently-named domain root is flagged
            bundle = root / ".gzkit/sales/catalog"
            (bundle / "bad.md").write_text("---\ntitle: x\n---\n\n# x\n", encoding="utf-8")
            errors = audit_okf_conformance(root)
            self.assertTrue(any("bad.md" in e.artifact for e in errors))

    @covers("REQ-0.30.0-03-03")
    def test_no_bundle_returns_no_errors(self) -> None:
        """A project with no OKF bundle yields zero findings."""
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(audit_okf_conformance(Path(tmp)), [])


if __name__ == "__main__":
    unittest.main()
