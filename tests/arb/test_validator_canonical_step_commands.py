"""Tests for the security-scan canonical-step slot in ``CANONICAL_STEP_COMMANDS``.

OBPI-0.0.22-05 reserves a ``"security"`` entry in ``CANONICAL_STEP_COMMANDS``
whose value is the placeholder empty list. The toolchain feature ADR (the one
promoting ``pool.agentic-security-review``) fills it; this OBPI only reserves
the slot. Receipts with ``step.name == "security"`` therefore fail provenance
checking against the placeholder until the slot is filled — that fail-closed
posture is the whole point of REQ-3.
"""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from gzkit.arb.validator import CANONICAL_STEP_COMMANDS, validate_receipts
from gzkit.traceability import covers


def _write_step_receipt(root: Path, suffix: str, step_name: str, command: list[str]) -> Path:
    path = root / f"arb-step-{step_name}-{suffix}.json"
    payload = {
        "schema": "gzkit.arb.step_receipt.v1",
        "run_id": f"arb-step-{step_name}-{suffix}",
        "timestamp_utc": "2026-04-29T07:30:00Z",
        "duration_ms": 10,
        "exit_status": 0,
        "stdout_tail": "",
        "stdout_truncated": False,
        "stderr_tail": "",
        "stderr_truncated": False,
        "git": {"commit": "abcdef0", "branch": "main", "dirty": False},
        "step": {"name": step_name, "command": command},
    }
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


class TestSecurityCanonicalSlot(unittest.TestCase):
    """REQ-0.0.22-05-03 — reserved security slot with placeholder shape."""

    @covers("REQ-0.0.22-05-03")
    def test_security_slot_present_in_canonical_step_commands(self) -> None:
        self.assertIn("security", CANONICAL_STEP_COMMANDS)

    @covers("REQ-0.0.22-05-03")
    def test_security_slot_value_is_placeholder_empty_list(self) -> None:
        # Placeholder shape: empty list signals the canonical command string is
        # deferred to the toolchain feature ADR. Filling the slot is out of
        # scope for this OBPI.
        self.assertEqual(CANONICAL_STEP_COMMANDS["security"], [])

    @covers("REQ-0.0.22-05-03")
    def test_security_receipt_with_any_command_fails_provenance_until_slot_filled(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            # A toolchain candidate (e.g. bandit) that the feature ADR might
            # canonize. Until the slot is filled, the receipt's command does
            # NOT match the placeholder ``[]``, so provenance fails.
            _write_step_receipt(
                root,
                "candidate",
                "security",
                ["uv", "run", "bandit", "-r", "src"],
            )
            result = validate_receipts(limit=10, root=root)
            self.assertEqual(result.scanned, 1)
            self.assertEqual(result.valid, 0)
            self.assertEqual(result.invalid, 1)
            self.assertEqual(result.non_canonical_provenance, 1)
            self.assertTrue(
                any("non-canonical provenance" in e for e in result.errors),
                msg=f"errors={result.errors}",
            )


if __name__ == "__main__":
    unittest.main()
