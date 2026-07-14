"""Tests for OBPI-0.0.72-04 — the ``security_floor_overridden`` ledger event.

The event witnesses an operator override of the completion-state-editing
security floor (``gz obpi complete --accept-security-floor``), closing the
invisible-override audit hole the OBPI-0.0.71-01 override exposed.

Coverage map:

| REQ                | Class                                   |
|--------------------|-----------------------------------------|
| REQ-0.0.72-04-01   | TestSecurityFloorOverriddenModel        |
| REQ-0.0.72-04-02   | TestSecurityFloorOverriddenEmission     |
| REQ-0.0.72-04-03   | TestSecurityFloorOverriddenCensus       |
| REQ-0.0.72-04-05   | TestSecurityFloorOverriddenRoundTrip    |

REQ-04 is a SUPPORT REQ (ledger.json schema entry) proven by the schema
alignment tests in ``tests/test_schemas.py`` + ``gz validate --documents``,
not by a ``@covers`` test here (ADR-0.0.59 proof-channel discipline).
"""

from __future__ import annotations

import json
import tempfile
import unittest
from io import StringIO
from pathlib import Path
from unittest.mock import MagicMock, patch

from pydantic import ValidationError
from rich.console import Console

from gzkit.events import SecurityFloorOverriddenEvent, parse_typed_event
from gzkit.ledger_events import security_floor_overridden_event
from gzkit.traceability import covers

# ---------------------------------------------------------------------------
# REQ-0.0.72-04-01 — model shape + fail-closed empty fields
# ---------------------------------------------------------------------------


class TestSecurityFloorOverriddenModel(unittest.TestCase):
    """REQ-0.0.72-04-01 — the model carries the audit fields and fails closed."""

    def _valid_kwargs(self) -> dict[str, str]:
        return {
            "id": "OBPI-0.0.72-04-security-floor-overridden-event",
            "event": "security_floor_overridden",
            "obpi_id": "OBPI-0.0.72-04-security-floor-overridden-event",
            "surfaces": "auth_boundaries",
            "reason": "operator reviewed overlap; change is structurally defensive",
            "attestor": "g0",
        }

    @covers("REQ-0.0.72-04-01")
    def test_model_carries_audit_fields(self) -> None:
        event = SecurityFloorOverriddenEvent(**self._valid_kwargs())
        self.assertEqual(event.obpi_id, "OBPI-0.0.72-04-security-floor-overridden-event")
        self.assertEqual(event.surfaces, "auth_boundaries")
        self.assertEqual(event.attestor, "g0")
        self.assertIn("structurally defensive", event.reason)
        # ts is inherited from _EventBase and always present.
        self.assertTrue(event.ts)

    @covers("REQ-0.0.72-04-01")
    def test_empty_required_string_fails_closed(self) -> None:
        for field in ("obpi_id", "surfaces", "reason", "attestor"):
            with self.subTest(field=field):
                kwargs = self._valid_kwargs()
                kwargs[field] = ""
                with self.assertRaises(ValidationError):
                    SecurityFloorOverriddenEvent(**kwargs)


# ---------------------------------------------------------------------------
# REQ-0.0.72-04-05 — localized writer-model round-trip coherence
# ---------------------------------------------------------------------------


class TestSecurityFloorOverriddenRoundTrip(unittest.TestCase):
    """REQ-0.0.72-04-05 — a factory-emitted event round-trips clean to the typed model."""

    @covers("REQ-0.0.72-04-05")
    def test_factory_output_round_trips_to_typed_model(self) -> None:
        emitted = security_floor_overridden_event(
            obpi_id="OBPI-0.0.72-04-security-floor-overridden-event",
            surfaces="auth_boundaries",
            reason="operator reviewed overlap",
            attestor="g0",
        )
        # Serialize exactly as Ledger.append writes it, then re-parse via the
        # discriminated union — real emitted output re-validated (localized
        # writer-model coherence, not a hand-built happy-path stub).
        raw = emitted.model_dump()
        parsed = parse_typed_event(raw)
        self.assertIsInstance(parsed, SecurityFloorOverriddenEvent)
        self.assertEqual(parsed.obpi_id, "OBPI-0.0.72-04-security-floor-overridden-event")
        self.assertEqual(parsed.surfaces, "auth_boundaries")
        self.assertEqual(parsed.reason, "operator reviewed overlap")
        self.assertEqual(parsed.attestor, "g0")


