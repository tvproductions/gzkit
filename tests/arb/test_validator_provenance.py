"""Tests for ARB receipt provenance checking (GHI #199 follow-up).

When a receipt's ``step.name`` is a canonical attestation label
(``typecheck``, ``unittest``, ...), its ``step.command`` MUST match the
canonical invocation. Otherwise the attestation claim is measuring the
wrong scope — the same class of failure GHI #199 documented when an ARB
receipt's scope disagreed with the ``gz typecheck`` gate's.

Every canonical command is read from ``CANONICAL_STEP_COMMANDS`` rather than
restated, so widening a scope (as ``typecheck`` was on 2026-08-08) does not
silently turn a positive control into a stale literal. The negative controls
are hand-written on purpose — a derived negative control cannot diverge, which
is the one property a negative control must have.
"""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from gzkit.arb.validator import (
    CANONICAL_STEP_COMMANDS,
    RETIRED_STEP_COMMANDS,
    validate_receipts,
)


def _write_step_receipt(
    root: Path,
    name: str,
    step_name: str,
    command: list[str],
    *,
    timestamp: str | None = "2026-04-18T12:00:00Z",
) -> Path:
    path = root / f"arb-step-{step_name}-{name}.json"
    payload = {
        "schema": "gzkit.arb.step_receipt.v1",
        "run_id": f"arb-step-{step_name}-{name}",
        "timestamp_utc": timestamp,
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
            # The GHI #199 failure shape: a receipt labelled `typecheck` whose
            # command measures a DIFFERENT scope than the gate. The divergence
            # here is the dropped `--exclude features/**` — the canonical scope
            # became tree-wide on 2026-08-08, so the old control (`ty check .`
            # with the exclusion) is now canon minus the launcher and would
            # have proved only that `uvx` != `uv run`.
            _write_step_receipt(
                root,
                "drifted",
                "typecheck",
                ["uv", "run", "ty", "check", "."],
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

    def test_canonical_coverage_command_validates(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_step_receipt(
                root,
                "cov",
                "coverage",
                CANONICAL_STEP_COMMANDS["coverage"],
            )
            result = validate_receipts(limit=10, root=root)
            self.assertEqual(result.valid, 1)
            self.assertEqual(result.non_canonical_provenance, 0)

    def test_non_canonical_coverage_command_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_step_receipt(
                root,
                "cov-drifted",
                "coverage",
                ["coverage", "run", "-m", "pytest"],  # wrong test runner
            )
            result = validate_receipts(limit=10, root=root)
            self.assertEqual(result.non_canonical_provenance, 1)

    def test_canonical_mkdocs_command_validates(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_step_receipt(
                root,
                "md",
                "mkdocs",
                CANONICAL_STEP_COMMANDS["mkdocs"],
            )
            result = validate_receipts(limit=10, root=root)
            self.assertEqual(result.valid, 1)
            self.assertEqual(result.non_canonical_provenance, 0)

    def test_non_canonical_mkdocs_command_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_step_receipt(
                root,
                "md-drifted",
                "mkdocs",
                ["uv", "run", "mkdocs", "build"],  # missing --strict
            )
            result = validate_receipts(limit=10, root=root)
            self.assertEqual(result.non_canonical_provenance, 1)

    def test_uncanonical_step_name_is_ignored(self) -> None:
        """Step names not in the canonical table are not subject to provenance checks."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_step_receipt(root, "bh", "behave", ["uv", "run", "behave"])
            result = validate_receipts(limit=10, root=root)
            self.assertEqual(result.valid, 1)
            self.assertEqual(result.non_canonical_provenance, 0)


class RetiredCanonIsJudgedAtTheReceiptsOwnTimestamp(unittest.TestCase):
    """A receipt records what was run; canon is read as of when it ran.

    Widening the `typecheck` scope on 2026-08-08 would otherwise have marked
    749 truthful receipts non-canonical overnight — the validator asserting a
    falsehood about history, which is the write-forward-only violation the
    operator ruled on for `.gzkit/schemas/ledger_events.json`. These tests pin
    the grandfather clause AND its two closing edges, because a clause that
    only ever admits is an escape hatch rather than a rule.
    """

    def _retired(self, name: str) -> tuple[str, list[str]]:
        return RETIRED_STEP_COMMANDS[name][0]

    def test_receipt_predating_the_change_is_canonical(self) -> None:
        retired_at, command = self._retired("typecheck")
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_step_receipt(
                root, "historic", "typecheck", command, timestamp="2026-07-01T00:00:00Z"
            )
            result = validate_receipts(limit=10, root=root)
            self.assertEqual(result.non_canonical_provenance, 0)
            self.assertEqual(result.valid, 1, msg=f"retired_at={retired_at}")

    def test_same_command_run_after_the_change_is_still_rejected(self) -> None:
        """The clause grandfathers history, never a stale invocation today."""
        _, command = self._retired("typecheck")
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_step_receipt(
                root, "stale", "typecheck", command, timestamp="2026-09-01T00:00:00Z"
            )
            result = validate_receipts(limit=10, root=root)
            self.assertEqual(result.non_canonical_provenance, 1)

    def test_missing_timestamp_cannot_claim_the_grandfather(self) -> None:
        """Fail closed: omitting the field must not buy the exemption.

        The refusal comes from the receipt *schema*, which requires
        `timestamp_utc`, so validation stops before provenance is consulted at
        all — a stronger guarantee than the provenance check alone. Asserted as
        "not valid" rather than as a provenance count for exactly that reason:
        pinning the channel here would make this test fail if the schema ever
        got stricter, which is the wrong direction to be brittle in.
        """
        _, command = self._retired("typecheck")
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_step_receipt(root, "undated", "typecheck", command, timestamp=None)
            result = validate_receipts(limit=10, root=root)
            self.assertEqual(result.valid, 0)
            self.assertEqual(result.invalid, 1)

    def test_unparseable_timestamp_cannot_claim_the_grandfather(self) -> None:
        _, command = self._retired("typecheck")
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_step_receipt(root, "garbled", "typecheck", command, timestamp="not-a-date")
            result = validate_receipts(limit=10, root=root)
            self.assertEqual(result.non_canonical_provenance, 1)

    def test_a_command_never_canonical_is_not_grandfathered_by_age(self) -> None:
        """Age alone proves nothing — the command must be a RETIRED one."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_step_receipt(
                root,
                "ancient-junk",
                "typecheck",
                ["uv", "run", "ty", "check", "some-scope-nobody-canonized"],
                timestamp="2020-01-01T00:00:00Z",
            )
            result = validate_receipts(limit=10, root=root)
            self.assertEqual(result.non_canonical_provenance, 1)


if __name__ == "__main__":
    unittest.main()
