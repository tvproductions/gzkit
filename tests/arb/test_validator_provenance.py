"""Tests for ARB receipt provenance checking (GHI #199 follow-up).

When a receipt's ``step.name`` is a canonical attestation label
(``typecheck``, ``unittest``, ...), its ``step.command`` MUST match the
canonical invocation. Otherwise the attestation claim is measuring the
wrong scope — the same class of failure GHI #199 documented when an ARB
``ty check .`` receipt disagreed with ``gz typecheck``'s ``ty check src``
gate.
"""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from gzkit.arb.validator import CANONICAL_STEP_COMMANDS, validate_receipts


def _write_step_receipt(root: Path, name: str, step_name: str, command: list[str]) -> Path:
    path = root / f"arb-step-{step_name}-{name}.json"
    payload = {
        "schema": "gzkit.arb.step_receipt.v1",
        "run_id": f"arb-step-{step_name}-{name}",
        "timestamp_utc": "2026-04-18T12:00:00Z",
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


class ProvenanceChecking(unittest.TestCase):
    """Canonical step labels require canonical commands."""

    def test_canonical_typecheck_command_validates(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_step_receipt(
                root,
                "canonical",
                "typecheck",
                CANONICAL_STEP_COMMANDS["typecheck"],
            )
            result = validate_receipts(limit=10, root=root)
            self.assertEqual(result.scanned, 1)
            self.assertEqual(result.valid, 1)
            self.assertEqual(result.non_canonical_provenance, 0)

    def test_non_canonical_typecheck_command_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            # The GHI #199 failure shape — wide target, scope-diverging flags.
            _write_step_receipt(
                root,
                "drifted",
                "typecheck",
                ["uvx", "ty", "check", ".", "--exclude", "features/**"],
            )
            result = validate_receipts(limit=10, root=root)
            self.assertEqual(result.scanned, 1)
            self.assertEqual(result.valid, 0)
            self.assertEqual(result.invalid, 1)
            self.assertEqual(result.non_canonical_provenance, 1)
            self.assertTrue(any("non-canonical provenance" in e for e in result.errors))

    def test_non_canonical_unittest_command_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_step_receipt(
                root,
                "drifted-ut",
                "unittest",
                ["python", "-m", "unittest"],  # missing `uv run` and `-q`
            )
            result = validate_receipts(limit=10, root=root)
            self.assertEqual(result.non_canonical_provenance, 1)

    def test_uncanonical_step_name_is_ignored(self) -> None:
        """Step names not in the canonical table are not subject to provenance checks."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_step_receipt(root, "mk", "mkdocs", ["uv", "run", "mkdocs", "build"])
            result = validate_receipts(limit=10, root=root)
            self.assertEqual(result.valid, 1)
            self.assertEqual(result.non_canonical_provenance, 0)


if __name__ == "__main__":
    unittest.main()