# ---------------------------------------------------------------------------
# REQ-0.0.72-04-03 — census surfaces the override
# ---------------------------------------------------------------------------


class TestSecurityFloorOverriddenCensus(unittest.TestCase):
    """REQ-0.0.72-04-03 — a ledger census counts the emitted override 0 -> 1."""

    @staticmethod
    def _census(ledger_path: Path) -> int:
        return sum(
            1
            for line in ledger_path.read_text(encoding="utf-8").splitlines()
            if line.strip() and json.loads(line).get("event") == "security_floor_overridden"
        )

    @covers("REQ-0.0.72-04-03")
    def test_census_counts_from_zero_to_one(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            ledger_path = Path(tmp) / "ledger.jsonl"
            ledger_path.write_text("", encoding="utf-8")
            self.assertEqual(self._census(ledger_path), 0)

            emitted = security_floor_overridden_event(
                obpi_id="OBPI-0.0.72-04-security-floor-overridden-event",
                surfaces="auth_boundaries",
                reason="operator reviewed overlap",
                attestor="g0",
            )
            with ledger_path.open("a", encoding="utf-8") as handle:
                json.dump(emitted.model_dump(), handle, separators=(",", ":"))
                handle.write("\n")

            self.assertEqual(self._census(ledger_path), 1)


# ---------------------------------------------------------------------------
# REQ-0.0.72-04-02 — emission from the --accept-security-floor branch
# ---------------------------------------------------------------------------

_OVERRIDE_BRIEF = """\
---
id: OBPI-0.0.72-04-security-floor-overridden-event
parent: ADR-0.0.72-meta-governance-coherence
item: 4
lane: Heavy
status: Draft
---

# OBPI-0.0.72-04: emission test fixture

## Objective

Test brief whose Allowed Paths intersect a registered security surface.

## Allowed Paths

- `src/gzkit/commands/obpi_complete.py`

## Requirements (FAIL-CLOSED)

1. Emission fires only on --accept-security-floor override.

## Acceptance Criteria

- [ ] REQ-0.0.72-04-02 [behavior]: emission fires.

## Evidence

### Implementation Summary

- Files created/modified: src/gzkit/commands/obpi_complete.py

### Key Proof

Emission fires on override.

## Human Attestation

- Attestor: `<name>` when required, otherwise `n/a`
- Attestation: substantive attestation text or `n/a`
- Date: YYYY-MM-DD or `n/a`

---

**Date Completed:** -
"""

_NON_OVERLAP_BRIEF = _OVERRIDE_BRIEF.replace(
    "- `src/gzkit/commands/obpi_complete.py`",
    "- `docs/user/runbook.md`",
)

_REGISTRY = [
    {
        "category": "auth_boundaries",
        "globs": ["src/gzkit/commands/obpi_complete.py"],
        "rationale": "Test fixture — auth-boundary surface exercising the auto-detect floor.",
    },
]


def _mock_config() -> MagicMock:
    config = MagicMock()
    config.mode = "heavy"
    config.paths.ledger = ".gzkit/ledger.jsonl"
    return config


def _mock_ledger(obpi_id: str, parent_adr: str) -> MagicMock:
    ledger = MagicMock()
    ledger.canonicalize_id.return_value = obpi_id
    ledger.get_artifact_graph.return_value = {
        obpi_id: {"type": "obpi", "parent": parent_adr, "ledger_completed": False},
        parent_adr: {"type": "adr", "lane": "heavy"},
    }
    return ledger


class _EmissionFixture(unittest.TestCase):
    """Drive obpi_complete_cmd against a mocked filesystem.

    ``_execute_transaction`` / ``_surrender_lock_at_completion`` / ``_print_success``
    are patched to no-ops (no real file I/O), and the post-commit best-effort
    override emitter ``_emit_security_floor_override_best_effort`` is patched so a
    test can inspect the event the command wired into it. If ``transaction_raises``
    is set the (mocked) transaction fails, exercising the phantom-guard path where
    the post-commit emitter is never reached.
    """

    def _run_capture_emit(
        self,
        brief_text: str,
        accept_security_floor: str | None,
        registry: list[dict] | None,
        *,
        transaction_raises: bool = False,
    ) -> MagicMock:
        obpi_id = "OBPI-0.0.72-04-security-floor-overridden-event"
        parent = "ADR-0.0.72-meta-governance-coherence"
        ledger = _mock_ledger(obpi_id, parent)
        exec_mock = MagicMock()
        if transaction_raises:
            exec_mock.side_effect = OSError("forced transaction failure")
        emit_mock = MagicMock()
        rec_console = Console(file=StringIO())

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".gzkit" / "rules").mkdir(parents=True)
            (root / ".gzkit" / "rules" / "security-sensitivity.md").write_text(
                "# Security Sensitivity Rule\n\n## Walkthrough Checklist\n\n- Boundary confirmed\n",
                encoding="utf-8",
            )
            if registry is not None:
                (root / "data").mkdir(parents=True, exist_ok=True)
                (root / "data" / "security_surfaces.json").write_text(
                    json.dumps(registry), encoding="utf-8"
                )
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
                    return_value=(obpi_file, obpi_id),
                ),
                patch("gzkit.commands.obpi_complete.Ledger", return_value=ledger),
                patch(
                    "gzkit.commands.obpi_complete.resolve_adr_file",
                    return_value=(root / "adr.md", parent),
                ),
                patch(
                    "gzkit.commands.obpi_complete.capture_validation_anchor",
                    return_value=MagicMock(commit="abc1234", semver="0.0.72"),
                ),
                patch("gzkit.commands.obpi_complete._enforce_reconcile_receipt_gate", MagicMock()),
                patch(
                    "gzkit.commands.obpi_complete._enforce_attestation_receipt_gate", MagicMock()
                ),
                patch("gzkit.commands.obpi_complete._enforce_req_coverage_gate", MagicMock()),
                patch("gzkit.commands.obpi_complete._execute_transaction", exec_mock),
                patch(
                    "gzkit.commands.obpi_complete._emit_security_floor_override_best_effort",
                    emit_mock,
                ),
                patch("gzkit.commands.obpi_complete._surrender_lock_at_completion", MagicMock()),
                patch("gzkit.commands.obpi_complete._print_success", MagicMock()),
            ]
            for p in patches:
                p.start()
            try:
                try:
                    from gzkit.commands.obpi_complete import obpi_complete_cmd

                    obpi_complete_cmd(
                        obpi=obpi_id,
                        attestor="g0",
                        attestation_text="attest completed",
                        implementation_summary="- Files: obpi_complete.py",
                        key_proof="Emission fires on override.",
                        adversary_verdict="not-refuted",
                        adversary="codex/gpt-5.4",
                        as_json=False,
                        dry_run=False,
                        accept_security_floor=accept_security_floor,
                    )
                except SystemExit:
                    pass
            finally:
                for p in patches:
                    p.stop()
        return emit_mock


