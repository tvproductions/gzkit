"""Tests for attestation-routing predicates in `gzkit.commands.adr_audit`.

Covers OBPI-0.0.22-04: ``_requires_security_review_attestation`` and the
OR composition into ``_requires_human_obpi_attestation`` that closes the
``lite + feature + sensitivity:security`` self-close vector.
"""

from __future__ import annotations

import unittest

from gzkit.commands.adr_audit import (
    _requires_human_obpi_attestation,
    _requires_security_review_attestation,
)


def covers(target: str):  # noqa: D401
    """Identity decorator linking test to ADR/OBPI target for traceability."""

    def _identity(obj):  # type: ignore[no-untyped-def]
        return obj

    return _identity


@covers("OBPI-0.0.22-04")
class TestRequiresSecurityReviewAttestation(unittest.TestCase):
    """REQ-0.0.22-04-01 — predicate fires only on sensitivity: security."""

    @covers("REQ-0.0.22-04-01")
    def test_sensitivity_security_returns_true(self):
        self.assertTrue(_requires_security_review_attestation({"sensitivity": "security"}))

    @covers("REQ-0.0.22-04-01")
    def test_no_sensitivity_key_returns_false(self):
        self.assertFalse(_requires_security_review_attestation({"id": "OBPI-x.y.z-nn"}))

    @covers("REQ-0.0.22-04-01")
    def test_empty_frontmatter_returns_false(self):
        self.assertFalse(_requires_security_review_attestation({}))

    @covers("REQ-0.0.22-04-01")
    def test_none_returns_false(self):
        self.assertFalse(_requires_security_review_attestation(None))

    @covers("REQ-0.0.22-04-01")
    def test_other_sensitivity_value_returns_false(self):
        # The schema currently enumerates only "security"; future values must
        # not silently inherit security-grade attestation rigor.
        self.assertFalse(_requires_security_review_attestation({"sensitivity": "privacy"}))
        self.assertFalse(_requires_security_review_attestation({"sensitivity": ""}))

    @covers("REQ-0.0.22-04-01")
    def test_non_mapping_input_returns_false(self):
        # The predicate must tolerate odd inputs without crashing — the call
        # site reads frontmatter from arbitrary brief content.
        self.assertFalse(_requires_security_review_attestation("sensitivity: security"))  # type: ignore[arg-type]
        self.assertFalse(_requires_security_review_attestation(["sensitivity"]))  # type: ignore[arg-type]


@covers("OBPI-0.0.22-04")
class TestRequiresHumanObpiAttestationORComposition(unittest.TestCase):
    """REQ-0.0.22-04-02..04 — security axis ORs into existing predicate."""

    @covers("REQ-0.0.22-04-02")
    def test_lite_feature_security_brief_requires_attestation(self):
        # The defect this OBPI closes: a security-sensitive lite-feature brief
        # used to be self-closeable because the predicate did not see the
        # third axis.
        self.assertTrue(
            _requires_human_obpi_attestation(
                "ADR-0.1.0-some-feature",
                "lite",
                {"sensitivity": "security"},
            )
        )

    @covers("REQ-0.0.22-04-03")
    def test_lite_feature_no_sensitivity_remains_self_closeable(self):
        # Self-closeable baseline must be preserved when sensitivity is absent.
        self.assertFalse(
            _requires_human_obpi_attestation(
                "ADR-0.1.0-some-feature",
                "lite",
                {},
            )
        )

    @covers("REQ-0.0.22-04-04")
    def test_heavy_feature_no_sensitivity_still_required(self):
        # No regression of the heavy-lane branch.
        self.assertTrue(
            _requires_human_obpi_attestation(
                "ADR-0.1.0-some-feature",
                "heavy",
                {},
            )
        )

    @covers("REQ-0.0.22-04-04")
    def test_lite_foundation_no_sensitivity_still_required(self):
        # No regression of the foundation-kind branch.
        self.assertTrue(
            _requires_human_obpi_attestation(
                "ADR-0.0.99-some-foundation",
                "lite",
                {},
            )
        )

    @covers("REQ-0.0.22-04-02")
    def test_frontmatter_argument_is_optional_for_call_site_compat(self):
        # ADR-level callers (`adr_emit_receipt_cmd`) do not have per-brief
        # frontmatter. The two-argument call shape must keep working — the
        # third argument defaults to None and is treated as "no security axis."
        self.assertFalse(_requires_human_obpi_attestation("ADR-0.1.0-some-feature", "lite"))
        self.assertTrue(_requires_human_obpi_attestation("ADR-0.0.99-some-foundation", "lite"))

    @covers("REQ-0.0.22-04-02")
    def test_heavy_lane_security_brief_still_required(self):
        # The OR is additive: heavy-lane and security both flag attestation,
        # neither suppresses the other.
        self.assertTrue(
            _requires_human_obpi_attestation(
                "ADR-0.1.0-some-feature",
                "heavy",
                {"sensitivity": "security"},
            )
        )


@covers("OBPI-0.0.22-04")
class TestAgentsMatrixThirdAxis(unittest.TestCase):
    """REQ-0.0.22-04-06 — AGENTS.md matrix is the readable projection."""

    @covers("REQ-0.0.22-04-06")
    def test_agents_md_matrix_names_third_axis(self):
        # Verify the readable projection of the predicate exists at the
        # canonical surface and names the third (sensitivity) axis,
        # cites the source-of-truth function, and names the security
        # sensitivity axis as a gate-firing factor.
        #
        # ADR-0.0.36 collapsed the old Lane & Kind & Sensitivity Attestation
        # Matrix to a universal attestation rule. The readable projection is
        # now the "Universal OBPI Attestation" section, which still names all
        # three axes for gate-firing scope and cites the predicate function.
        from pathlib import Path

        repo_root = Path(__file__).resolve().parent.parent
        agents_md = (repo_root / "AGENTS.md").read_text(encoding="utf-8")

        # Heading is now the Universal OBPI Attestation section (ADR-0.0.36).
        self.assertIn("Universal OBPI Attestation", agents_md)
        # Sensitivity axis still named for gate-firing scope.
        self.assertIn("sensitivity", agents_md)
        # Source-of-truth citation present.
        self.assertIn("_requires_human_obpi_attestation", agents_md)
        # The security axis is still enumerated as a gate-firing factor.
        self.assertIn("`security`", agents_md)


if __name__ == "__main__":
    unittest.main()
