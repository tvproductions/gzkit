"""Tests asserting gz validate --taxonomy accepts sparse/gapped foundation IDs.

REQ-0.0.57-01-01/02: ADR-0.0.17 and ADR-0.0.18 contain dated amendment blocks.
REQ-0.0.57-01-03: src/gzkit/trust_audits.py is audit-clean (no sequence-position).
REQ-0.0.57-01-04: gz validate --taxonomy accepts sparse/gapped foundation IDs.
REQ-0.0.57-01-05: src/gzkit/commands/plan.py unchanged (OBPI-02 boundary).
REQ-0.0.57-01-06: No existing foundation ADR was renamed or moved.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from gzkit.commands.plan import _next_available_foundation_semver
from gzkit.governance.trust_audits import audit_adr_taxonomy
from gzkit.traceability import covers

_PROJECT_ROOT = Path(__file__).parent.parent


def _make_foundation_adr(root: Path, semver: str, slug: str) -> None:
    adr_dir = root / "docs" / "design" / "adr" / "foundation" / f"ADR-{semver}-{slug}"
    adr_dir.mkdir(parents=True)
    adr_file = adr_dir / f"ADR-{semver}-{slug}.md"
    adr_file.write_text(
        f"---\n"
        f"id: ADR-{semver}-{slug}\n"
        f"status: Draft\n"
        f"kind: foundation\n"
        f"semver: {semver}\n"
        f"---\n\n"
        f"# ADR-{semver}: {slug}\n",
        encoding="utf-8",
    )


class TestNominalIdTaxonomyValidator(unittest.TestCase):
    """The taxonomy validator accepts sparse (gapped) foundation ADR IDs."""

    @covers("REQ-0.0.57-01-04")
    def test_sparse_foundation_ids_produce_no_taxonomy_errors(self) -> None:
        """Validator accepts 0.0.54, gap at 0.0.55, 0.0.56 without error."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            _make_foundation_adr(root, "0.0.54", "slug-a")
            # Intentional gap: 0.0.55 is absent — nominal semantics, not odometer
            _make_foundation_adr(root, "0.0.56", "slug-b")
            errors = audit_adr_taxonomy(root)
            self.assertEqual(errors, [], f"Expected no errors, got: {errors}")

    @covers("REQ-0.0.57-01-04")
    def test_nonconsecutive_foundation_ids_produce_no_taxonomy_errors(self) -> None:
        """Validator accepts 0.0.1, 0.0.5, 0.0.10 (large gaps) without error."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            _make_foundation_adr(root, "0.0.1", "slug-a")
            _make_foundation_adr(root, "0.0.5", "slug-b")
            _make_foundation_adr(root, "0.0.10", "slug-c")
            errors = audit_adr_taxonomy(root)
            self.assertEqual(errors, [], f"Expected no errors, got: {errors}")

    @covers("REQ-0.0.57-01-05")
    def test_plan_allocator_is_unchanged(self) -> None:
        """commands/plan.py _next_available_foundation_semver still uses max+1.

        This assertion confirms plan.py was not modified by OBPI-0.0.57-01.
        The nominal-allocator replacement is OBPI-0.0.57-02's surface.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            foundation = root / "docs" / "design" / "adr" / "foundation"
            adr_dir = foundation / "ADR-0.0.3-some-slug"
            adr_dir.mkdir(parents=True)
            result = _next_available_foundation_semver(foundation)
            self.assertEqual(result, "0.0.4", "max+1 allocator must remain unchanged")


class TestNominalIdDoctrineAmendments(unittest.TestCase):
    """ADR-0.0.17 and ADR-0.0.18 contain the nominal-ID amendment block."""

    @covers("REQ-0.0.57-01-01")
    def test_adr_0017_contains_amendment_block(self) -> None:
        """ADR-0.0.17 must contain a dated amendment section from ADR-0.0.57."""
        adr_path = (
            _PROJECT_ROOT
            / "docs/design/adr/foundation/ADR-0.0.17-adr-taxonomy-mechanical"
            / "ADR-0.0.17-adr-taxonomy-mechanical.md"
        )
        content = adr_path.read_text(encoding="utf-8")
        self.assertIn(
            "## Amendment 2026-05-23 — ADR-0.0.57",
            content,
            "ADR-0.0.17 must contain a dated amendment block from ADR-0.0.57",
        )
        self.assertIn(
            "nominal integer",
            content,
            "ADR-0.0.17 amendment must document the nominal-integer doctrine",
        )

    @covers("REQ-0.0.57-01-02")
    def test_adr_0018_contains_amendment_block(self) -> None:
        """ADR-0.0.18 must contain a dated amendment section from ADR-0.0.57."""
        adr_path = (
            _PROJECT_ROOT
            / "docs/design/adr/foundation/ADR-0.0.18-adr-taxonomy-doctrine"
            / "ADR-0.0.18-adr-taxonomy-doctrine.md"
        )
        content = adr_path.read_text(encoding="utf-8")
        self.assertIn(
            "## Amendment 2026-05-23 — ADR-0.0.57",
            content,
            "ADR-0.0.18 must contain a dated amendment block from ADR-0.0.57",
        )
        self.assertIn(
            "nominal integer",
            content,
            "ADR-0.0.18 amendment must document the nominal-integer doctrine",
        )

    @covers("REQ-0.0.57-01-03")
    def test_trust_audits_audit_annotation_present(self) -> None:
        """src/gzkit/trust_audits.py must record the ADR-0.0.57 audit finding."""
        trust_audits = _PROJECT_ROOT / "src" / "gzkit" / "trust_audits.py"
        self.assertTrue(trust_audits.exists(), "src/gzkit/trust_audits.py must exist")
        content = trust_audits.read_text(encoding="utf-8")
        self.assertIn(
            "ADR-0.0.57",
            content,
            "trust_audits.py must reference the ADR-0.0.57 audit",
        )
        self.assertIn(
            "sequence-position assumptions",
            content,
            "trust_audits.py must document the sequence-position audit finding",
        )

    @covers("REQ-0.0.57-01-06")
    def test_no_existing_foundation_adr_was_renamed(self) -> None:
        """ADR-0.0.17 and ADR-0.0.18 directories must remain unchanged in path."""
        adr_17 = _PROJECT_ROOT / "docs/design/adr/foundation/ADR-0.0.17-adr-taxonomy-mechanical"
        adr_18 = _PROJECT_ROOT / "docs/design/adr/foundation/ADR-0.0.18-adr-taxonomy-doctrine"
        self.assertTrue(
            adr_17.is_dir(),
            "ADR-0.0.17 directory must not be renamed/moved",
        )
        self.assertTrue(
            adr_18.is_dir(),
            "ADR-0.0.18 directory must not be renamed/moved",
        )


if __name__ == "__main__":
    unittest.main()
