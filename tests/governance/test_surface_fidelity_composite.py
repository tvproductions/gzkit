"""Tests for OBPI-0.0.33-05 surface-fidelity composite scope and CI wiring.

Coverage:
    REQ-0.0.33-05-01 — `gz validate --surface-fidelity` invokes the four
        validators in declared order and aggregates errors.
    REQ-0.0.33-05-02 — Exit code is worst-of-four; never lower than highest
        constituent exit code.
    REQ-0.0.33-05-03 — `gz check` includes surface-fidelity step in its
        aggregate pipeline.
    REQ-0.0.33-05-04 — `.pre-commit-config.yaml` hooks invoke the cheap
        3-validator subset (not including scenario-reachability).
    REQ-0.0.33-05-05 — `docs/user/manpages/validate.md` documents
        `--surface-fidelity`.
    REQ-0.0.33-05-06 — `validate_surface_fidelity` is importable and callable.
"""

from __future__ import annotations

import pathlib
import unittest
from unittest.mock import patch

from gzkit.core.validation_rules import ValidationError
from gzkit.traceability import covers
from tests.governance.common import QuietAdvisoriesMixin

# REQ-0.0.33-05-06: this import will fail at test-run time (TDD Red)
# until implementation lands.
try:
    from gzkit.governance.trust_audits import validate_surface_fidelity
except ImportError:
    # Placeholder for TDD Red phase — test will fail with ImportError
    validate_surface_fidelity = None  # type: ignore


_PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[2]


class TestValidateSurfaceFidelityImportable(QuietAdvisoriesMixin):
    """Importability tests for the composite validator."""

    @covers("REQ-0.0.33-05-06")
    def test_validate_surface_fidelity_is_callable(self) -> None:
        """@covers REQ-0.0.33-05-06

        validate_surface_fidelity must be importable and callable.
        """
        self.assertIsNotNone(
            validate_surface_fidelity,
            "validate_surface_fidelity not importable — TDD Red expected",
        )
        self.assertTrue(
            callable(validate_surface_fidelity),
            "validate_surface_fidelity must be callable",
        )


