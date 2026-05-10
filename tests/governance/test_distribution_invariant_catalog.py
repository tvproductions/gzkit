"""Structural tests for docs/governance/distribution_invariant_catalog.md.

Covers OBPI-0.0.31-03 REQ-01..08. Documentation-only OBPI; assertions verify
the catalog file's structural shape and required cross-references rather than
runtime behavior. Each REQ maps to one test method via the @covers decorator
so the ADR-0.0.25 REQ-coverage gate finds the canonical anchor.
"""

import re
import unittest
from pathlib import Path

from gzkit.traceability import covers

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_CATALOG = _PROJECT_ROOT / "docs" / "governance" / "distribution_invariant_catalog.md"
_TRUST_DOCTRINE = _PROJECT_ROOT / "docs" / "governance" / "trust-doctrine.md"
_GOVERNANCE_RUNBOOK = _PROJECT_ROOT / "docs" / "governance" / "governance_runbook.md"


class DistributionInvariantCatalogStructure(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.catalog_text = _CATALOG.read_text(encoding="utf-8")
        cls.trust_doctrine_text = _TRUST_DOCTRINE.read_text(encoding="utf-8")
        cls.runbook_text = _GOVERNANCE_RUNBOOK.read_text(encoding="utf-8")

    @covers("REQ-0.0.31-03-01")
    def test_catalog_exists_with_three_required_sections(self) -> None:
        self.assertTrue(_CATALOG.exists(), "catalog file must exist")
        self.assertIn(
            "trust-doctrine.md", self.catalog_text, "must cross-link to trust-doctrine.md"
        )
        self.assertIn("Worked Example", self.catalog_text, "must contain worked-example sections")
        self.assertTrue(
            "Decision Tree" in self.catalog_text or "Is This a T0 Breach" in self.catalog_text,
            "must contain a decision tree section",
        )

    @covers("REQ-0.0.31-03-02")
    def test_ghi_318_worked_example_with_all_four_failure_classes(self) -> None:
        self.assertIn("GHI #318", self.catalog_text, "worked example #1 must reference GHI #318")
        for marker in ("Failure Class A", "Failure Class B", "Failure Class C", "Failure Class D"):
            self.assertIn(marker, self.catalog_text, f"failure class section missing: {marker}")
        for obpi_link in (
            "OBPI-0.0.32-01",
            "OBPI-0.0.32-02",
            "OBPI-0.0.32-03",
            "OBPI-0.0.32-04",
            "OBPI-0.0.32-05",
            "OBPI-0.0.32-06",
            "OBPI-0.0.32-07",
        ):
            self.assertIn(
                obpi_link,
                self.catalog_text,
                f"failure class must forward-link to closing OBPI: {obpi_link}",
            )

    @covers("REQ-0.0.31-03-03")
    def test_chores_promotion_gap_worked_example(self) -> None:
        self.assertIn(
            "ADR-0.0.21", self.catalog_text, "worked example #2 must reference ADR-0.0.21"
        )
        self.assertIn(
            "operationally true before it was named",
            self.catalog_text.lower(),
            "must frame ADR-0.0.21 as 'T0 was operationally true before it was named'",
        )
        self.assertIn("chores", self.catalog_text.lower(), "must discuss chores promotion gap")

    @covers("REQ-0.0.31-03-04")
    def test_decision_tree_with_four_branches_and_recovery_actions(self) -> None:
        catalog_lower = self.catalog_text.lower()
        self.assertTrue(
            "decision tree" in catalog_lower or "is this a t0 breach" in catalog_lower,
            "decision tree section must be present",
        )
        for branch_keyword in ("ship in the wheel", "gz init", "baseline manifest", "validate"):
            self.assertIn(
                branch_keyword,
                catalog_lower,
                f"decision tree branch must mention: {branch_keyword}",
            )
        self.assertIn(
            "Recovery", self.catalog_text, "decision tree must include explicit Recovery actions"
        )

    @covers("REQ-0.0.31-03-05")
    def test_forward_link_to_adr_0_0_32_and_back_link_from_trust_doctrine(self) -> None:
        self.assertIn("ADR-0.0.32", self.catalog_text, "catalog must forward-link to ADR-0.0.32")
        self.assertIn(
            "distribution_invariant_catalog.md",
            self.trust_doctrine_text,
            "trust-doctrine.md must back-link to the catalog (See also)",
        )

    @covers("REQ-0.0.31-03-06")
    def test_no_doctrine_prose_duplicates_trust_doctrine(self) -> None:
        self.assertIn(
            "references and applies the",
            self.catalog_text,
            "catalog must explicitly state it references rather than redefines the doctrine",
        )
        self.assertIn(
            "Doctrine source",
            self.catalog_text,
            "catalog must cite trust-doctrine.md as doctrine source",
        )

    @covers("REQ-0.0.31-03-07")
    def test_runbook_discoverability_entry_present(self) -> None:
        self.assertIn(
            "distribution_invariant_catalog.md",
            self.runbook_text,
            "governance_runbook.md must mention the catalog for discoverability",
        )

    @covers("REQ-0.0.31-03-08")
    def test_catalog_well_formed_for_validate_and_mkdocs_strict(self) -> None:
        """Structural preconditions for `gz validate --documents` and `mkdocs build --strict`.

        The actual gate runs are Stage 3 ARB receipts (`arb-step-mkdocs-*` and
        `gz validate --documents`); this in-process test asserts the structural
        invariants whose absence would break those gates: every internal
        markdown link must use a relative path that exists, and every anchor
        reference into trust-doctrine.md must match an actual heading there.
        Subprocess calls would violate `.gzkit/rules/tests.md` § Unit-tier
        contract (mocking required, <200ms target).
        """
        link_pattern = re.compile(r"\]\(([^)]+)\)")
        for match in link_pattern.finditer(self.catalog_text):
            target = match.group(1).split("#")[0]
            if not target or target.startswith(("http://", "https://", "mailto:")):
                continue
            resolved = (_CATALOG.parent / target).resolve()
            self.assertTrue(
                resolved.exists(),
                f"catalog link target does not exist: {target} (resolved: {resolved})",
            )
        anchor_match = re.search(r"trust-doctrine\.md#([a-z0-9-]+)", self.catalog_text)
        self.assertIsNotNone(anchor_match, "catalog must reference a trust-doctrine.md anchor")
        anchor = anchor_match.group(1) if anchor_match else ""
        heading_pattern = re.compile(r"^#{1,6}\s+(.+)$", re.MULTILINE)
        rendered_anchors: set[str] = set()
        for heading in heading_pattern.findall(self.trust_doctrine_text):
            normalized = heading.lower()
            normalized = re.sub(r"[^\w\s-]", "", normalized, flags=re.UNICODE)
            normalized = re.sub(r"\s+", "-", normalized.strip())
            normalized = re.sub(r"-{2,}", "-", normalized)
            rendered_anchors.add(normalized)
        self.assertIn(
            anchor,
            rendered_anchors,
            f"trust-doctrine.md does not contain anchor '#{anchor}' that catalog links to",
        )


if __name__ == "__main__":
    unittest.main()
