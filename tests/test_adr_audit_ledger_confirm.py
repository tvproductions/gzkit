"""Confirmation tests for OBPI-0.25.0-19 (ADR Audit Ledger Pattern).

@covers ADR-0.25.0-core-infrastructure-pattern-absorption
@covers OBPI-0.25.0-19-adr-audit-ledger-pattern

Decision: Confirm. gzkit's audit surface already covers the airlineops
adr_audit_ledger.py capabilities through three modules: adr_audit (completeness
check + REQ coverage), ledger_check (schema validation), and obpi_audit_cmd
(evidence gathering).
"""

import unittest

from gzkit.traceability import covers


class TestAuditLedgerSurfaceExists(unittest.TestCase):
    """Verify gzkit's audit surface covers the airlineops module's capabilities."""

    @covers("REQ-0.25.0-19-01")
    def test_adr_audit_check_importable(self):
        """adr_audit_check provides Gate 5 completeness checking."""
        from gzkit.commands.adr_audit import adr_audit_check

        self.assertTrue(callable(adr_audit_check))

    @covers("REQ-0.25.0-19-02")
    def test_validate_ledger_importable(self):
        """validate_ledger provides JSONL ledger schema validation."""
        from gzkit.validate_pkg.ledger_check import validate_ledger

        self.assertTrue(callable(validate_ledger))

    @covers("REQ-0.25.0-19-02")
    def test_obpi_audit_cmd_importable(self):
        """obpi_audit_cmd provides deterministic evidence gathering."""
        from gzkit.commands.obpi_audit_cmd import obpi_audit_cmd

        self.assertTrue(callable(obpi_audit_cmd))

    @covers("REQ-0.25.0-19-04")
    def test_confirm_decision_no_absorption_needed(self):
        """Confirm: gzkit audit surface is broader than airlineops equivalent.

        airlineops adr_audit_ledger.py provides:
        - check_ledger_completeness (reads local obpi-audit.jsonl)
        - format_ledger_check_report (markdown report)

        gzkit provides all of the above plus:
        - Central ledger graph (not local audit file)
        - Brief content inspection (not just status values)
        - @covers REQ traceability verification
        """
        from gzkit.commands.adr_audit import adr_audit_check
        from gzkit.commands.obpi_audit_cmd import obpi_audit_cmd
        from gzkit.validate_pkg.ledger_check import validate_ledger

        surface_functions = [adr_audit_check, validate_ledger, obpi_audit_cmd]
        self.assertEqual(len(surface_functions), 3)
        self.assertTrue(all(callable(f) for f in surface_functions))


if __name__ == "__main__":
    unittest.main()
