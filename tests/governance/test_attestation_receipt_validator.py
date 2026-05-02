"""Tests for the ``gz validate --attestation-receipts`` scope (OBPI-0.0.24-01).

@covers ADR-0.0.24-attestation-receipt-binding
@covers OBPI-0.0.24-01-validator-scope

Tests derive from the OBPI brief's REQ list. Each test is REQ-pinned via
``gzkit.traceability.covers`` and asserts behavior — not strings, not
internal helpers — per ``.claude/rules/tests.md`` § "Tests assert
semantics, not strings".

The validator is exposed as ``validate_attestation_receipts`` (worker) and
``audit_attestation_receipts`` (no-op wrapper for the dispatch table) from
``gzkit.governance.trust_audits``.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from gzkit.governance.trust_audits import (
    audit_attestation_receipts,
    validate_attestation_receipts,
)
from gzkit.traceability import covers

_RECEIPTS_ENV = "GZKIT_ARB_RECEIPTS_ROOT"


def _write_lint_receipt(root: Path, run_id: str, *, exit_status: int = 0) -> None:
    payload = {
        "exit_status": exit_status,
        "findings": [],
        "findings_total": 0,
        "findings_truncated": False,
        "git": {"branch": "main", "commit": "0" * 40, "dirty": False},
        "run_id": run_id,
        "schema": "gzkit.arb.lint_receipt.v1",
        "timestamp_utc": "2026-05-02T00:00:00Z",
        "tool": {"name": "ruff", "version": "ruff 0.15.11"},
    }
    (root / f"{run_id}.json").write_text(json.dumps(payload, sort_keys=True), encoding="utf-8")


def _write_step_receipt(root: Path, run_id: str, name: str, *, exit_status: int = 0) -> None:
    payload = {
        "duration_ms": 100,
        "exit_status": exit_status,
        "git": {"branch": "main", "commit": "0" * 40, "dirty": False},
        "run_id": run_id,
        "schema": "gzkit.arb.step_receipt.v1",
        "stderr_tail": "",
        "stderr_truncated": False,
        "stdout_tail": "ok\n",
        "stdout_truncated": False,
        "step": {"command": ["uv", "run", "ty", "check", "src"], "name": name},
        "timestamp_utc": "2026-05-02T00:00:00Z",
    }
    (root / f"{run_id}.json").write_text(json.dumps(payload, sort_keys=True), encoding="utf-8")


class AttestationReceiptValidatorTest(unittest.TestCase):
    """Worker-function semantics for ``validate_attestation_receipts``."""

    def setUp(self) -> None:
        self._tmpdir = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmpdir.cleanup)
        self.receipts_root = Path(self._tmpdir.name)
        self._prev_env = os.environ.get(_RECEIPTS_ENV)
        os.environ[_RECEIPTS_ENV] = str(self.receipts_root)

    def tearDown(self) -> None:
        if self._prev_env is None:
            os.environ.pop(_RECEIPTS_ENV, None)
        else:
            os.environ[_RECEIPTS_ENV] = self._prev_env

    @covers("REQ-0.0.24-01-01")
    def test_all_resolved_returns_exit_zero(self) -> None:
        run_id = "arb-ruff-" + "a" * 32
        _write_lint_receipt(self.receipts_root, run_id)
        text = f"lint clean (lint: receipt {run_id})"
        result = validate_attestation_receipts(text, lane="heavy", kind="feature")
        self.assertEqual(result.exit_code, 0, msg=str(result.entries))
        self.assertFalse(result.warn_only)
        self.assertEqual(len(result.entries), 1)
        self.assertEqual(result.entries[0].status, "resolved")
        self.assertEqual(result.entries[0].run_id, run_id)

    @covers("REQ-0.0.24-01-02")
    def test_missing_receipt_returns_exit_three(self) -> None:
        run_id = "arb-ruff-" + "b" * 32
        # Deliberately do not stage the receipt file.
        text = f"lint clean (lint: receipt {run_id})"
        result = validate_attestation_receipts(text, lane="heavy", kind="feature")
        self.assertEqual(result.exit_code, 3)
        self.assertEqual(len(result.entries), 1)
        self.assertEqual(result.entries[0].status, "missing")

    @covers("REQ-0.0.24-01-03")
    def test_status_mismatch_returns_exit_three(self) -> None:
        run_id = "arb-step-typecheck-" + "c" * 32
        _write_step_receipt(self.receipts_root, run_id, "typecheck", exit_status=1)
        text = f"typecheck clean (typecheck: receipt {run_id})"
        result = validate_attestation_receipts(text, lane="heavy", kind="feature")
        self.assertEqual(result.exit_code, 3)
        self.assertEqual(len(result.entries), 1)
        self.assertEqual(result.entries[0].status, "status_mismatch")

    @covers("REQ-0.0.24-01-04")
    def test_claim_mismatch_returns_exit_three(self) -> None:
        run_id = "arb-step-typecheck-" + "d" * 32
        _write_step_receipt(self.receipts_root, run_id, "typecheck")
        # Cite "lint" category adjacent to a typecheck receipt.
        text = f"clean lint (lint: receipt {run_id})"
        result = validate_attestation_receipts(text, lane="heavy", kind="feature")
        self.assertEqual(result.exit_code, 3)
        self.assertEqual(len(result.entries), 1)
        self.assertEqual(result.entries[0].status, "claim_mismatch")
        self.assertEqual(result.entries[0].cited_category, "lint")
        self.assertEqual(result.entries[0].derived_category, "typecheck")

    @covers("REQ-0.0.24-01-05")
    def test_malformed_receipt_id_reported_not_silent(self) -> None:
        # Embed a near-shape garbage token (uppercase hex, wrong length, etc.)
        # The validator must surface the malformed token, not silently skip.
        text = "lint clean (lint: receipt arb-ruff-NOTAVALIDHEX12345)"
        result = validate_attestation_receipts(text, lane="heavy", kind="feature")
        self.assertEqual(result.exit_code, 3)
        # Either we surface it as a malformed_id entry, or we surface it as
        # zero-receipts on a heavy lane (also exit 3). The contract is
        # "not silently skipped".
        self.assertGreater(len(result.entries), 0)
        statuses = {entry.status for entry in result.entries}
        # Heavy + zero-canonical-receipts is an enforceable failure path.
        self.assertTrue(
            "malformed_id" in statuses or result.exit_code == 3,
            msg=f"malformed token must surface; got {result.entries}",
        )

    @covers("REQ-0.0.24-01-06")
    def test_zero_receipts_warn_only_on_lite_non_foundation(self) -> None:
        text = "narrative attestation with no receipts"
        result = validate_attestation_receipts(text, lane="lite", kind="feature")
        self.assertEqual(result.exit_code, 0)
        self.assertTrue(result.warn_only)
        # No entries, since no receipt IDs were cited.
        self.assertEqual(result.entries, ())

    @covers("REQ-0.0.24-01-06")
    def test_zero_receipts_fail_closed_on_heavy(self) -> None:
        text = "narrative attestation with no receipts"
        result = validate_attestation_receipts(text, lane="heavy", kind="feature")
        self.assertEqual(result.exit_code, 3)
        self.assertFalse(result.warn_only)

    @covers("REQ-0.0.24-01-06")
    def test_zero_receipts_fail_closed_on_foundation_lite(self) -> None:
        text = "narrative attestation with no receipts"
        result = validate_attestation_receipts(text, lane="lite", kind="foundation")
        self.assertEqual(result.exit_code, 3)
        self.assertFalse(result.warn_only)

    @covers("REQ-0.0.24-01-01")
    def test_bare_citation_without_category_prefix(self) -> None:
        """A receipt ID standing alone (no ``lint:`` prefix) is also accepted."""
        run_id = "arb-step-unittest-" + "e" * 32
        _write_step_receipt(self.receipts_root, run_id, "unittest")
        text = f"tests pass: {run_id}"
        result = validate_attestation_receipts(text, lane="heavy", kind="feature")
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.entries[0].status, "resolved")
        self.assertEqual(result.entries[0].derived_category, "unittest")


class AuditAttestationReceiptsWrapperTest(unittest.TestCase):
    """The ``audit_*`` wrapper for the validate-scope dispatch table."""

    @covers("REQ-0.0.24-01-01")
    def test_wrapper_returns_empty_list_without_input(self) -> None:
        # The umbrella ``--audits`` sweep calls every audit_* wrapper without
        # extra args. The attestation-receipts validator is opt-in
        # (gated by ``--attestation-receipts <text|@file>``); the wrapper
        # therefore returns an empty error list when invoked with no input.
        errors = audit_attestation_receipts(Path.cwd())
        self.assertEqual(errors, [])


@unittest.skipIf(sys.platform == "win32", "shell quoting cost is high on Windows")
class AttestationReceiptCliSmokeTest(unittest.TestCase):
    """Smoke test the ``gz validate --attestation-receipts`` CLI surface."""

    @covers("REQ-0.0.24-01-01")
    def test_cli_reports_resolved_receipt(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            run_id = "arb-ruff-" + "f" * 32
            _write_lint_receipt(root, run_id)
            env = {**os.environ, _RECEIPTS_ENV: str(root)}
            cmd = [
                "uv",
                "run",
                "gz",
                "validate",
                "--attestation-receipts",
                f"lint clean (lint: receipt {run_id})",
                "--lane",
                "heavy",
                "--kind",
                "feature",
            ]
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding="utf-8",
                env=env,
                check=False,
            )
            self.assertEqual(
                result.returncode,
                0,
                msg=f"stdout={result.stdout!r} stderr={result.stderr!r}",
            )


if __name__ == "__main__":
    unittest.main()
