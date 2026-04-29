"""Tests for the OBPI-0.0.22-05 Gate 5 security walkthrough + ARB receipt gate.

Coverage map:

| REQ                  | Class                                    |
|----------------------|------------------------------------------|
| REQ-0.0.22-05-01     | TestSecurityWalkthroughFires             |
| REQ-0.0.22-05-02     | TestSecurityWalkthroughSuppressed        |
| REQ-0.0.22-05-04     | TestSecurityPlaceholderSlotFailsClosed   |
| REQ-0.0.22-05-05     | TestSecurityReceiptMissingFailsClosed    |
| REQ-0.0.22-05-06     | TestSecurityReceiptStaleFailsClosed      |

Helper unit tests sit alongside as ``TestLoadSecurityChecklist`` /
``TestFindFreshSecurityReceipt`` so the gate's smaller pieces are exercised
in isolation before the integration tests assemble them.
"""

from __future__ import annotations

import json
import tempfile
import unittest
from datetime import UTC, datetime, timedelta
from io import StringIO
from pathlib import Path
from unittest.mock import MagicMock, patch

from rich.console import Console

from gzkit.commands.common import GzCliError
from gzkit.commands.obpi_complete import (
    _find_fresh_security_receipt,
    _load_security_checklist,
    _security_canonical_slot_filled,
    obpi_complete_cmd,
)
from gzkit.events import EventAnchor
from gzkit.traceability import covers

# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

_quiet_console = Console(file=StringIO())

_SECURITY_BRIEF = """\
---
id: OBPI-0.0.22-05-gate5-walkthrough-arb-slot
parent: ADR-0.0.22-security-sensitivity-doctrine
item: 5
lane: Heavy
status: Draft
sensitivity: security
---

# OBPI-0.0.22-05: security brief test fixture

## Objective

Test brief carrying ``sensitivity: security``.

## Allowed Paths

- `src/gzkit/commands/obpi_complete.py`

## Requirements (FAIL-CLOSED)

1. Walkthrough must fire for sensitivity:security briefs.

## Acceptance Criteria

- [ ] REQ-0.0.22-05-01: Walkthrough fires.

## Evidence

### Implementation Summary

- Files created/modified: src/gzkit/commands/obpi_complete.py
- Tests added: tests/commands/test_obpi_complete_security.py
- Date completed: 2026-04-29
- Attestation status: Pending
- Defects noted: none

### Key Proof

uv run -m unittest tests.commands.test_obpi_complete_security -v passes 0/0.

## Human Attestation

- Attestor: `<name>` when required, otherwise `n/a`
- Attestation: substantive attestation text or `n/a`
- Date: YYYY-MM-DD or `n/a`

---

**Brief Status:** Draft

**Date Completed:** -

**Evidence Hash:** -
"""

_NON_SECURITY_BRIEF = _SECURITY_BRIEF.replace("sensitivity: security\n", "")


_RULE_FILE_BODY = """\
# Security Sensitivity Rule

## Walkthrough Checklist

- Credential handling reviewed (no hardcoded secrets, no env-var leaks)
- Subprocess input validated (no shell=True, no unbounded user-controlled args)
- Crypto choices justified (algorithm, key size, library named)
- Boundary validation confirmed (untrusted input sanitized at the boundary)

## Other Section

This section must NOT appear in the parsed checklist.

- Decoy item that should not be returned
"""


def _mock_config():
    config = MagicMock()
    config.mode = "heavy"
    config.paths.ledger = ".gzkit/ledger.jsonl"
    return config


def _mock_ledger(obpi_id: str, parent_adr: str):
    ledger = MagicMock()
    ledger.canonicalize_id.return_value = obpi_id
    graph = {
        obpi_id: {
            "type": "obpi",
            "parent": parent_adr,
            "ledger_completed": False,
        },
        parent_adr: {
            "type": "adr",
            "lane": "heavy",
        },
    }
    ledger.get_artifact_graph.return_value = graph
    return ledger


