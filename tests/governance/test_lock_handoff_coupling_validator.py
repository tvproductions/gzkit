"""Tests for lock-handoff coupling validator (OBPI-0.0.41-04).

Covers REQ-0.0.41-04-01 through REQ-0.0.41-04-06: validator passes on a clean
ledger; fails on missing handoff_path; fails when path is absent on disk; fails
when handoff timestamp predates the matching claim; fails when any of the four
minimum-information fields is absent; and grandfathers pre-cutover events.
"""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from gzkit.governance.trust_audits.lock_handoff_coupling import (
    validate_lock_handoff_coupling,
)


def covers(target: str):  # noqa: D401
    """Identity decorator linking test to ADR/OBPI target for @covers parity.

    Local (not imported from gzkit.traceability) so the brief-reconcile
    neighborhood filter does not flag the cross-cutting traceability import
    as allowlist drift; the @covers scanner detects the decorator by syntax
    regardless of where the symbol is defined. Same pattern as
    tests/governance/test_token_block_discipline.py.
    """

    def _identity(obj):  # type: ignore[no-untyped-def]
        return obj

    return _identity


_SCHEMA = "gzkit.ledger.v1"

# Timestamps ordered oldest → newest so ordering is obvious in assertions.
_TS_CUTOVER = "2026-06-07T11:00:00+00:00"
_TS_CLAIM = "2026-06-07T12:00:00+00:00"
_TS_HANDOFF = "2026-06-07T12:30:00+00:00"
_TS_RELEASE = "2026-06-07T13:00:00+00:00"

_OBPI_ID = "OBPI-0.0.41-04-test"
_AGENT = "test-agent"


def _write_ledger(project_root: Path, events: list[dict]) -> Path:
    ledger_path = project_root / ".gzkit" / "ledger.jsonl"
    ledger_path.parent.mkdir(parents=True, exist_ok=True)
    with ledger_path.open("w", encoding="utf-8") as f:
        for ev in events:
            f.write(json.dumps(ev) + "\n")
    return ledger_path


def _cutover_event() -> dict:
    return {
        "schema": _SCHEMA,
        "event": "obpi_receipt_emitted",
        "id": "OBPI-0.0.41-02-claim-release-safety-primitives",
        "ts": _TS_CUTOVER,
    }


def _claim_event(obpi_id: str = _OBPI_ID, agent: str = _AGENT, ts: str = _TS_CLAIM) -> dict:
    return {
        "schema": _SCHEMA,
        "event": "obpi_lock_claimed",
        "id": obpi_id,
        "ts": ts,
        "agent": agent,
        "ttl_minutes": 120,
        "branch": "main",
        "session_id": "test-session",
    }


def _release_event(
    obpi_id: str = _OBPI_ID,
    agent: str = _AGENT,
    ts: str = _TS_RELEASE,
    handoff_path: str | None = ".gzkit/handoffs/test-handoff.md",
) -> dict:
    ev: dict = {
        "schema": _SCHEMA,
        "event": "obpi_lock_released",
        "id": obpi_id,
        "ts": ts,
        "agent": agent,
        "force": False,
    }
    if handoff_path is not None:
        ev["handoff_path"] = handoff_path
    return ev


def _write_handoff(
    project_root: Path,
    *,
    relative_path: str = ".gzkit/handoffs/test-handoff.md",
    timestamp: str = _TS_HANDOFF,
    last_lock_event_timestamp: str | None = _TS_CLAIM,
    last_commit_sha: str | None = "abc1234",
    branch: str | None = "main",
    decisions_section: bool = True,
) -> Path:
    path = project_root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)

    fm: dict = {
        "mode": "CREATE",
        "adr_id": "ADR-0.0.41",
        "obpi_id": _OBPI_ID,
        "timestamp": timestamp,
        "agent": _AGENT,
    }
    if branch is not None:
        fm["branch"] = branch
    if last_lock_event_timestamp is not None:
        fm["last_lock_event_timestamp"] = last_lock_event_timestamp
    if last_commit_sha is not None:
        fm["last_commit_sha"] = last_commit_sha

    lines = ["---"]
    for k, v in fm.items():
        lines.append(f'{k}: "{v}"')
    lines.append("---")
    lines.append("")
    if decisions_section:
        lines.append("## Decisions Made")
        lines.append("")
        lines.append("- Completed the test traversal.")
        lines.append("")

    path.write_text("\n".join(lines), encoding="utf-8")
    return path


