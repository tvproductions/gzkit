"""Tests for the setpoint-coherence validator (OBPI-0.0.37-20).

The validator asserts that every (content_type x consumer) pair declared in
``data/vendor-manifest.json`` ``content_type_routes`` carries a legal declared
setpoint in ``content_type_temperatures``. Legal tokens are {lite, medium,
heavy} (mirrored from src/gzkit/schemas/vendor_manifest.json).
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from gzkit.traceability import covers


def _write_manifest(root: Path, payload: dict) -> None:
    """Write a vendor-manifest fixture under ``root/data``."""
    data_dir = root / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    (data_dir / "vendor-manifest.json").write_text(
        json.dumps(payload), encoding="utf-8"
    )


class TestSetpointCoherence(unittest.TestCase):
    """Validator behaviors REQ-0.0.37-20-01/02/03."""

    @covers("REQ-0.0.37-20-01")
    def test_routed_pair_without_setpoint_is_flagged(self) -> None:
        """A (content_type, vendor) routed pair with no declared setpoint -> error."""
        from gzkit.governance.trust_audits.setpoint_coherence import (
            validate_setpoint_coherence,
        )

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_manifest(
                root,
                {
                    "content_type_routes": {"AgentContract": ["claude", "codex"]},
                    "content_type_temperatures": {"AgentContract": {"claude": "heavy"}},
                },
            )
            errors = validate_setpoint_coherence(root)
            self.assertTrue(errors, "expected a coherence error for the uncovered pair")
            blob = " ".join(e.message for e in errors)
            self.assertIn("codex", blob)
            self.assertIn("AgentContract", blob)

    @covers("REQ-0.0.37-20-02")
    def test_illegal_setpoint_token_is_flagged(self) -> None:
        """A declared setpoint token outside {lite, medium, heavy} -> error."""
        from gzkit.governance.trust_audits.setpoint_coherence import (
            validate_setpoint_coherence,
        )

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_manifest(
                root,
                {
                    "content_type_routes": {"AgentContract": ["claude"]},
                    "content_type_temperatures": {"AgentContract": {"claude": "frozen"}},
                },
            )
            errors = validate_setpoint_coherence(root)
            self.assertTrue(errors, "expected an illegal-token error")
            blob = " ".join(e.message for e in errors)
            self.assertIn("frozen", blob)

    @covers("REQ-0.0.37-20-03")
    def test_coherent_manifest_has_no_errors(self) -> None:
        """Every routed pair carries a legal setpoint -> no errors."""
        from gzkit.governance.trust_audits.setpoint_coherence import (
            validate_setpoint_coherence,
        )

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_manifest(
                root,
                {
                    "content_type_routes": {
                        "AgentContract": ["claude", "codex"],
                        "Rule": ["claude"],
                    },
                    "content_type_temperatures": {
                        "AgentContract": {"claude": "heavy", "codex": "lite"},
                        "Rule": {"claude": "heavy"},
                    },
                },
            )
            self.assertEqual(validate_setpoint_coherence(root), [])

    @covers("REQ-0.0.37-20-01")
    def test_missing_manifest_fails_closed(self) -> None:
        """An absent manifest fails closed with an error (no silent pass)."""
        from gzkit.governance.trust_audits.setpoint_coherence import (
            validate_setpoint_coherence,
        )

        with TemporaryDirectory() as tmp:
            errors = validate_setpoint_coherence(Path(tmp))
            self.assertTrue(errors, "missing manifest must fail closed")


class TestTemperatureAccessorFailClosed(unittest.TestCase):
    """REQ-0.0.37-20-04 — the declared-setpoint accessor fails closed."""

    @covers("REQ-0.0.37-20-04")
    def test_temperature_for_raises_on_undeclared_pair(self) -> None:
        """``temperature_for`` raises ValueError on an undeclared (type, vendor) pair.

        Pins the fail-closed accessor contract: no baked-in vendor-locked default
        is ever resolved for a pair absent from content_type_temperatures.
        """
        from gzkit.content.vendors import temperature_for

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_manifest(
                root,
                {
                    "content_type_routes": {"AgentContract": ["claude"]},
                    "content_type_temperatures": {"AgentContract": {"claude": "heavy"}},
                },
            )
            with self.assertRaises(ValueError):
                temperature_for("AgentContract", "codex", project_root=root)


if __name__ == "__main__":
    unittest.main()