class TestSecurityFloorOverriddenEmission(_EmissionFixture):
    """REQ-0.0.72-04-02 — the override witness is built + handed to the post-commit
    emitter ONLY on --accept-security-floor, and never for a failed completion."""

    @covers("REQ-0.0.72-04-02")
    def test_override_event_emitted_on_override(self) -> None:
        emit_mock = self._run_capture_emit(
            brief_text=_OVERRIDE_BRIEF,
            accept_security_floor="operator reviewed overlap; change is defensive",
            registry=_REGISTRY,
        )
        self.assertIsNotNone(emit_mock.call_args, "post-commit override emitter was never reached")
        event = emit_mock.call_args.args[1]
        self.assertIsNotNone(event, "override event was not built on --accept-security-floor")
        self.assertEqual(event.event, "security_floor_overridden")
        self.assertEqual(event.extra["reason"], "operator reviewed overlap; change is defensive")
        self.assertEqual(event.extra["attestor"], "g0")
        self.assertIn("auth_boundaries", event.extra["surfaces"])

    @covers("REQ-0.0.72-04-02")
    def test_no_override_event_on_normal_completion(self) -> None:
        emit_mock = self._run_capture_emit(
            brief_text=_NON_OVERLAP_BRIEF,
            accept_security_floor=None,
            registry=_REGISTRY,
        )
        self.assertIsNotNone(emit_mock.call_args, "post-commit override emitter was never reached")
        self.assertIsNone(emit_mock.call_args.args[1])

    @covers("REQ-0.0.72-04-02")
    def test_no_phantom_override_when_transaction_fails(self) -> None:
        # The emitter runs AFTER the transaction; a failed transaction _fail-exits
        # first, so the override is never emitted for a completion that did not
        # commit (structural phantom guard — the emitter is outside the rollback).
        emit_mock = self._run_capture_emit(
            brief_text=_OVERRIDE_BRIEF,
            accept_security_floor="operator reviewed overlap",
            registry=_REGISTRY,
            transaction_raises=True,
        )
        self.assertIsNone(
            emit_mock.call_args,
            "override must not be emitted when the completion transaction failed",
        )