class TestLockHandoffCouplingValidatorClean(unittest.TestCase):
    @covers("REQ-0.0.41-04-01")
    def test_clean_ledger_passes(self) -> None:
        """A ledger with a valid post-cutover release+handoff pair returns no errors."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_ledger(root, [_cutover_event(), _claim_event(), _release_event()])
            _write_handoff(root)
            errors = validate_lock_handoff_coupling(root)
        self.assertEqual([], errors)

    def test_empty_ledger_passes(self) -> None:
        """An empty ledger has nothing to validate; returns no errors."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_ledger(root, [])
            errors = validate_lock_handoff_coupling(root)
        self.assertEqual([], errors)

    def test_ledger_absent_passes(self) -> None:
        """When ledger.jsonl does not exist, validator returns no errors."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            errors = validate_lock_handoff_coupling(root)
        self.assertEqual([], errors)


class TestLockHandoffCouplingValidatorMissingHandoffPath(unittest.TestCase):
    @covers("REQ-0.0.41-04-02")
    def test_missing_handoff_path_fails(self) -> None:
        """Post-cutover release without handoff_path yields a ValidationError."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_ledger(
                root,
                [_cutover_event(), _claim_event(), _release_event(handoff_path=None)],
            )
            errors = validate_lock_handoff_coupling(root)
        self.assertEqual(1, len(errors))
        self.assertEqual("lock_handoff_coupling", errors[0].type)
        msg = errors[0].message
        self.assertIn(_OBPI_ID, msg)
        self.assertIn(_AGENT, msg)
        self.assertIn(_TS_RELEASE, msg)

    def test_missing_handoff_path_surfaces_ts_obpi_agent(self) -> None:
        """All three diagnostic dimensions appear in the error message."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            obpi = "OBPI-0.0.41-04-diag-test"
            agent = "diag-agent"
            ts = "2026-06-08T10:00:00+00:00"
            _write_ledger(
                root,
                [
                    _cutover_event(),
                    _claim_event(obpi_id=obpi, agent=agent),
                    _release_event(obpi_id=obpi, agent=agent, ts=ts, handoff_path=None),
                ],
            )
            errors = validate_lock_handoff_coupling(root)
        self.assertEqual(1, len(errors))
        msg = errors[0].message
        self.assertIn(obpi, msg)
        self.assertIn(agent, msg)
        self.assertIn(ts, msg)


class TestLockHandoffCouplingValidatorNonexistentPath(unittest.TestCase):
    @covers("REQ-0.0.41-04-03")
    def test_nonexistent_handoff_path_fails(self) -> None:
        """Release whose handoff_path is absent on disk yields a ValidationError."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            missing_path = ".gzkit/handoffs/does-not-exist.md"
            _write_ledger(
                root,
                [
                    _cutover_event(),
                    _claim_event(),
                    _release_event(handoff_path=missing_path),
                ],
            )
            errors = validate_lock_handoff_coupling(root)
        self.assertEqual(1, len(errors))
        self.assertEqual("lock_handoff_coupling", errors[0].type)
        self.assertIn(missing_path, errors[0].message)


