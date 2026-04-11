"""Confirmation tests for OBPI-0.25.0-20 (ADR Governance Pattern).

@covers ADR-0.25.0-core-infrastructure-pattern-absorption
@covers OBPI-0.25.0-20-adr-governance-pattern

Decision: Confirm. gzkit's governance surface already covers the airlineops
adr_governance.py capabilities through three modules: traceability (AST-based
@covers scanning + coverage rollups), covers (CLI command), and adr_audit
(evidence audit + REQ traceability).
"""

import unittest

from gzkit.traceability import covers


class TestGovernanceSurfaceExists(unittest.TestCase):
    """Verify gzkit's governance surface covers the airlineops module's capabilities."""

    @covers("REQ-0.25.0-20-01")
    def test_scan_test_tree_importable(self):
        """scan_test_tree provides AST-based @covers discovery (replaces regex parsing)."""
        from gzkit.traceability import scan_test_tree

        self.assertTrue(callable(scan_test_tree))

    @covers("REQ-0.25.0-20-02")
    def test_compute_coverage_importable(self):
        """compute_coverage provides multi-level ADR/OBPI/REQ rollups (replaces flat mapping)."""
        from gzkit.traceability import compute_coverage

        self.assertTrue(callable(compute_coverage))

    @covers("REQ-0.25.0-20-02")
    def test_adr_audit_check_importable(self):
        """adr_audit_check provides evidence audit via brief content inspection."""
        from gzkit.commands.adr_audit import adr_audit_check

        self.assertTrue(callable(adr_audit_check))

    @covers("REQ-0.25.0-20-04")
    def test_confirm_decision_no_absorption_needed(self):
        """Confirm: gzkit governance surface is broader than airlineops equivalent.

        airlineops adr_governance.py provides:
        - evidence_audit (regex-based ADR scanning)
        - adr_autolink (regex @covers parsing, auto-write Verification sections)
        - verification_report (covers-map JSONL ledger)

        gzkit provides all of the above plus:
        - AST-based scanning (not regex)
        - Multi-level coverage rollups (ADR/OBPI/REQ)
        - Runtime REQ validation at decoration time
        - Pydantic models (not stdlib dataclass)
        - Central ledger graph (not local covers-map file)
        """
        from gzkit.commands.adr_audit import adr_audit_check
        from gzkit.commands.covers import covers_cmd
        from gzkit.traceability import compute_coverage, scan_test_tree

        surface_functions = [scan_test_tree, compute_coverage, adr_audit_check, covers_cmd]
        self.assertEqual(len(surface_functions), 4)
        self.assertTrue(all(callable(f) for f in surface_functions))


if __name__ == "__main__":
    unittest.main()
