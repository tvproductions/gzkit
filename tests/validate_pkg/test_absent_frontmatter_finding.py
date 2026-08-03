"""A canonical ADR with no frontmatter is a finding, not a pass (GHI #742).

``validate_document`` opened with ``if not frontmatter: return []`` under the
comment *"they are not governance documents"*. That premise is false for the
intent document of a canonical ADR package: four such ADRs carried no
frontmatter and ``gz validate --documents`` reported green over all of them.

This is the class GHI #483 already fixed once, for ``kind_invariance``, and
never generalized: **a validator that keys on a frontmatter field silently
exempts every artifact with no frontmatter — absence of the key reads as
absence of the obligation.**

The repair keys on **directory placement**, matching the GHI #483 precedent: a
canonical ADR package's intent document is the ``.md`` file named for its own
directory. Sidecars (closeout forms, briefs, audit and log files) legitimately
carry no frontmatter and stay exempt, so every assertion that a finding fires
is paired with a **negative control** proving the exemption still holds for
them. Without the controls these tests would keep passing if the new guard
degenerated into "flag everything".

The absent/malformed split is the GHI #736 tri-state reader's payoff: a
truncated block must not be reported as a missing one, because the two have
different repairs.
"""

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from gzkit.validate_pkg.document import (
    is_canonical_adr_intent_path,
    validate_document,
)

_ADR_ID = "ADR-0.9.9-sample-work"
_BODY = f"# {_ADR_ID}: Sample\n\n## Intent\n\nSample intent.\n"
_VALID_FRONTMATTER = (
    "---\n"
    f"id: {_ADR_ID}\n"
    "status: Validated\n"
    "semver: 0.9.9\n"
    "lane: heavy\n"
    "kind: feature\n"
    "parent: PRD-GZKIT-1.0.0\n"
    "date: 2026-03-15\n"
    "---\n\n"
)


def _package(tmp: Path) -> Path:
    """Create a canonical ADR package directory and return it."""
    pkg = tmp / _ADR_ID
    pkg.mkdir()
    return pkg


def _frontmatter_findings(errors: list) -> list[str]:
    return [e.message for e in errors if e.type == "frontmatter"]


class TestCanonicalAdrIntentPredicate(unittest.TestCase):
    """The predicate is directory placement, never a list of sidecar names."""

    def test_intent_document_is_the_file_named_for_its_package(self) -> None:
        pkg = Path("docs/design/adr/pre-release") / _ADR_ID
        self.assertTrue(is_canonical_adr_intent_path(pkg / f"{_ADR_ID}.md"))

    def test_sidecars_within_the_package_are_not_intent_documents(self) -> None:
        pkg = Path("docs/design/adr/pre-release") / _ADR_ID
        for sidecar in (
            pkg / "ADR-CLOSEOUT-FORM.md",
            pkg / "obpis" / "OBPI-0.9.9-01-thing.md",
            pkg / "briefs" / "OBPI-0.9.9-01-thing.md",
            pkg / "audit" / f"{_ADR_ID}.md",
            pkg / "logs" / f"{_ADR_ID}.md",
        ):
            with self.subTest(sidecar=sidecar.name):
                self.assertFalse(is_canonical_adr_intent_path(sidecar))

    def test_pool_adrs_are_flat_files_and_are_not_intent_documents(self) -> None:
        self.assertFalse(
            is_canonical_adr_intent_path(Path("docs/design/adr/pool/ADR-pool.some-slug.md"))
        )


class TestAbsentFrontmatterIsAFinding(unittest.TestCase):
    """The hole GHI #742 named: no frontmatter must not read as no obligation."""

    def test_canonical_adr_without_frontmatter_produces_a_finding(self) -> None:
        with TemporaryDirectory() as tmp:
            pkg = _package(Path(tmp))
            doc = pkg / f"{_ADR_ID}.md"
            doc.write_text(_BODY, encoding="utf-8")

            findings = _frontmatter_findings(validate_document(doc, "adr"))
            self.assertTrue(findings, "an ADR with no frontmatter must not validate clean")
            self.assertIn("absent", findings[0].lower())

    def test_negative_control_same_document_with_frontmatter_is_clean(self) -> None:
        """Only the frontmatter block differs from the failing case above."""
        with TemporaryDirectory() as tmp:
            pkg = _package(Path(tmp))
            doc = pkg / f"{_ADR_ID}.md"
            doc.write_text(_VALID_FRONTMATTER + _BODY, encoding="utf-8")

            self.assertEqual(_frontmatter_findings(validate_document(doc, "adr")), [])

    def test_negative_control_sidecar_without_frontmatter_stays_exempt(self) -> None:
        """Closeout forms legitimately carry no frontmatter; 79 exist on disk."""
        with TemporaryDirectory() as tmp:
            pkg = _package(Path(tmp))
            sidecar = pkg / "ADR-CLOSEOUT-FORM.md"
            sidecar.write_text(_BODY, encoding="utf-8")

            self.assertEqual(validate_document(sidecar, "adr"), [])

    def test_negative_control_non_adr_schema_without_frontmatter_stays_exempt(self) -> None:
        """The guard is scoped to ADR intent documents, not every markdown file."""
        with TemporaryDirectory() as tmp:
            doc = Path(tmp) / "notes.md"
            doc.write_text(_BODY, encoding="utf-8")

            self.assertEqual(validate_document(doc, "prd"), [])


class TestMalformedIsDistinguishedFromAbsent(unittest.TestCase):
    """GHI #736's tri-state reader is what makes this distinction possible."""

    def test_truncated_block_reports_malformed_rather_than_absent(self) -> None:
        """An opening `---` with no closing `---` is damage, not omission."""
        with TemporaryDirectory() as tmp:
            pkg = _package(Path(tmp))
            doc = pkg / f"{_ADR_ID}.md"
            doc.write_text(f"---\nid: {_ADR_ID}\nstatus: Validated\n\n{_BODY}", encoding="utf-8")

            findings = _frontmatter_findings(validate_document(doc, "adr"))
            self.assertTrue(findings)
            self.assertIn("malformed", findings[0].lower())
            self.assertNotIn("absent", findings[0].lower())

    def test_invisible_separator_prefix_reports_malformed(self) -> None:
        """A leading VT hides the block from some readers and not others."""
        with TemporaryDirectory() as tmp:
            pkg = _package(Path(tmp))
            doc = pkg / f"{_ADR_ID}.md"
            doc.write_text("\x0b" + _VALID_FRONTMATTER + _BODY, encoding="utf-8")

            findings = _frontmatter_findings(validate_document(doc, "adr"))
            self.assertTrue(findings)
            self.assertIn("malformed", findings[0].lower())


if __name__ == "__main__":
    unittest.main()