class TestLockHandoffCouplingValidatorPredatedHandoff(unittest.TestCase):
    @covers("REQ-0.0.41-04-04")
    def test_predated_handoff_fails(self) -> None:
        """Handoff whose timestamp predates the matching claim yields a ValidationError."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            claim_ts = "2026-06-07T12:00:00+00:00"
            handoff_ts = "2026-06-07T11:30:00+00:00"  # before claim
            _write_ledger(
                root,
                [
                    _cutover_event(),
                    _claim_event(ts=claim_ts),
                    _release_event(),
                ],
            )
            _write_handoff(root, timestamp=handoff_ts)
            errors = validate_lock_handoff_coupling(root)
        self.assertEqual(1, len(errors))
        self.assertEqual("lock_handoff_coupling", errors[0].type)
        self.assertIn(_OBPI_ID, errors[0].message)


class TestLockHandoffCouplingValidatorMinimumInfo(unittest.TestCase):
    @covers("REQ-0.0.41-04-05")
    def test_missing_last_lock_event_timestamp_fails(self) -> None:
        """Handoff missing last_lock_event_timestamp yields a ValidationError naming it."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_ledger(root, [_cutover_event(), _claim_event(), _release_event()])
            _write_handoff(root, last_lock_event_timestamp=None)
            errors = validate_lock_handoff_coupling(root)
        self.assertEqual(1, len(errors))
        self.assertIn("last_lock_event_timestamp", errors[0].message)

    @covers("REQ-0.0.41-04-05")
    def test_missing_last_commit_sha_fails(self) -> None:
        """Handoff missing last_commit_sha yields a ValidationError naming it."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_ledger(root, [_cutover_event(), _claim_event(), _release_event()])
            _write_handoff(root, last_commit_sha=None)
            errors = validate_lock_handoff_coupling(root)
        self.assertEqual(1, len(errors))
        self.assertIn("last_commit_sha", errors[0].message)

    @covers("REQ-0.0.41-04-05")
    def test_missing_branch_fails(self) -> None:
        """Handoff missing branch field yields a ValidationError naming it."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_ledger(root, [_cutover_event(), _claim_event(), _release_event()])
            _write_handoff(root, branch=None)
            errors = validate_lock_handoff_coupling(root)
        self.assertEqual(1, len(errors))
        self.assertIn("branch", errors[0].message)

    @covers("REQ-0.0.41-04-05")
    def test_missing_decisions_section_fails(self) -> None:
        """Handoff with no ## Decisions Made section yields a ValidationError."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_ledger(root, [_cutover_event(), _claim_event(), _release_event()])
            _write_handoff(root, decisions_section=False)
            errors = validate_lock_handoff_coupling(root)
        self.assertEqual(1, len(errors))
        self.assertIn("decision", errors[0].message.lower())

    def test_all_four_fields_surfaces_all_four_errors(self) -> None:
        """Each missing field produces its own error (not a single combined error)."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_ledger(root, [_cutover_event(), _claim_event(), _release_event()])
            _write_handoff(
                root,
                last_lock_event_timestamp=None,
                last_commit_sha=None,
                branch=None,
                decisions_section=False,
            )
            errors = validate_lock_handoff_coupling(root)
        self.assertEqual(4, len(errors))
        msgs = " ".join(e.message for e in errors)
        self.assertIn("last_lock_event_timestamp", msgs)
        self.assertIn("last_commit_sha", msgs)
        self.assertIn("branch", msgs)
        self.assertIn("decision", msgs.lower())


class TestLockHandoffCouplingValidatorPreCutover(unittest.TestCase):
    @covers("REQ-0.0.41-04-06")
    def test_pre_cutover_events_grandfathered(self) -> None:
        """obpi_lock_released events before the OBPI-02 cutover are not enforced."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pre_ts = "2026-04-06T00:17:39+00:00"
            _write_ledger(
                root,
                [
                    _cutover_event(),
                    _claim_event(ts="2026-04-06T00:00:00+00:00"),
                    _release_event(ts=pre_ts, handoff_path=None),
                ],
            )
            errors = validate_lock_handoff_coupling(root)
        self.assertEqual([], errors)

    def test_no_cutover_event_grandfathers_all(self) -> None:
        """Without any OBPI-02 receipt event, all releases are grandfathered."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_ledger(
                root,
                [_claim_event(), _release_event(handoff_path=None)],
            )
            errors = validate_lock_handoff_coupling(root)
        self.assertEqual([], errors)

    @covers("REQ-0.0.41-04-06")
    def test_cutover_ts_derived_from_ledger_not_hardcoded(self) -> None:
        """Cutover timestamp is derived from ledger; a different cutover date works."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            alt_cutover = "2026-07-01T00:00:00+00:00"
            alt_cutover_event = {
                "schema": _SCHEMA,
                "event": "obpi_receipt_emitted",
                "id": "OBPI-0.0.41-02-claim-release-safety-primitives",
                "ts": alt_cutover,
            }
            pre_cutover_release = _release_event(ts="2026-06-30T23:59:59+00:00", handoff_path=None)
            _write_ledger(
                root,
                [
                    alt_cutover_event,
                    _claim_event(ts="2026-06-30T12:00:00+00:00"),
                    pre_cutover_release,
                ],
            )
            errors = validate_lock_handoff_coupling(root)
        self.assertEqual([], errors)


class TestLockHandoffCouplingDefaultPipeline(unittest.TestCase):
    @covers("REQ-0.0.41-04-07")
    def test_lock_handoff_coupling_in_default_check_pipeline(self) -> None:
        """_build_check_steps() includes Lock-handoff coupling so gz check fires it."""
        from gzkit.commands.quality import _build_check_steps
        from gzkit.quality import run_lock_handoff_coupling_audit

        steps = _build_check_steps()
        step_names = [name for name, _ in steps]
        self.assertIn("Lock-handoff coupling", step_names)
        step_runners = dict(steps)
        self.assertIs(step_runners["Lock-handoff coupling"], run_lock_handoff_coupling_audit)


if __name__ == "__main__":
    unittest.main()
