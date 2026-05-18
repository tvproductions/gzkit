"""Tests for HistoricalAttestationWaiver and HistoricalAttestationWaiverFile models.

Tests derive from OBPI-0.0.36-04 REQ-0.0.36-04-06: frozen mutations, extra-field
rejection, and required-field validation for the Pydantic models.

Uses gzkit.models.historical_waiver (will be written in the GREEN phase).
"""

from __future__ import annotations

import unittest

from gzkit.models.historical_waiver import (
    HistoricalAttestationWaiver,
    HistoricalAttestationWaiverFile,
)
from pydantic import ValidationError

from gzkit.traceability import covers


class TestHistoricalAttestationWaiverFrozen(unittest.TestCase):
    """Frozen-mutation and extra-field rejection for HistoricalAttestationWaiver."""

    @covers("REQ-0.0.36-04-06")
    def test_waiver_frozen_mutation_raises(self) -> None:
        """Attempt to mutate a frozen HistoricalAttestationWaiver post-construction."""
        waiver = HistoricalAttestationWaiver(
            receipt_id="arb-ruff-12345",
            obpi_id="OBPI-0.0.36-04",
            deprecated_shape="attestation_requirement: optional",
            rationale="Pre-cutoff self-close receipt.",
            added_under="OBPI-0.0.36-04-historical-self-close-waivers",
        )
        with self.assertRaises(ValidationError):
            waiver.receipt_id = "different-id"  # type: ignore[misc]

    @covers("REQ-0.0.36-04-06")
    def test_waiver_extra_field_forbidden(self) -> None:
        """Extra fields in HistoricalAttestationWaiver construction raise ValidationError."""
        with self.assertRaises(ValidationError):
            HistoricalAttestationWaiver(
                receipt_id="arb-ruff-12345",
                obpi_id="OBPI-0.0.36-04",
                deprecated_shape="attestation_requirement: optional",
                rationale="Pre-cutoff self-close receipt.",
                added_under="OBPI-0.0.36-04-historical-self-close-waivers",
                extra_field="should fail",  # type: ignore[call-arg]
            )

    @covers("REQ-0.0.36-04-06")
    def test_waiver_required_field_absence_raises(self) -> None:
        """Omitting receipt_id from HistoricalAttestationWaiver raises ValidationError."""
        with self.assertRaises(ValidationError):
            HistoricalAttestationWaiver(
                obpi_id="OBPI-0.0.36-04",
                deprecated_shape="attestation_requirement: optional",
                rationale="Pre-cutoff self-close receipt.",
                added_under="OBPI-0.0.36-04-historical-self-close-waivers",
            )  # type: ignore[call-arg]

    @covers("REQ-0.0.36-04-01")
    @covers("REQ-0.0.36-04-06")
    def test_valid_waiver_constructs_ok(self) -> None:
        """Valid HistoricalAttestationWaiver construction with all five required fields succeeds."""
        waiver = HistoricalAttestationWaiver(
            receipt_id="arb-ruff-12345",
            obpi_id="OBPI-0.0.36-04",
            deprecated_shape="attestation_requirement: optional",
            rationale="Pre-cutoff self-close receipt.",
            added_under="OBPI-0.0.36-04-historical-self-close-waivers",
        )
        # Verify all five required fields are present and accessible
        self.assertEqual(waiver.receipt_id, "arb-ruff-12345")
        self.assertEqual(waiver.obpi_id, "OBPI-0.0.36-04")
        self.assertEqual(waiver.deprecated_shape, "attestation_requirement: optional")
        self.assertEqual(waiver.rationale, "Pre-cutoff self-close receipt.")
        self.assertEqual(waiver.added_under, "OBPI-0.0.36-04-historical-self-close-waivers")


class TestHistoricalAttestationWaiverFile(unittest.TestCase):
    """Frozen and extra-forbid enforcement for HistoricalAttestationWaiverFile."""

    @covers("REQ-0.0.36-04-06")
    def test_waiver_file_extra_field_forbidden(self) -> None:
        """Extra fields in HistoricalAttestationWaiverFile raise ValidationError."""
        with self.assertRaises(ValidationError):
            HistoricalAttestationWaiverFile(
                waivers=[],
                extra_field="should fail",  # type: ignore[call-arg]
            )

    @covers("REQ-0.0.36-04-06")
    def test_waiver_file_valid_constructs_ok(self) -> None:
        """Valid HistoricalAttestationWaiverFile with waivers list constructs."""
        waiver = HistoricalAttestationWaiver(
            receipt_id="arb-ruff-12345",
            obpi_id="OBPI-0.0.36-04",
            deprecated_shape="attestation_requirement: optional",
            rationale="Pre-cutoff self-close receipt.",
            added_under="OBPI-0.0.36-04-historical-self-close-waivers",
        )
        waiver_file = HistoricalAttestationWaiverFile(waivers=[waiver])
        self.assertEqual(len(waiver_file.waivers), 1)
        self.assertEqual(waiver_file.waivers[0].receipt_id, "arb-ruff-12345")


if __name__ == "__main__":
    unittest.main()