def _write_security_receipt(root: Path, suffix: str, age_hours: float = 0.0) -> Path:
    """Write a ``arb-step-security-{suffix}.json`` receipt aged by ``age_hours``."""
    created_at = datetime.now(UTC) - timedelta(hours=age_hours)
    path = root / f"arb-step-security-{suffix}.json"
    payload = {
        "schema": "gzkit.arb.step_receipt.v1",
        "run_id": f"arb-step-security-{suffix}",
        "timestamp_utc": created_at.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "duration_ms": 10,
        "exit_status": 0,
        "stdout_tail": "",
        "stdout_truncated": False,
        "stderr_tail": "",
        "stderr_truncated": False,
        "git": {"commit": "abcdef0", "branch": "main", "dirty": False},
        "step": {"name": "security", "command": ["uv", "run", "bandit", "-r", "src"]},
    }
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


# ---------------------------------------------------------------------------
# Helper unit tests
# ---------------------------------------------------------------------------


class TestLoadSecurityChecklist(unittest.TestCase):
    """REQ-0.0.22-05-01 / REQ-0.0.22-05-02 — checklist read at runtime, not hardcoded."""

    @covers("REQ-0.0.22-05-01")
    def test_returns_bullets_under_walkthrough_checklist_heading(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            rule_dir = root / ".gzkit" / "rules"
            rule_dir.mkdir(parents=True)
            (rule_dir / "security-sensitivity.md").write_text(_RULE_FILE_BODY, encoding="utf-8")
            items = _load_security_checklist(root)
            self.assertEqual(len(items), 4)
            self.assertIn("Credential handling reviewed", items[0])
            self.assertIn("Subprocess input validated", items[1])
            self.assertIn("Crypto choices justified", items[2])
            self.assertIn("Boundary validation confirmed", items[3])
            # Decoy item under another section MUST NOT leak in.
            for item in items:
                self.assertNotIn("Decoy item", item)

    @covers("REQ-0.0.22-05-02")
    def test_raises_gzclierror_when_rule_file_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with self.assertRaises(GzCliError) as ctx:
                _load_security_checklist(root)
            self.assertIn("security-sensitivity.md", str(ctx.exception))
            self.assertIn("OBPI-0.0.22-06", str(ctx.exception))


class TestSecurityCanonicalSlotFilled(unittest.TestCase):
    """REQ-0.0.22-05-04 — slot-filled boolean reflects placeholder state."""

    @covers("REQ-0.0.22-05-04")
    def test_returns_false_when_slot_is_placeholder_empty_list(self) -> None:
        with patch.dict(
            "gzkit.arb.validator.CANONICAL_STEP_COMMANDS",
            {"security": []},
            clear=False,
        ):
            self.assertFalse(_security_canonical_slot_filled())

    @covers("REQ-0.0.22-05-04")
    def test_returns_true_when_slot_is_filled(self) -> None:
        with patch.dict(
            "gzkit.arb.validator.CANONICAL_STEP_COMMANDS",
            {"security": ["uv", "run", "bandit", "-r", "src"]},
            clear=False,
        ):
            self.assertTrue(_security_canonical_slot_filled())


class TestFindFreshSecurityReceipt(unittest.TestCase):
    """REQ-0.0.22-05-05 / REQ-0.0.22-05-06 — fresh-receipt search semantics."""

    @covers("REQ-0.0.22-05-05")
    def test_returns_none_pair_when_no_security_receipts_exist(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            newest, fresh = _find_fresh_security_receipt(root)
            self.assertIsNone(newest)
            self.assertIsNone(fresh)

    @covers("REQ-0.0.22-05-06")
    def test_returns_newest_but_not_fresh_when_only_stale_receipts_exist(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            stale_path = _write_security_receipt(root, "stale", age_hours=25.0)
            newest, fresh = _find_fresh_security_receipt(root, max_age_hours=24)
            self.assertEqual(newest, stale_path)
            self.assertIsNone(fresh)

    @covers("REQ-0.0.22-05-05")
    def test_returns_fresh_when_recent_receipt_exists(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fresh_path = _write_security_receipt(root, "recent", age_hours=1.0)
            newest, fresh = _find_fresh_security_receipt(root, max_age_hours=24)
            self.assertEqual(newest, fresh_path)
            self.assertEqual(fresh, fresh_path)


# ---------------------------------------------------------------------------
# Integration tests for the full security gate
# ---------------------------------------------------------------------------


class _ObpiCompleteIntegrationFixture(unittest.TestCase):
    """Shared mock-rig for the security-gate integration tests."""

    def _run_complete(
        self,
        brief_text: str,
        receipts_root: Path,
        rule_file_body: str | None,
        canonical_slot: list[str],
    ) -> tuple[type[BaseException] | None, int | None, list[str]]:
        """Drive ``obpi_complete_cmd`` against a mocked filesystem; return outcome."""
        recorded_console: list[str] = []
        rec_console = Console(file=StringIO(), record=True)
        original_print = rec_console.print

        def _capture(*args, **kwargs):
            recorded_console.append(" ".join(str(a) for a in args))
            return original_print(*args, **kwargs)

        rec_console.print = _capture  # type: ignore

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)

            if rule_file_body is not None:
                rule_dir = root / ".gzkit" / "rules"
                rule_dir.mkdir(parents=True)
                (rule_dir / "security-sensitivity.md").write_text(rule_file_body, encoding="utf-8")

            obpi_file = root / "brief.md"
            obpi_file.write_text(brief_text, encoding="utf-8")

            patches = [
                patch("gzkit.commands.obpi_complete.console", rec_console),
                patch("gzkit.commands.obpi_complete.get_project_root", return_value=root),
                patch(
                    "gzkit.commands.obpi_complete.ensure_initialized",
                    return_value=_mock_config(),
                ),
                patch(
                    "gzkit.commands.obpi_complete.resolve_obpi_file",
                    return_value=(obpi_file, "OBPI-0.0.22-05-gate5-walkthrough-arb-slot"),
                ),
                patch(
                    "gzkit.commands.obpi_complete.Ledger",
                    return_value=_mock_ledger(
                        "OBPI-0.0.22-05-gate5-walkthrough-arb-slot",
                        "ADR-0.0.22-security-sensitivity-doctrine",
                    ),
                ),
                patch(
                    "gzkit.commands.obpi_complete.resolve_adr_file",
                    return_value=(root / "adr.md", "ADR-0.0.22-security-sensitivity-doctrine"),
                ),
                patch(
                    "gzkit.commands.obpi_complete.capture_validation_anchor",
                    return_value=EventAnchor(commit="abc1234", semver="0.0.22"),
                ),
                # Bypass the GHI #290 TTY gate so we can exercise the security
                # gate in isolation; the security gate runs BEFORE this hook.
                patch(
                    "gzkit.commands.obpi_complete._enforce_human_attestation_authenticity",
                    return_value="human",
                ),
                # Drive the receipts-root resolver to our temp dir.
                patch(
                    "gzkit.commands.obpi_complete.receipts_root",
                    return_value=receipts_root,
                ),
                patch.dict(
                    "gzkit.arb.validator.CANONICAL_STEP_COMMANDS",
                    {"security": canonical_slot},
                    clear=False,
                ),
            ]

            for p in patches:
                p.start()
            try:
                exc_type: type[BaseException] | None = None
                code: int | None = None
                try:
                    obpi_complete_cmd(
                        obpi="OBPI-0.0.22-05-gate5-walkthrough-arb-slot",
                        attestor="Jeffry Babb",
                        attestation_text="attest completed",
                        implementation_summary="- Files: obpi_complete.py",
                        key_proof="gz obpi complete fires the walkthrough.",
                        as_json=False,
                        dry_run=False,
                    )
                except SystemExit as exc:
                    exc_type = SystemExit
                    code = int(exc.code) if isinstance(exc.code, int) else 1
            finally:
                for p in patches:
                    p.stop()

        return exc_type, code, recorded_console


class TestSecurityWalkthroughFires(_ObpiCompleteIntegrationFixture):
    """REQ-0.0.22-05-01 — walkthrough fires for sensitivity:security briefs."""

    @covers("REQ-0.0.22-05-01")
    def test_walkthrough_renders_checklist_for_security_brief(self) -> None:
        with tempfile.TemporaryDirectory() as receipts_dir:
            receipts_root = Path(receipts_dir)
            _write_security_receipt(receipts_root, "fresh", age_hours=1.0)
            exc_type, _code, output = self._run_complete(
                brief_text=_SECURITY_BRIEF,
                receipts_root=receipts_root,
                rule_file_body=_RULE_FILE_BODY,
                canonical_slot=["uv", "run", "bandit", "-r", "src"],
            )
            # The brief is in a Draft state and the test does not write it
            # back. The completion may exit on later steps; what matters is
            # that the walkthrough rendered the checklist BEFORE any failure.
            joined = "\n".join(output)
            self.assertIn("Security Review Walkthrough", joined)
            self.assertIn("Credential handling reviewed", joined)
            self.assertIn("Subprocess input validated", joined)
            self.assertIn("Crypto choices justified", joined)
            self.assertIn("Boundary validation confirmed", joined)
            # Sanity: walkthrough was invoked even if a downstream step
            # raised SystemExit; we do not pin code here.
            del exc_type


class TestSecurityWalkthroughSuppressed(_ObpiCompleteIntegrationFixture):
    """REQ-0.0.22-05-02 — walkthrough does NOT fire when sensitivity is absent."""

    @covers("REQ-0.0.22-05-02")
    def test_walkthrough_not_rendered_for_non_security_brief(self) -> None:
        with tempfile.TemporaryDirectory() as receipts_dir:
            receipts_root = Path(receipts_dir)
            # No security receipt; canonical slot empty. If the gate ran by
            # mistake it would fail closed; suppression is proven by the
            # absence of both the walkthrough header AND the gate's
            # placeholder-slot finding.
            _exc, _code, output = self._run_complete(
                brief_text=_NON_SECURITY_BRIEF,
                receipts_root=receipts_root,
                rule_file_body=None,
                canonical_slot=[],
            )
            joined = "\n".join(output)
            self.assertNotIn("Security Review Walkthrough", joined)
            self.assertNotIn("Security-scan canonical slot", joined)


class TestSecurityPlaceholderSlotFailsClosed(_ObpiCompleteIntegrationFixture):
    """REQ-0.0.22-05-04 — placeholder slot blocks completion with exit 3."""

    @covers("REQ-0.0.22-05-04")
    def test_placeholder_slot_exits_3_with_parent_adr_finding(self) -> None:
        with tempfile.TemporaryDirectory() as receipts_dir:
            receipts_root = Path(receipts_dir)
            exc_type, code, output = self._run_complete(
                brief_text=_SECURITY_BRIEF,
                receipts_root=receipts_root,
                rule_file_body=_RULE_FILE_BODY,
                canonical_slot=[],
            )
            self.assertIs(exc_type, SystemExit)
            self.assertEqual(code, 3)
            joined = "\n".join(output)
            self.assertIn("Security-scan canonical slot", joined)
            self.assertIn("ADR-0.0.22-security-sensitivity-doctrine", joined)


class TestSecurityReceiptMissingFailsClosed(_ObpiCompleteIntegrationFixture):
    """REQ-0.0.22-05-05 — filled slot + no receipt → exit 3 receipt-missing."""

    @covers("REQ-0.0.22-05-05")
    def test_receipt_missing_exits_3(self) -> None:
        with tempfile.TemporaryDirectory() as receipts_dir:
            receipts_root = Path(receipts_dir)
            # Slot filled, but no arb-step-security-* receipts exist.
            exc_type, code, output = self._run_complete(
                brief_text=_SECURITY_BRIEF,
                receipts_root=receipts_root,
                rule_file_body=_RULE_FILE_BODY,
                canonical_slot=["uv", "run", "bandit", "-r", "src"],
            )
            self.assertIs(exc_type, SystemExit)
            self.assertEqual(code, 3)
            joined = "\n".join(output)
            self.assertIn("receipt-missing", joined)


class TestSecurityReceiptStaleFailsClosed(_ObpiCompleteIntegrationFixture):
    """REQ-0.0.22-05-06 — filled slot + stale (>24h) receipt → exit 3 receipt-stale."""

    @covers("REQ-0.0.22-05-06")
    def test_receipt_stale_exits_3_citing_timestamp(self) -> None:
        with tempfile.TemporaryDirectory() as receipts_dir:
            receipts_root = Path(receipts_dir)
            stale_path = _write_security_receipt(receipts_root, "stale", age_hours=25.0)
            exc_type, code, output = self._run_complete(
                brief_text=_SECURITY_BRIEF,
                receipts_root=receipts_root,
                rule_file_body=_RULE_FILE_BODY,
                canonical_slot=["uv", "run", "bandit", "-r", "src"],
            )
            self.assertIs(exc_type, SystemExit)
            self.assertEqual(code, 3)
            joined = "\n".join(output)
            self.assertIn("receipt-stale", joined)
            self.assertIn(stale_path.name, joined)


if __name__ == "__main__":
    unittest.main()
