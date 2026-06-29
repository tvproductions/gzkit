"""REQ-derived tests for the .gzkit/governance/knowledge/content-boundary.md doctrine doc.

OBPI-0.30.0-06: content-boundary doctrine authoring.

Assertions derive from brief Requirements (FAIL-CLOSED), not from a run of the
implementation (.gzkit/rules/tests.md § "Tests assert semantics, not strings").
"""

import unittest
from pathlib import Path

from gzkit.traceability import covers

_PROJECT_ROOT = Path(__file__).parents[2]
_DOCTRINE_DOC = _PROJECT_ROOT / ".gzkit" / "governance" / "knowledge" / "content-boundary.md"
_RUNBOOK = _PROJECT_ROOT / "docs" / "user" / "runbook.md"
_GOVERNANCE_RUNBOOK = _PROJECT_ROOT / "docs" / "governance" / "governance_runbook.md"

# Docs the doctrine itself NAMES as relocation candidates (must still exist at
# their docs/ home — the doctrine declares the move, this OBPI does not perform it).
_RELOCATION_CANDIDATE_DOCS = [
    Path("docs/governance/state-doctrine.md"),
    Path("docs/governance/trust-doctrine.md"),
    Path("docs/governance/agent-contract-rationale.md"),
    Path("docs/user/runbook.md"),
    Path("docs/governance/governance_runbook.md"),
]

_DOCTRINE_POINTER_PATH = ".gzkit/governance/knowledge/content-boundary.md"


def _lines_with(*needles: str) -> list[str]:
    """Return doctrine-doc lines containing ALL needles (case-insensitive).

    A semantic co-occurrence check: an inverted doctrine (one that bound the
    boundary the wrong way round) would NOT produce a single line carrying both
    sides of the relationship, so this fails where a bare substring check passes.
    """
    content = _DOCTRINE_DOC.read_text(encoding="utf-8").lower()
    needles_l = [n.lower() for n in needles]
    return [line for line in content.splitlines() if all(n in line for n in needles_l)]


class TestBoundaryDoctrineExists(unittest.TestCase):
    """REQ-0.30.0-06-01: doctrine file exists and states the .gzkit/ vs docs/ boundary."""

    @covers("REQ-0.30.0-06-01")
    def test_doctrine_file_exists(self) -> None:
        """content-boundary.md must exist under .gzkit/governance/knowledge/."""
        self.assertTrue(
            _DOCTRINE_DOC.exists(),
            f"Doctrine doc missing: {_DOCTRINE_DOC}",
        )

    @covers("REQ-0.30.0-06-01")
    def test_doctrine_binds_gzkit_to_core_canon(self) -> None:
        """Doctrine binds .gzkit/ to gzkit-core canon on the SAME statement.

        Asserts the boundary DIRECTION: a single line must tie `.gzkit/` to
        gzkit-core canon. A doctrine that placed canon under docs/ would fail.
        """
        self.assertTrue(
            _lines_with(".gzkit/", "canon"),
            "No statement binds .gzkit/ to gzkit-core canon — boundary direction unproven",
        )

    @covers("REQ-0.30.0-06-01")
    def test_doctrine_binds_docs_to_adopter_space(self) -> None:
        """Doctrine binds docs/ to adopter-authored content on the SAME statement.

        Asserts the other half of the boundary direction: a line must tie
        `docs/` to adopter ownership. An inverted doctrine would fail.
        """
        self.assertTrue(
            _lines_with("docs/", "adopter"),
            "No statement binds docs/ to adopter-authored content — boundary direction unproven",
        )

    @covers("REQ-0.30.0-06-01")
    def test_doctrine_states_okf_bundles_domain_named_not_format_named(self) -> None:
        """Doctrine states OKF bundles are domain-named AND negates format-naming.

        Bare presence of 'domain' is insufficient; the REQ is the contrast
        (domain-named, NOT format-named / okf/ namespace).
        """
        self.assertTrue(
            _lines_with("domain-named", "format-named"),
            "Doctrine must state OKF bundles are domain-named, NOT format-named",
        )


class TestBoundaryDoctrineDeclaresPhase(unittest.TestCase):
    """REQ-0.30.0-06-02: doctrine declares phased relocation and states migration NOT performed."""

    @covers("REQ-0.30.0-06-02")
    def test_doctrine_declares_relocation_is_phased(self) -> None:
        """Doctrine ties 'phased' to the docs/→.gzkit/ relocation, not stray text.

        Asserts 'phased' co-occurs with 'relocation' on one statement, so the
        word is load-bearing for the migration claim — not matched incidentally.
        """
        self.assertTrue(
            _lines_with("phased", "relocation"),
            "Doctrine must declare the docs/→.gzkit/ RELOCATION as phased",
        )

    @covers("REQ-0.30.0-06-02")
    def test_doctrine_states_migration_not_performed_under_adr(self) -> None:
        """Doctrine states the migration is NOT performed under ADR-0.30.0.

        Asserts 'not', 'performed', and 'adr-0.30.0' co-occur on one statement —
        a doc that merely MENTIONED ADR-0.30.0 elsewhere would fail this.
        """
        self.assertTrue(
            _lines_with("not", "performed", "adr-0.30.0"),
            "Doctrine must state explicitly that migration is NOT performed under ADR-0.30.0",
        )


class TestNoDocsCanonRelocated(unittest.TestCase):
    """REQ-0.30.0-06-03: no docs/ core-canon files were relocated, moved, or deleted."""

    @covers("REQ-0.30.0-06-03")
    def test_relocation_candidate_docs_still_present_and_nonempty(self) -> None:
        """The docs/ files the doctrine NAMES as relocation candidates still exist.

        Binds the negative invariant to the doctrine's own claim: it declares
        these would move 'later' — so they MUST still be at their docs/ home now,
        and non-empty (a relocated-then-stubbed file would be caught by size).
        """
        for rel in _RELOCATION_CANDIDATE_DOCS:
            path = _PROJECT_ROOT / rel
            self.assertTrue(
                path.exists(),
                f"Core-canon file was relocated or deleted by this OBPI: {rel}",
            )
            self.assertGreater(
                path.stat().st_size,
                0,
                f"Core-canon file was emptied (relocation stub) by this OBPI: {rel}",
            )


class TestRunbooksPointToDoctrine(unittest.TestCase):
    """REQ-0.30.0-06-04: runbooks point to the content-boundary doctrine doc."""

    @covers("REQ-0.30.0-06-04")
    def test_user_runbook_points_to_doctrine_path(self) -> None:
        """docs/user/runbook.md names the full doctrine-doc PATH, not just a word."""
        content = _RUNBOOK.read_text(encoding="utf-8")
        self.assertIn(
            _DOCTRINE_POINTER_PATH,
            content,
            f"docs/user/runbook.md must point to {_DOCTRINE_POINTER_PATH}",
        )

    @covers("REQ-0.30.0-06-04")
    def test_governance_runbook_points_to_doctrine_path(self) -> None:
        """governance_runbook.md names the full doctrine-doc PATH, not just a word."""
        content = _GOVERNANCE_RUNBOOK.read_text(encoding="utf-8")
        self.assertIn(
            _DOCTRINE_POINTER_PATH,
            content,
            f"docs/governance/governance_runbook.md must point to {_DOCTRINE_POINTER_PATH}",
        )