class TestSecurityFloorOverrideBestEffort(unittest.TestCase):
    """REQ-0.0.72-04-02 + Step-4b regression (Codex rounds 1-4): the post-commit
    override emitter is fully best-effort — it appends once on success, no-ops on
    a None event, and NEVER raises when the append (or even its own warning) fails,
    so it can never gate the completion or revert the committed receipt."""

    @staticmethod
    def _event() -> object:
        return security_floor_overridden_event(
            obpi_id="OBPI-0.0.72-04-security-floor-overridden-event",
            surfaces="auth_boundaries",
            reason="operator reviewed overlap",
            attestor="g0",
        )

    def test_appends_event_once_on_success(self) -> None:
        from gzkit.commands.obpi_complete import _emit_security_floor_override_best_effort

        ledger = MagicMock()
        _emit_security_floor_override_best_effort(ledger, self._event())
        events = [
            c.args[0].event
            for c in ledger.append.call_args_list
            if c.args and hasattr(c.args[0], "event")
        ]
        self.assertEqual(events, ["security_floor_overridden"])

    def test_none_event_is_noop(self) -> None:
        from gzkit.commands.obpi_complete import _emit_security_floor_override_best_effort

        ledger = MagicMock()
        _emit_security_floor_override_best_effort(ledger, None)
        ledger.append.assert_not_called()

    @covers("REQ-0.0.72-04-02")
    def test_append_failure_is_swallowed_and_warns(self) -> None:
        from gzkit.commands.obpi_complete import _emit_security_floor_override_best_effort

        ledger = MagicMock()
        ledger.append.side_effect = OSError("disk full")
        console_mock = MagicMock()
        with patch("gzkit.commands.obpi_complete.console", console_mock):
            # Must not raise — a failed emission may never gate the completion.
            _emit_security_floor_override_best_effort(ledger, self._event())
        printed = " ".join(str(c.args[0]) for c in console_mock.print.call_args_list if c.args)
        self.assertIn("security_floor_overridden", printed)
        self.assertIn("best-effort", printed)

    @covers("REQ-0.0.72-04-02")
    def test_append_and_warning_both_failing_is_still_swallowed(self) -> None:
        # Step-4b round 4 (Codex): the warning path must itself be non-throwing —
        # a console backed by a closed stream raises ValueError. Neither the
        # failed append NOR the failed warning may escape and gate completion.
        from gzkit.commands.obpi_complete import _emit_security_floor_override_best_effort

        ledger = MagicMock()
        ledger.append.side_effect = OSError("disk full")
        console_mock = MagicMock()
        console_mock.print.side_effect = ValueError("I/O operation on closed file")
        with patch("gzkit.commands.obpi_complete.console", console_mock):
            # Must NOT raise despite both the append and its warning failing.
            _emit_security_floor_override_best_effort(ledger, self._event())
        console_mock.print.assert_called()


if __name__ == "__main__":
    unittest.main()