class TestSurfaceFidelityComposite(QuietAdvisoriesMixin):
    """Composite validation tests for surface-fidelity scope."""

    @covers("REQ-0.0.33-05-01")
    def test_all_live_validators_fire_in_order(self) -> None:
        """@covers REQ-0.0.33-05-01

        Composite must invoke bullet_retention, surface_weight and
        pointer_integrity in that declared order and aggregate their errors.
        Invariant 4 (scenario reachability) was retired 2026-07-25 —
        ADR-0.0.33 § Amendment (2026-07-25).
        """
        with (
            patch("gzkit.governance.trust_audits.validate_bullet_retention") as mock_bullet,
            patch("gzkit.governance.trust_audits.validate_surface_weight") as mock_surface,
            patch("gzkit.governance.trust_audits.validate_pointer_integrity") as mock_pointer,
        ):
            # Setup return values: each validator returns some errors
            mock_bullet.return_value = [
                ValidationError(
                    type="bullet_retention",
                    artifact="AGENTS.md",
                    message="missing bullet",
                )
            ]
            mock_surface.return_value = [
                ValidationError(
                    type="surface_weight",
                    artifact="CLAUDE.md",
                    message="surface too heavy",
                )
            ]
            mock_pointer.return_value = []

            result = validate_surface_fidelity(_PROJECT_ROOT)

            # Verify each was called exactly once
            self.assertEqual(mock_bullet.call_count, 1)
            self.assertEqual(mock_surface.call_count, 1)
            self.assertEqual(mock_pointer.call_count, 1)

            # Assert errors are aggregated
            self.assertEqual(len(result), 2)
            self.assertTrue(
                any(e.type == "bullet_retention" for e in result),
                "bullet_retention error not aggregated",
            )
            self.assertTrue(
                any(e.type == "surface_weight" for e in result),
                "surface_weight error not aggregated",
            )

    @covers("REQ-0.0.33-05-02")
    def test_exit_code_worst_of_constituents(self) -> None:
        """@covers REQ-0.0.33-05-02

        Composite exit code must be the worst (highest) of its constituent
        validators. If any constituent indicates a policy breach (exit 3),
        the composite must also indicate exit 3.
        """
        with (
            patch("gzkit.governance.trust_audits.validate_bullet_retention") as mock_bullet,
            patch("gzkit.governance.trust_audits.validate_surface_weight") as mock_surface,
            patch("gzkit.governance.trust_audits.validate_pointer_integrity") as mock_pointer,
        ):
            # Scenario: bullet_retention returns an error (indicating breach)
            # others return clean. Composite should return that error.
            mock_bullet.return_value = [
                ValidationError(
                    type="bullet_retention",
                    artifact="AGENTS.md",
                    message="policy breach",
                )
            ]
            mock_surface.return_value = []
            mock_pointer.return_value = []

            result = validate_surface_fidelity(_PROJECT_ROOT)

            # The composite result must include the error from bullet_retention
            self.assertGreater(len(result), 0)
            self.assertTrue(
                any(e.type == "bullet_retention" for e in result),
                "composite must preserve error from constituent",
            )

    @covers("REQ-0.0.33-05-03")
    def test_gz_check_includes_surface_fidelity(self) -> None:
        """@covers REQ-0.0.33-05-03

        `gz check` must invoke `run_surface_fidelity_audit` as part of its
        default pipeline. Assert via introspection of _build_check_steps().
        """
        from gzkit.commands.quality import gz_check_cmd

        steps = gz_check_cmd.steps
        step_names = [name for name, _ in steps]

        # The step name should be something like "Surface fidelity"
        # (exact name TBD by implementation)
        self.assertTrue(
            any("surface" in name.lower() and "fidelity" in name.lower() for name in step_names),
            f"gz check must include a surface-fidelity step; got {step_names}",
        )

    @covers("REQ-0.0.33-05-04")
    def test_precommit_cheap_subset_registration(self) -> None:
        """@covers REQ-0.0.33-05-04

        `.pre-commit-config.yaml` MUST contain a hook invoking
        `uv run gz validate --bullet-retention --surface-weight --pointer-anchors`
        as a single CLI call. MUST NOT include `--scenario-reachability`.
        """
        precommit_path = _PROJECT_ROOT / ".pre-commit-config.yaml"
        self.assertTrue(precommit_path.is_file(), ".pre-commit-config.yaml not found")

        content = precommit_path.read_text(encoding="utf-8")

        # The cheap subset should be present
        self.assertIn(
            "--bullet-retention",
            content,
            ".pre-commit-config.yaml missing --bullet-retention flag",
        )
        self.assertIn(
            "--surface-weight",
            content,
            ".pre-commit-config.yaml missing --surface-weight flag",
        )
        self.assertIn(
            "--pointer-anchors",
            content,
            ".pre-commit-config.yaml missing --pointer-anchors flag",
        )

        # The expensive validator MUST NOT be in pre-commit
        # (it can be in gz validate --all but not in pre-commit)
        # Count lines with scenario-reachability to ensure no hook runs it
        lines_with_scenario = [
            line
            for line in content.split("\n")
            if "--scenario-reachability" in line and "entry:" in line
        ]
        self.assertEqual(
            len(lines_with_scenario),
            0,
            ".pre-commit-config.yaml MUST NOT invoke --scenario-reachability",
        )

    @covers("REQ-0.0.33-05-05")
    def test_validate_manpage_documents_surface_fidelity(self) -> None:
        """@covers REQ-0.0.33-05-05

        `docs/user/manpages/validate.md` MUST document `--surface-fidelity`.
        """
        manpage_path = _PROJECT_ROOT / "docs" / "user" / "manpages" / "validate.md"
        self.assertTrue(manpage_path.is_file(), "validate.md manpage not found")

        content = manpage_path.read_text(encoding="utf-8")

        self.assertIn(
            "--surface-fidelity",
            content,
            "validate.md must document --surface-fidelity flag",
        )


if __name__ == "__main__":
    unittest.main()
