"""Tests for gz validate --task-envelope-coherence (OBPI-0.0.64-04).

REQ-derived assertions for:
  REQ-0.0.64-04-01: signature (a) — worklog event under active TASK with no task_id
  REQ-0.0.64-04-02: signature (b) — OBPI all-seq=01 without req_atomic suppression
  REQ-0.0.64-04-03: signature (c) — layer-drift across frontmatter tasks: and ledger task_id
  REQ-0.0.64-04-05: gz task envelope diagnose renders per-channel declarations
  REQ-0.0.64-04-06: validator is registered in the gz check pipeline
"""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import yaml

from gzkit.commands import validate_task_envelope
from gzkit.commands.validate_cmd import _validate_task_envelope_coherence
from gzkit.traceability import covers


def _write_ledger(root: Path, lines: list[str]) -> None:
    gzkit_dir = root / ".gzkit"
    gzkit_dir.mkdir(parents=True, exist_ok=True)
    (gzkit_dir / "ledger.jsonl").write_text("\n".join(lines), encoding="utf-8")


def _write_brief(root: Path, frontmatter: dict) -> Path:
    brief_dir = (
        root / "docs" / "design" / "adr" / "foundation" / "ADR-0.0.64-test-fixture" / "obpis"
    )
    brief_dir.mkdir(parents=True, exist_ok=True)
    fm_text = yaml.dump(frontmatter, default_flow_style=False)
    body = "\n# Test Brief\n\n## Acceptance Criteria\n\n- [ ] REQ-0.0.64-04-01\n"
    brief_path = brief_dir / "OBPI-0.0.64-04-fixture.md"
    brief_path.write_text(f"---\n{fm_text}---\n{body}", encoding="utf-8")
    return brief_path


_BASE_FM = {
    "id": "OBPI-0.0.64-04",
    "parent": "ADR-0.0.64-task-envelope-and-planning-decomposition",
    "lane": "Heavy",
    "status": "Draft",
    "allowlist": ["src/gzkit/commands/validate_cmd.py"],
    "reqs": ["REQ-0.0.64-04-01"],
    "verification": ["uv run gz lint"],
}


def _write_brief_with_id(root: Path, obpi_id: str) -> Path:
    """Write a minimal OBPI brief whose frontmatter ``id`` is ``obpi_id``.

    Used to populate the drift loop with several distinct OBPIs so a per-OBPI
    subprocess regression is observable as a call count > 1.
    """
    safe = obpi_id.replace(".", "_")
    brief_dir = root / "docs" / "design" / "adr" / "foundation" / f"ADR-fixture-{safe}" / "obpis"
    brief_dir.mkdir(parents=True, exist_ok=True)
    fm = {**_BASE_FM, "id": obpi_id}
    fm_text = yaml.dump(fm, default_flow_style=False)
    body = "\n# Test Brief\n\n## Acceptance Criteria\n\n- [ ] REQ-0.0.64-04-01\n"
    brief_path = brief_dir / f"{obpi_id}.md"
    brief_path.write_text(f"---\n{fm_text}---\n{body}", encoding="utf-8")
    return brief_path


class TestSignatureA(unittest.TestCase):
    """Signature (a): worklog event under active TASK with no task_id."""

    @covers("REQ-0.0.64-04-01")
    def test_worklog_without_task_id_under_active_task_fails(self) -> None:
        """Worklog event with no task_id while a TASK is active → violation."""
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _write_ledger(
                root,
                [
                    json.dumps(
                        {
                            "event": "task_started",
                            "task_id": "TASK-0.0.64-04-01-01",
                            "obpi_id": "OBPI-0.0.64-04",
                            "id": "evt-1",
                            "schema_": "1.0",
                            "timestamp": "2026-05-30T15:00:00Z",
                        }
                    ),
                    # Exemplar worklog type. Was `artifact_edited` until GHI #947
                    # removed that type from `_TASK_WORKLOG_TYPES`; `gate_checked`
                    # carries a `task_id` and has no carve-out, so it exercises the
                    # same general signature (a) rule this test is about.
                    json.dumps(
                        {
                            "event": "gate_checked",
                            "id": "evt-2",
                            "schema_": "1.0",
                            "timestamp": "2026-05-30T15:01:00Z",
                        }
                    ),
                    json.dumps(
                        {
                            "event": "task_completed",
                            "task_id": "TASK-0.0.64-04-01-01",
                            "obpi_id": "OBPI-0.0.64-04",
                            "id": "evt-3",
                            "schema_": "1.0",
                            "timestamp": "2026-05-30T15:02:00Z",
                        }
                    ),
                ],
            )
            errors = [
                e for e in _validate_task_envelope_coherence(root) if "Signature (a)" in e.message
            ]
            self.assertGreater(len(errors), 0, "Expected signature (a) violation")

    @covers("REQ-0.0.64-04-01")
    def test_worklog_with_task_id_under_active_task_passes(self) -> None:
        """Worklog event WITH task_id under active TASK → no signature (a) violation."""
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _write_ledger(
                root,
                [
                    json.dumps(
                        {
                            "event": "task_started",
                            "task_id": "TASK-0.0.64-04-01-01",
                            "obpi_id": "OBPI-0.0.64-04",
                            "id": "evt-1",
                            "schema_": "1.0",
                            "timestamp": "2026-05-30T15:00:00Z",
                        }
                    ),
                    json.dumps(
                        {
                            "event": "artifact_edited",
                            "path": "src/foo.py",
                            "session": "s1",
                            "task_id": "TASK-0.0.64-04-01-01",
                            "id": "evt-2",
                            "schema_": "1.0",
                            "timestamp": "2026-05-30T15:01:00Z",
                        }
                    ),
                    json.dumps(
                        {
                            "event": "task_completed",
                            "task_id": "TASK-0.0.64-04-01-01",
                            "obpi_id": "OBPI-0.0.64-04",
                            "id": "evt-3",
                            "schema_": "1.0",
                            "timestamp": "2026-05-30T15:02:00Z",
                        }
                    ),
                ],
            )
            errors = [
                e for e in _validate_task_envelope_coherence(root) if "Signature (a)" in e.message
            ]
            self.assertEqual(len(errors), 0)

    @covers("REQ-0.0.64-04-01")
    def test_worklog_without_active_task_is_clean(self) -> None:
        """Worklog event with no task_id and no active TASK → no violation."""
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _write_ledger(
                root,
                [
                    json.dumps(
                        {
                            "event": "artifact_edited",
                            "path": "src/foo.py",
                            "session": "s1",
                            "id": "evt-1",
                            "schema_": "1.0",
                            "timestamp": "2026-05-30T15:01:00Z",
                        }
                    ),
                ],
            )
            errors = [
                e for e in _validate_task_envelope_coherence(root) if "Signature (a)" in e.message
            ]
            self.assertEqual(len(errors), 0)

    @covers("REQ-0.0.64-04-01")
    def test_historical_worklog_before_enforcement_epoch_is_clean(self) -> None:
        """Pre-recovery TASK rows are bounded historical drift, not current failure."""
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _write_ledger(
                root,
                [
                    json.dumps(
                        {
                            "event": "task_started",
                            "task_id": "TASK-0.0.64-04-01-01",
                            "obpi_id": "OBPI-0.0.64-04",
                            "id": "evt-1",
                            "schema_": "1.0",
                            "timestamp": "2026-05-30T14:43:59Z",
                        }
                    ),
                    json.dumps(
                        {
                            "event": "artifact_edited",
                            "path": "src/foo.py",
                            "session": "s1",
                            "id": "evt-2",
                            "schema_": "1.0",
                            "timestamp": "2026-05-30T14:43:59Z",
                        }
                    ),
                ],
            )
            errors = [
                e for e in _validate_task_envelope_coherence(root) if "Signature (a)" in e.message
            ]
            self.assertEqual(len(errors), 0)

    @covers("REQ-0.0.64-04-01")
    def test_terminal_event_clears_task_under_divergent_obpi_id_spelling(self) -> None:
        """A completed TASK is not active even when start/complete used different
        obpi_id spellings (short ``OBPI-0.0.74-20`` vs full slug).

        Regression pin for the real 2026-06-24 ledger incident: the TASK was
        started once with the short obpi_id and once with the full slug, then
        completed under the full slug. Keying the terminal discard to the
        event's own obpi_id left the start orphaned in the short-form bucket, so
        the validator marked the TASK perpetually active — and every later
        ADR-closeout worklog row (``attested`` + ``gate_checked``, emitted with
        no ``task_id`` because they are ADR ceremony, not TASK labor) tripped
        Signature (a). A TASK's identity is its globally-unique ``task_id``; its
        terminal event ends it regardless of which obpi_id label was recorded.
        """
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _write_ledger(
                root,
                [
                    json.dumps(
                        {
                            "event": "task_started",
                            "task_id": "TASK-0.0.74-20-01-01",
                            "obpi_id": "OBPI-0.0.74-20",  # short form
                            "id": "evt-1",
                            "schema_": "1.0",
                            "timestamp": "2026-06-24T00:45:33Z",
                        }
                    ),
                    json.dumps(
                        {
                            "event": "task_started",
                            "task_id": "TASK-0.0.74-20-01-01",
                            "obpi_id": "OBPI-0.0.74-20-mx-gz-check-step-checkpoint-seam",  # full
                            "id": "evt-2",
                            "schema_": "1.0",
                            "timestamp": "2026-06-24T00:50:19Z",
                        }
                    ),
                    json.dumps(
                        {
                            "event": "task_completed",
                            "task_id": "TASK-0.0.74-20-01-01",
                            "obpi_id": "OBPI-0.0.74-20-mx-gz-check-step-checkpoint-seam",  # full
                            "id": "evt-3",
                            "schema_": "1.0",
                            "timestamp": "2026-06-24T01:03:36Z",
                        }
                    ),
                    # ADR-closeout ceremony rows emitted long after the TASK
                    # closed, with no task_id — these are NOT TASK labor.
                    json.dumps(
                        {
                            "event": "attested",
                            "id": "ADR-0.0.74-mx-mode-maintenance-hangar",
                            "status": "completed",
                            "schema_": "1.0",
                            "timestamp": "2026-06-27T23:10:02Z",
                        }
                    ),
                    json.dumps(
                        {
                            "event": "gate_checked",
                            "id": "ADR-0.0.74-mx-mode-maintenance-hangar",
                            "gate": 2,
                            "status": "pass",
                            "schema_": "1.0",
                            "timestamp": "2026-06-27T23:19:43Z",
                        }
                    ),
                ],
            )
            errors = [
                e for e in _validate_task_envelope_coherence(root) if "Signature (a)" in e.message
            ]
            self.assertEqual(
                len(errors),
                0,
                "completed TASK must not stay active under divergent obpi_id spelling",
            )

    @covers("REQ-0.0.64-04-01")
    def test_meta_receipt_bind_ceremony_event_excluded_from_signature_a(self) -> None:
        """Closeout ``meta-receipt-bind`` is ceremony, not labor → no signature (a).

        A ``meta-receipt-bind`` ``audit_receipt_emitted`` is a Gate-5 ceremony
        receipt-binding event: it carries an ``attestor`` and binds
        already-emitted attestation receipts at closeout. It is not a TASK labor
        unit, so it MUST NOT trip signature (a) even when emitted under an active
        TASK with no top-level ``task_id``. Regression pin for the OBPI-0.0.37-12
        return-to-health instance (GHI #563): ledger ``:8460`` was a post-epoch
        meta-receipt-bind the labor signature wrongly flagged.
        """
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _write_ledger(
                root,
                [
                    json.dumps(
                        {
                            "event": "task_started",
                            "task_id": "TASK-0.0.37-12-01-01",
                            "obpi_id": "OBPI-0.0.37-12-temperature-renderer-templates",
                            "id": "evt-1",
                            "schema_": "1.0",
                            "timestamp": "2026-06-01T11:00:00Z",
                        }
                    ),
                    json.dumps(
                        {
                            "event": "audit_receipt_emitted",
                            "receipt_event": "meta-receipt-bind",
                            "attestor": "g0",
                            "id": "ADR-0.0.37-constitutional-invariant-composition",
                            "schema_": "1.0",
                            "timestamp": "2026-06-01T11:09:46Z",
                        }
                    ),
                ],
            )
            errors = [
                e for e in _validate_task_envelope_coherence(root) if "Signature (a)" in e.message
            ]
            self.assertEqual(
                len(errors), 0, "meta-receipt-bind ceremony event must not trip signature (a)"
            )

    @covers("REQ-0.0.64-04-01")
    def test_non_ceremony_audit_receipt_under_active_task_still_fails(self) -> None:
        """The ceremony carve-out is narrow: only ``meta-receipt-bind`` is excused.

        A bare ``audit_receipt_emitted`` (no ``receipt_event``) under an active
        TASK with no ``task_id`` still represents labor-time receipt emission and
        MUST trip signature (a). Guards against the meta-receipt-bind exclusion
        widening into a blanket ``audit_receipt_emitted`` bypass that would blind
        the gate to genuine labor drift.
        """
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _write_ledger(
                root,
                [
                    json.dumps(
                        {
                            "event": "task_started",
                            "task_id": "TASK-0.0.64-04-01-01",
                            "obpi_id": "OBPI-0.0.64-04",
                            "id": "evt-1",
                            "schema_": "1.0",
                            "timestamp": "2026-05-30T15:00:00Z",
                        }
                    ),
                    json.dumps(
                        {
                            "event": "audit_receipt_emitted",
                            "id": "evt-2",
                            "schema_": "1.0",
                            "timestamp": "2026-05-30T15:01:00Z",
                        }
                    ),
                ],
            )
            errors = [
                e for e in _validate_task_envelope_coherence(root) if "Signature (a)" in e.message
            ]
            self.assertGreater(
                len(errors), 0, "non-ceremony audit receipt without task_id must still fail"
            )

    @covers("REQ-0.0.64-04-01")
    def test_composition_rendered_telemetry_excluded_from_signature_a(self) -> None:
        """``composition_rendered`` is validator-emitted render telemetry, not labor.

        ``gz validate --invariant-coherence`` emits one ``composition_rendered``
        event on every run (``invariant_coherence.py``), and that validator is in
        the default ``gz check`` scope. Any ``gz check`` run during an active OBPI
        pipeline therefore emits an unattributed ``composition_rendered`` while
        TASKs are live — a whole-AGENTS.md render that belongs to no single REQ and
        cannot be honestly attributed to one. It MUST NOT trip signature (a).
        Regression pin for the OBPI-0.0.37-14 instance (ledger ``:8521``-``:8523``).
        """
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _write_ledger(
                root,
                [
                    json.dumps(
                        {
                            "event": "task_started",
                            "task_id": "TASK-0.0.37-14-01-01",
                            "obpi_id": "OBPI-0.0.37-14-wire-sync-retire-monolith",
                            "id": "evt-1",
                            "schema_": "1.0",
                            "timestamp": "2026-06-02T07:56:24Z",
                        }
                    ),
                    json.dumps(
                        {
                            "event": "composition_rendered",
                            "id": "composition-rendered-2026-06-02T08:15:21Z",
                            "invariant_count": 4,
                            "target": "AGENTS.md",
                            "byte_count": 33048,
                            "schema_": "1.0",
                            "timestamp": "2026-06-02T08:15:21Z",
                        }
                    ),
                ],
            )
            errors = [
                e for e in _validate_task_envelope_coherence(root) if "Signature (a)" in e.message
            ]
            self.assertEqual(
                len(errors), 0, "composition_rendered telemetry must not trip signature (a)"
            )

    def test_commit_locus_artifact_edited_excluded_from_signature_a(self) -> None:
        """A commit-locus backstop row has NO attribution channel, so it cannot fail (GHI #869).

        ``artifact_edited_event`` (``ledger_events.py``) accepts no ``task_id``
        parameter, so the commit-locus backstop introduced by GHI #847 -- the
        ``commit`` field is its discriminator -- physically cannot attribute one.
        Gating it on attribution makes the row fail permanently: the ledger is
        append-only, so it can never be repaired, and it blocks every subsequent
        push including commits unrelated to the OBPI whose TASKs were open.
        Measured instance: ledger ``:15362``, an AGENTS.md canon render committed
        as ``a80ed283`` while eight auto-started OBPI-0.35.0-08 TASKs were live.

        Same ground as the ``composition_rendered`` carve-out directly above: a
        row derived from a commit diff after the fact is not an attributable
        labor unit. Attributing it to an arbitrary live TASK would be FALSE
        attribution, which is worse than none.
        """
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _write_ledger(
                root,
                [
                    json.dumps(
                        {
                            "event": "task_started",
                            "task_id": "TASK-0.35.0-08-01-01",
                            "obpi_id": "OBPI-0.35.0-08-remember-post-append-advisory",
                            "id": "evt-1",
                            "schema_": "1.0",
                            "timestamp": "2026-08-23T13:12:21Z",
                        }
                    ),
                    json.dumps(
                        {
                            "event": "artifact_edited",
                            "id": "AGENTS.md",
                            "path": "AGENTS.md",
                            "commit": "a80ed283543e9e29b3f1b8649e47c0ae64b2e3be",
                            "schema_": "1.0",
                            "timestamp": "2026-08-23T14:24:09Z",
                        }
                    ),
                ],
            )
            errors = [
                e for e in _validate_task_envelope_coherence(root) if "Signature (a)" in e.message
            ]
            self.assertEqual(
                len(errors), 0, "commit-locus artifact_edited must not trip signature (a)"
            )

    def test_tool_locus_artifact_edited_cannot_trip_signature_a(self) -> None:
        """The tool locus has no attribution channel either, so it cannot fail (GHI #947).

        INVERTED 2026-09-02. This pin previously asserted the opposite, on the
        premise that "the tool locus records an edit AT edit time, when a live
        TASK is knowable and attributable". Measured, that premise is false in
        both halves:

        * ``artifact_edited_event`` (``ledger_events.py``) accepts no ``task_id``
          parameter at all, so ``record_artifact_edit`` cannot record one even
          when it knows which TASK is live -- the identical "sole caller cannot
          supply one even in principle" property GHI #869 established for the
          commit locus.
        * There is no single current TASK to attribute to. TASKs are listed per
          OBPI, and ``gz obpi pipeline`` auto-starts one per REQ; 12 were active
          across two OBPIs when this was measured.

        So ``artifact_edited`` never satisfied ``_TASK_WORKLOG_TYPES``' own
        stated membership criterion -- "worklog event types that carry an
        optional ``task_id`` field" -- and gating it produced rows that fail
        permanently against an append-only ledger, blocking every later push.
        The type is out of the roster; both loci are ungated for it.

        The negative control this once provided is preserved in kind by
        ``test_attested_without_task_id_still_trips_signature_a``: types that DO
        carry a ``task_id`` must still fail unattributed, so removing one type
        from the roster is not the same as disarming signature (a).
        """
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _write_ledger(
                root,
                [
                    json.dumps(
                        {
                            "event": "task_started",
                            "task_id": "TASK-0.35.0-08-01-01",
                            "obpi_id": "OBPI-0.35.0-08-remember-post-append-advisory",
                            "id": "evt-1",
                            "schema_": "1.0",
                            "timestamp": "2026-08-23T13:12:21Z",
                        }
                    ),
                    json.dumps(
                        {
                            "event": "artifact_edited",
                            "id": "src/foo.py",
                            "path": "src/foo.py",
                            "session": "s1",
                            "schema_": "1.0",
                            "timestamp": "2026-08-23T14:24:09Z",
                        }
                    ),
                ],
            )
            errors = [
                e for e in _validate_task_envelope_coherence(root) if "Signature (a)" in e.message
            ]
            self.assertEqual(
                len(errors),
                0,
                "a tool-locus row has no task_id channel, so gating it can only fail forever",
            )

    def test_attested_without_task_id_still_trips_signature_a(self) -> None:
        """Replacement negative control for the inversion above (GHI #947).

        Dropping ``artifact_edited`` from ``_TASK_WORKLOG_TYPES`` must not be
        mistakable for disarming signature (a). ``attested`` remains in the
        roster, so an unattributed ``attested`` row under a live TASK still
        trips the signature. Without this pin, deleting the whole roster would
        look identical to the correct fix.

        This docstring asserted "its producer DOES carry a ``task_id``" until
        2026-09-03. That was false and is corrected here (GHI #950):
        ``attested_event`` is ``(adr_id, status, by, reason)`` -- no ``task_id``
        parameter -- so ``attested`` fails the same membership criterion that
        evicted ``artifact_edited``. What this test pins is therefore narrower
        than the original claim: that the roster is still ARMED, not that its
        remaining members are attributable. Whether they should be in it at all
        is #950's subject; until that is ruled, do not read this pin as evidence
        the roster is coherent.
        """
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _write_ledger(
                root,
                [
                    json.dumps(
                        {
                            "event": "task_started",
                            "task_id": "TASK-0.35.0-08-01-01",
                            "obpi_id": "OBPI-0.35.0-08-remember-post-append-advisory",
                            "id": "evt-1",
                            "schema_": "1.0",
                            "timestamp": "2026-08-23T13:12:21Z",
                        }
                    ),
                    json.dumps(
                        {
                            "event": "attested",
                            "id": "evt-2",
                            "schema_": "1.0",
                            "timestamp": "2026-08-23T14:24:09Z",
                        }
                    ),
                ],
            )
            errors = [
                e for e in _validate_task_envelope_coherence(root) if "Signature (a)" in e.message
            ]
            self.assertEqual(
                len(errors), 1, "an unattributed attested row is real drift and must still fail"
            )

    @covers("REQ-0.0.64-04-01")
    def test_obpi_brief_reflection_edit_under_active_task_is_clean(self) -> None:
        """Editing the active OBPI brief itself is closeout reflection, not TASK labor."""
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _write_ledger(
                root,
                [
                    json.dumps(
                        {
                            "event": "task_started",
                            "task_id": "TASK-0.0.37-13-01-01",
                            "obpi_id": "OBPI-0.0.37-13-reverse-parse-migration",
                            "id": "evt-1",
                            "schema_": "1.0",
                            "timestamp": "2026-06-01T22:33:04Z",
                        }
                    ),
                    json.dumps(
                        {
                            "event": "artifact_edited",
                            "path": (
                                "docs/design/adr/foundation/"
                                "ADR-0.0.37-constitutional-invariant-composition/obpis/"
                                "OBPI-0.0.37-13-reverse-parse-migration.md"
                            ),
                            "id": "evt-2",
                            "schema_": "1.0",
                            "timestamp": "2026-06-01T22:55:23Z",
                        }
                    ),
                ],
            )
            errors = [
                e for e in _validate_task_envelope_coherence(root) if "Signature (a)" in e.message
            ]
            self.assertEqual(len(errors), 0)

    @covers("REQ-0.0.64-04-01")
    def test_brief_authoring_edit_before_own_pipeline_is_clean(self) -> None:
        """Authoring a brief (gz-obpi-specify) emits artifact_edited on
        /obpis/<X>.md BEFORE the pipeline starts X's own TASKs. While a
        *different* OBPI's TASKs are active, that ceremony edit must not be
        flagged as TASK-labor drift: brief edits (authoring OR closeout
        reflection) are OBPI ceremony, not REQ labor. The earlier carve-out
        required the brief's own OBPI to already have active TASKs, which missed
        pre-pipeline authoring (GHI #563; mirrors the ADR-decision-doc carve-out).
        """
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _write_ledger(
                root,
                [
                    json.dumps(
                        {
                            "event": "task_started",
                            "task_id": "TASK-0.0.37-26-01-01",
                            "obpi_id": (
                                "OBPI-0.0.37-26-codex-root-setpoint-"
                                "application-interim-attested-relief"
                            ),
                            "id": "evt-1",
                            "schema_": "1.0",
                            "timestamp": "2026-06-01T22:33:04Z",
                        }
                    ),
                    json.dumps(
                        {
                            "event": "artifact_edited",
                            "path": (
                                "docs/design/adr/foundation/"
                                "ADR-0.0.37-constitutional-invariant-composition/obpis/"
                                "OBPI-0.0.37-18-append-only-corpus-model.md"
                            ),
                            "id": "evt-2",
                            "schema_": "1.0",
                            "timestamp": "2026-06-05T00:28:11Z",
                        }
                    ),
                ],
            )
            errors = [
                e for e in _validate_task_envelope_coherence(root) if "Signature (a)" in e.message
            ]
            self.assertEqual(len(errors), 0)

    @covers("REQ-0.0.64-04-01")
    def test_pool_adr_edit_under_active_task_is_clean(self) -> None:
        """Editing a pool ADR (``ADR-pool.*``) is SUPPORT-channel governance
        ceremony, not OBPI-REQ TASK labor — the same carve-out reasoning as
        versioned ADR decision docs, and exactly the cross-workstream case GHI
        #563 designed this carve-out for: a pool-ADR backlog edit emitted while a
        *different* OBPI's pipeline TASKs are active must not trip Signature (a).
        """
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _write_ledger(
                root,
                [
                    json.dumps(
                        {
                            "event": "task_started",
                            "task_id": "TASK-0.0.69-03-01-01",
                            "obpi_id": "OBPI-0.0.69-03-closeout-proof-derived-view",
                            "id": "evt-1",
                            "schema_": "1.0",
                            "timestamp": "2026-06-10T10:00:00Z",
                        }
                    ),
                    json.dumps(
                        {
                            "event": "artifact_edited",
                            "path": (
                                "docs/design/adr/pool/ADR-pool.command-doctrine-internalization.md"
                            ),
                            "id": "evt-2",
                            "schema_": "1.0",
                            "timestamp": "2026-06-10T10:52:22Z",
                        }
                    ),
                ],
            )
            errors = [
                e for e in _validate_task_envelope_coherence(root) if "Signature (a)" in e.message
            ]
            self.assertEqual(len(errors), 0)

    @covers("REQ-0.0.64-04-01")
    def test_adr_decision_doc_edit_under_active_task_is_clean(self) -> None:
        """Editing an ADR decision doc is SUPPORT-channel governance ceremony,
        not OBPI-REQ TASK labor — excused both for the active OBPI's own parent
        ADR and for any other ADR amended in the same design session (cross-ADR
        redesign edits). Sibling of the brief-reflection carve-out, lifted to
        the ADR-decision-doc layer.
        """
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _write_ledger(
                root,
                [
                    json.dumps(
                        {
                            "event": "task_started",
                            "task_id": "TASK-0.0.37-17-01-01",
                            "obpi_id": "OBPI-0.0.37-17-agents-md-density-classification",
                            "id": "evt-1",
                            "schema_": "1.0",
                            "timestamp": "2026-06-03T10:41:00Z",
                        }
                    ),
                    json.dumps(
                        {
                            "event": "artifact_edited",
                            "path": (
                                "docs/design/adr/foundation/"
                                "ADR-0.0.37-constitutional-invariant-composition/"
                                "ADR-0.0.37-constitutional-invariant-composition.md"
                            ),
                            "id": "evt-2",
                            "schema_": "1.0",
                            "timestamp": "2026-06-03T11:51:10Z",
                        }
                    ),
                    json.dumps(
                        {
                            "event": "artifact_edited",
                            "path": (
                                "docs/design/adr/foundation/"
                                "ADR-0.0.33-agent-control-surface-fidelity/"
                                "ADR-0.0.33-agent-control-surface-fidelity.md"
                            ),
                            "id": "evt-3",
                            "schema_": "1.0",
                            "timestamp": "2026-06-03T11:54:12Z",
                        }
                    ),
                ],
            )
            errors = [
                e for e in _validate_task_envelope_coherence(root) if "Signature (a)" in e.message
            ]
            self.assertEqual(len(errors), 0)

    @covers("REQ-0.0.64-04-01")
    def test_support_manpage_edit_under_active_task_is_clean(self) -> None:
        """Editing a ``docs/user/manpages/`` manpage is SUPPORT-channel documentation,
        not OBPI-REQ TASK labor. SUPPORT-kind REQs (e.g. OBPI-0.0.41-02's REQ-09) are
        proven by the ``artifact_edited`` ledger event + ``gz validate --documents``
        per the REQ Scope Discipline taxonomy — the manpage edit IS the proof, not a
        per-REQ TASK labor record. Sibling of the ADR-decision-doc carve-out, lifted
        to the manpage layer (ordinary ``src/`` edits still require attribution; see
        ``test_worklog_without_task_id_under_active_task_fails``).
        """
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _write_ledger(
                root,
                [
                    json.dumps(
                        {
                            "event": "task_started",
                            "task_id": "TASK-0.0.41-02-01-01",
                            "obpi_id": "OBPI-0.0.41-02-claim-release-safety-primitives",
                            "id": "evt-1",
                            "schema_": "1.0",
                            "timestamp": "2026-06-07T10:13:00Z",
                        }
                    ),
                    json.dumps(
                        {
                            "event": "artifact_edited",
                            "path": "docs/user/manpages/obpi-lock-release.md",
                            "id": "evt-2",
                            "schema_": "1.0",
                            "timestamp": "2026-06-07T10:39:00Z",
                        }
                    ),
                    json.dumps(
                        {
                            "event": "artifact_edited",
                            "path": "docs/user/manpages/obpi-lock-claim.md",
                            "id": "evt-3",
                            "schema_": "1.0",
                            "timestamp": "2026-06-07T10:39:01Z",
                        }
                    ),
                ],
            )
            errors = [
                e for e in _validate_task_envelope_coherence(root) if "Signature (a)" in e.message
            ]
            self.assertEqual(len(errors), 0)

    @covers("REQ-0.0.64-04-01")
    def test_uncovered_accept_with_req_id_under_active_task_is_clean(self) -> None:
        """REQ-level uncovered-accept ceremony carries attribution via ``req_id``."""
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _write_ledger(
                root,
                [
                    json.dumps(
                        {
                            "event": "task_started",
                            "task_id": "TASK-0.0.37-13-06-01",
                            "obpi_id": "OBPI-0.0.37-13-reverse-parse-migration",
                            "id": "evt-1",
                            "schema_": "1.0",
                            "timestamp": "2026-06-01T22:33:04Z",
                        }
                    ),
                    json.dumps(
                        {
                            "event": "obpi_completion_uncovered_accept",
                            "id": "OBPI-0.0.37-13-reverse-parse-migration",
                            "obpi_id": "OBPI-0.0.37-13-reverse-parse-migration",
                            "req_id": "REQ-0.0.37-13-06",
                            "operator": "g0",
                            "rationale": "SUPPORT-kind proof channel.",
                            "acceptance_type": "agent-relayed-operator-attestation",
                            "schema_": "1.0",
                            "timestamp": "2026-06-01T23:57:26Z",
                        }
                    ),
                ],
            )
            errors = [
                e for e in _validate_task_envelope_coherence(root) if "Signature (a)" in e.message
            ]
            self.assertEqual(len(errors), 0)


class TestSignatureB(unittest.TestCase):
    """Signature (b): OBPI with all-seq=01 TASKs and no req_atomic exemption."""

    @covers("REQ-0.0.64-04-02")
    def test_obpi_all_seq01_no_req_atomic_fails(self) -> None:
        """All-seq=01 TASKs no req_atomic → signature (b); no other bypass exists."""
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _write_ledger(
                root,
                [
                    json.dumps(
                        {
                            "event": "task_started",
                            "task_id": "TASK-0.0.64-04-01-01",
                            "obpi_id": "OBPI-0.0.64-04",
                            "id": "evt-1",
                            "schema_": "1.0",
                            "timestamp": "2026-05-30T15:00:00Z",
                        }
                    ),
                    json.dumps(
                        {
                            "event": "obpi_receipt_emitted",
                            "receipt_event": "completed",
                            "id": "OBPI-0.0.64-04",
                            "schema_": "1.0",
                            "timestamp": "2026-05-30T15:10:00Z",
                        }
                    ),
                ],
            )
            _write_brief(root, _BASE_FM)
            errors = [
                e for e in _validate_task_envelope_coherence(root) if "Signature (b)" in e.message
            ]
            self.assertGreater(len(errors), 0, "Expected signature (b) violation")

    @covers("REQ-0.0.64-04-02")
    def test_obpi_all_seq01_req_atomic_covers_all_reqs_passes(self) -> None:
        """req_atomic covering all REQs → signature (b) suppressed entirely."""
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _write_ledger(
                root,
                [
                    json.dumps(
                        {
                            "event": "task_started",
                            "task_id": "TASK-0.0.64-04-01-01",
                            "obpi_id": "OBPI-0.0.64-04",
                            "id": "evt-1",
                            "schema_": "1.0",
                            "timestamp": "2026-05-30T15:00:00Z",
                        }
                    ),
                    json.dumps(
                        {
                            "event": "obpi_receipt_emitted",
                            "receipt_event": "completed",
                            "id": "OBPI-0.0.64-04",
                            "schema_": "1.0",
                            "timestamp": "2026-05-30T15:10:00Z",
                        }
                    ),
                ],
            )
            fm = {**_BASE_FM, "req_atomic": ["REQ-0.0.64-04-01"]}
            _write_brief(root, fm)
            errors = [
                e for e in _validate_task_envelope_coherence(root) if "Signature (b)" in e.message
            ]
            self.assertEqual(len(errors), 0)

    @covers("REQ-0.0.64-04-02")
    def test_obpi_seq02_exists_no_violation(self) -> None:
        """When seq=02 exists for a REQ on a completed OBPI, no signature (b) violation."""
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _write_ledger(
                root,
                [
                    json.dumps(
                        {
                            "event": "task_started",
                            "task_id": "TASK-0.0.64-04-01-01",
                            "obpi_id": "OBPI-0.0.64-04",
                            "id": "evt-1",
                            "schema_": "1.0",
                            "timestamp": "2026-05-30T15:00:00Z",
                        }
                    ),
                    json.dumps(
                        {
                            "event": "task_started",
                            "task_id": "TASK-0.0.64-04-01-02",
                            "obpi_id": "OBPI-0.0.64-04",
                            "id": "evt-2",
                            "schema_": "1.0",
                            "timestamp": "2026-05-30T15:01:00Z",
                        }
                    ),
                    json.dumps(
                        {
                            "event": "obpi_receipt_emitted",
                            "receipt_event": "completed",
                            "id": "OBPI-0.0.64-04",
                            "schema_": "1.0",
                            "timestamp": "2026-05-30T15:10:00Z",
                        }
                    ),
                ],
            )
            _write_brief(root, _BASE_FM)
            errors = [
                e for e in _validate_task_envelope_coherence(root) if "Signature (b)" in e.message
            ]
            self.assertEqual(len(errors), 0)

    @covers("REQ-0.0.64-04-02")
    def test_completed_full_slug_sees_short_form_seq02(self) -> None:
        """Repository-wide validation aggregates historical task ids by OBPI lineage."""
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            full_slug = "OBPI-0.0.64-04-task-envelope-and-planning-decomposition"
            _write_ledger(
                root,
                [
                    json.dumps(
                        {
                            "event": "task_started",
                            "task_id": "TASK-0.0.64-04-01-01",
                            "obpi_id": full_slug,
                            "timestamp": "2026-07-10T10:12:00Z",
                        }
                    ),
                    json.dumps(
                        {
                            "event": "task_started",
                            "task_id": "TASK-0.0.64-04-01-02",
                            "obpi_id": "OBPI-0.0.64-04",
                            "timestamp": "2026-07-10T10:13:00Z",
                        }
                    ),
                    json.dumps(
                        {
                            "event": "obpi_receipt_emitted",
                            "receipt_event": "completed",
                            "id": full_slug,
                            "timestamp": "2026-07-10T10:20:00Z",
                        }
                    ),
                ],
            )
            _write_brief(root, {**_BASE_FM, "id": full_slug, "status": "Completed"})

            errors = [
                e for e in _validate_task_envelope_coherence(root) if "Signature (b)" in e.message
            ]

            self.assertEqual(errors, [])

    @covers("REQ-0.0.64-04-02")
    def test_completed_full_slug_does_not_activate_short_only_legacy_channel(self) -> None:
        """A historical short-only channel remains outside prospective enforcement."""
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            full_slug = "OBPI-0.0.64-04-task-envelope-and-planning-decomposition"
            _write_ledger(
                root,
                [
                    json.dumps(
                        {
                            "event": "task_started",
                            "task_id": "TASK-0.0.64-04-01-01",
                            "obpi_id": "OBPI-0.0.64-04",
                            "timestamp": "2026-06-01T10:00:00Z",
                        }
                    ),
                    json.dumps(
                        {
                            "event": "obpi_receipt_emitted",
                            "receipt_event": "completed",
                            "id": full_slug,
                            "timestamp": "2026-06-01T10:10:00Z",
                        }
                    ),
                ],
            )
            _write_brief(root, {**_BASE_FM, "id": full_slug, "status": "Completed"})

            errors = [
                e for e in _validate_task_envelope_coherence(root) if "Signature (b)" in e.message
            ]

            self.assertEqual(errors, [])

    @covers("REQ-0.0.64-04-02")
    def test_historical_completed_obpi_before_enforcement_epoch_is_clean(self) -> None:
        """Closed pre-recovery default-bucket OBPIs do not block the prospective gate."""
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _write_ledger(
                root,
                [
                    json.dumps(
                        {
                            "event": "task_started",
                            "task_id": "TASK-0.0.64-04-01-01",
                            "obpi_id": "OBPI-0.0.64-04",
                            "id": "evt-1",
                            "schema_": "1.0",
                            "timestamp": "2026-05-30T14:43:59Z",
                        }
                    ),
                    json.dumps(
                        {
                            "event": "obpi_receipt_emitted",
                            "receipt_event": "completed",
                            "id": "OBPI-0.0.64-04",
                            "schema_": "1.0",
                            "timestamp": "2026-05-30T14:43:59Z",
                        }
                    ),
                ],
            )
            _write_brief(root, _BASE_FM)
            errors = [
                e for e in _validate_task_envelope_coherence(root) if "Signature (b)" in e.message
            ]
            self.assertEqual(len(errors), 0)


class TestSignatureC(unittest.TestCase):
    """Signature (c): layer-drift across frontmatter tasks: and ledger task_id."""

    @covers("REQ-0.0.64-04-03")
    def test_layer_drift_frontmatter_vs_ledger_fails(self) -> None:
        """Different TASK IDs in frontmatter tasks: vs ledger task_started → drift violation."""
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            # Ledger channel (ch4) is built from task_started events with obpi_id
            _write_ledger(
                root,
                [
                    json.dumps(
                        {
                            "event": "task_started",
                            "task_id": "TASK-0.0.64-04-01-02",  # ch4 says TASK-02
                            "obpi_id": "OBPI-0.0.64-04",
                            "id": "evt-1",
                            "schema_": "1.0",
                            "timestamp": "2026-05-30T15:00:00Z",
                        }
                    ),
                ],
            )
            # ch2 (frontmatter) says TASK-01, ch4 (ledger) says TASK-02 → drift
            fm = {**_BASE_FM, "tasks": ["TASK-0.0.64-04-01-01"]}
            _write_brief(root, fm)
            errors = [
                e
                for e in _validate_task_envelope_coherence(root)
                if "Signature (c)" in e.message or "layer-drift" in e.message.lower()
            ]
            self.assertGreater(len(errors), 0, "Expected layer-drift violation")

    @covers("REQ-0.0.64-04-03")
    def test_same_task_id_all_channels_passes(self) -> None:
        """Same TASK ID in frontmatter tasks: and ledger task_started → no drift."""
        task_id = "TASK-0.0.64-04-01-01"
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _write_ledger(
                root,
                [
                    json.dumps(
                        {
                            "event": "task_started",
                            "task_id": task_id,
                            "obpi_id": "OBPI-0.0.64-04",
                            "id": "evt-1",
                            "schema_": "1.0",
                            "timestamp": "2026-05-30T15:00:00Z",
                        }
                    ),
                ],
            )
            fm = {**_BASE_FM, "tasks": [task_id]}
            _write_brief(root, fm)
            errors = [
                e
                for e in _validate_task_envelope_coherence(root)
                if "Signature (c)" in e.message or "layer-drift" in e.message.lower()
            ]
            self.assertEqual(len(errors), 0)

    @covers("REQ-0.0.64-04-03")
    def test_only_one_channel_populated_no_drift(self) -> None:
        """Drift requires two channels; one populated → no violation."""
        task_id = "TASK-0.0.64-04-01-01"
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _write_ledger(
                root,
                [
                    json.dumps(
                        {
                            "event": "artifact_edited",
                            "path": "src/foo.py",
                            "id": "evt-1",
                            "schema_": "1.0",
                            "timestamp": "2026-05-30T15:00:00Z",
                        }
                    ),
                ],
            )
            # ch2 has tasks, ch4 has nothing → no drift (one channel only)
            fm = {**_BASE_FM, "tasks": [task_id]}
            _write_brief(root, fm)
            errors = [
                e
                for e in _validate_task_envelope_coherence(root)
                if "Signature (c)" in e.message or "layer-drift" in e.message.lower()
            ]
            self.assertEqual(len(errors), 0)


def _after_cutover(hours: int) -> str:
    """Return an ISO timestamp AFTER the obpi_id canonicalization cutover.

    Derived from `_OBPI_ID_CANONICAL_CUTOVER` rather than hardcoded: the cutover
    advances whenever the producer is repaired again, and a literal date slides
    to the tolerated side of it, so the divergence this fixture stages stops
    firing (observed 2026-07-29, when the fixture's `2026-07-11` literal fell
    behind an advanced cutover).

    That rot is LOUD, not silent — the assertion is `assertGreater(len(errors), 0)`,
    so the test FAILS rather than passing vacuously; measured by advancing
    `_TASK_ENVELOPE_ENFORCEMENT_EPOCH` a year, which produced 4 failures and 0
    silent passes. Deriving the timestamp is still correct: it re-anchors the
    fixture automatically instead of presenting a red test whose obvious "fix"
    is to weaken the assertion.
    """
    from datetime import timedelta

    from gzkit.commands.validate_task_envelope import _OBPI_ID_CANONICAL_CUTOVER

    return (_OBPI_ID_CANONICAL_CUTOVER + timedelta(hours=hours)).isoformat()


class TestSignatureD(unittest.TestCase):
    """Signature (d): a single task_id carries divergent obpi_id across events (GHI #653).

    A ``task_id`` maps to exactly one OBPI, so every TASK-lifecycle event must
    carry the same canonical ``obpi_id``. Two spellings (short
    ``OBPI-<semver>-<item>`` vs the full slug ``gz obpi pipeline`` records) were
    the producer defect behind the Signature (a) false positives; the read-side
    walk was hardened in ef976e88 and this guard fail-closes on the producer side.
    """

    @covers("REQ-0.0.64-04-01")
    def test_divergent_obpi_id_across_lifecycle_fails(self) -> None:
        """task_started + task_completed under different obpi_id for one task_id → Sig (d)."""
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _write_ledger(
                root,
                [
                    json.dumps(
                        {
                            "event": "task_started",
                            "task_id": "TASK-0.0.99-01-01-01",
                            "obpi_id": "OBPI-0.0.99-01",
                            "id": "evt-1",
                            "schema_": "1.0",
                            "timestamp": _after_cutover(1),
                        }
                    ),
                    json.dumps(
                        {
                            "event": "task_completed",
                            "task_id": "TASK-0.0.99-01-01-01",
                            "obpi_id": "OBPI-0.0.99-01-full-slug-suffix",
                            "id": "evt-2",
                            "schema_": "1.0",
                            "timestamp": _after_cutover(2),
                        }
                    ),
                ],
            )
            errors = [
                e for e in _validate_task_envelope_coherence(root) if "Signature (d)" in e.message
            ]
            self.assertGreater(len(errors), 0, "Expected Signature (d) divergence violation")

    @covers("REQ-0.0.64-04-01")
    def test_same_lineage_divergence_before_regression_cutover_passes(self) -> None:
        """Append-only rows emitted before the repaired producer remain readable."""
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _write_ledger(
                root,
                [
                    json.dumps(
                        {
                            "event": "task_started",
                            "task_id": "TASK-0.44.0-01-01-01",
                            "obpi_id": "OBPI-0.44.0-01-full-slug",
                            "timestamp": "2026-07-10T10:13:00Z",
                        }
                    ),
                    json.dumps(
                        {
                            "event": "task_completed",
                            "task_id": "TASK-0.44.0-01-01-01",
                            "obpi_id": "OBPI-0.44.0-01",
                            "timestamp": "2026-07-10T10:13:30Z",
                        }
                    ),
                ],
            )

            errors = [
                e for e in _validate_task_envelope_coherence(root) if "Signature (d)" in e.message
            ]

            self.assertEqual(errors, [])

    @covers("REQ-0.0.64-04-01")
    def test_consistent_obpi_id_passes(self) -> None:
        """Same obpi_id on every lifecycle event → no Signature (d)."""
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _write_ledger(
                root,
                [
                    json.dumps(
                        {
                            "event": "task_started",
                            "task_id": "TASK-0.0.99-01-01-01",
                            "obpi_id": "OBPI-0.0.99-01-full-slug-suffix",
                            "id": "evt-1",
                            "schema_": "1.0",
                            "timestamp": "2026-07-01T10:00:00Z",
                        }
                    ),
                    json.dumps(
                        {
                            "event": "task_completed",
                            "task_id": "TASK-0.0.99-01-01-01",
                            "obpi_id": "OBPI-0.0.99-01-full-slug-suffix",
                            "id": "evt-2",
                            "schema_": "1.0",
                            "timestamp": "2026-07-01T11:00:00Z",
                        }
                    ),
                ],
            )
            errors = [
                e for e in _validate_task_envelope_coherence(root) if "Signature (d)" in e.message
            ]
            self.assertEqual(len(errors), 0)

    @covers("REQ-0.0.64-04-01")
    def test_grandfathered_historical_divergence_passes(self) -> None:
        """The two pre-existing divergent task_ids are grandfathered (shrink-only)."""
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _write_ledger(
                root,
                [
                    json.dumps(
                        {
                            "event": "task_started",
                            "task_id": "TASK-0.0.74-20-01-01",
                            "obpi_id": "OBPI-0.0.74-20",
                            "id": "evt-1",
                            "schema_": "1.0",
                            "timestamp": "2026-06-24T00:45:33Z",
                        }
                    ),
                    json.dumps(
                        {
                            "event": "task_completed",
                            "task_id": "TASK-0.0.74-20-01-01",
                            "obpi_id": "OBPI-0.0.74-20-mx-gz-check-step-checkpoint-seam",
                            "id": "evt-2",
                            "schema_": "1.0",
                            "timestamp": "2026-06-24T01:03:36Z",
                        }
                    ),
                ],
            )
            errors = [
                e for e in _validate_task_envelope_coherence(root) if "Signature (d)" in e.message
            ]
            self.assertEqual(len(errors), 0, "grandfathered task_id must not trip Signature (d)")


class TestCheckPipelineIntegration(unittest.TestCase):
    """REQ-0.0.64-04-06: validator is registered in the gz check pipeline."""

    def test_task_envelope_coherence_in_gz_check_steps(self) -> None:
        """gz check pipeline includes 'Task envelope coherence' step."""
        from gzkit.commands.quality import _build_check_steps

        step_names = [name for name, _ in _build_check_steps()]
        self.assertIn("Task envelope coherence", step_names)


class TestDiagnoseCmd(unittest.TestCase):
    """REQ-0.0.64-04-05: gz task envelope diagnose renders all four channels."""

    @covers("REQ-0.0.64-04-05")
    def test_diagnose_renders_all_four_channels(self) -> None:
        """The diagnose readback reads and renders ALL FOUR discovery channels.

        Regression guard for the 2-of-4 bug: `@advances` (ch1) and commit
        trailers (ch3) were previously hardcoded empty, so the ADR's named
        layer-drift recovery surface was blind to the exact channels the
        validator's signature (c) evaluates. The command must delegate to the
        validator's four-channel collector so a declaration in ANY channel
        surfaces in the readback and participates in drift. If the command
        regressed to a 2-channel subset, ch1/ch3 would render empty and this
        test fails.
        """
        import contextlib  # noqa: PLC0415
        import io  # noqa: PLC0415

        from gzkit.commands import task as task_cmd  # noqa: PLC0415

        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _write_brief(root, {**_BASE_FM, "tasks": ["TASK-0.0.64-04-01-02"]})
            # Distinct declarations in each of the four channels: the fix must
            # surface all four, the old 2-channel version rendered ch1/ch3 empty.
            fake_decls = {
                "advances": {"TASK-0.0.64-04-01-01"},
                "frontmatter": {"TASK-0.0.64-04-01-02"},
                "commit_trailer": {"TASK-0.0.64-04-01-03"},
                "ledger": {"TASK-0.0.64-04-01-04"},
            }
            buf = io.StringIO()
            with (
                mock.patch.object(task_cmd, "get_project_root", return_value=root),
                mock.patch.object(
                    validate_task_envelope,
                    "_channel_declarations_for_obpi",
                    return_value=fake_decls,
                ),
                contextlib.redirect_stdout(buf),
            ):
                task_cmd.task_envelope_diagnose_cmd("OBPI-0.0.64-04", as_json=True)

            channels = json.loads(buf.getvalue())["channels"]
            self.assertEqual(channels["@advances (ch1)"], ["TASK-0.0.64-04-01-01"])
            self.assertEqual(channels["frontmatter tasks: (ch2)"], ["TASK-0.0.64-04-01-02"])
            self.assertEqual(channels["commit trailers (ch3)"], ["TASK-0.0.64-04-01-03"])
            self.assertEqual(channels["ledger task_id (ch4)"], ["TASK-0.0.64-04-01-04"])
            self.assertTrue(json.loads(buf.getvalue())["drift"])


class TestFrontmatterChannelFullSlugResolution(unittest.TestCase):
    """ch2 must resolve a brief whose ``id:`` carries the authored full slug (GHI #946).

    Briefs are authored with the full slug in ``id:``
    (``OBPI-0.35.0-04-section-ownership-and-ratchet``), while the three TASK-id
    channels resolve on the bare ``OBPI-<semver>-<NN>`` form — ``_task_matches_obpi``
    reconstructs exactly that shape out of a TASK id and compares it for equality.
    ``_channel_declarations_for_obpi`` hands ONE id to all four collectors, so
    whichever form the caller picks, the other side cannot match. The caller picked
    bare, so the frontmatter map — keyed on the authored slug — missed for EVERY
    real brief and ch2 read empty everywhere.

    That is invisible rather than loud: ``drift`` is computed over
    ``populated = [s for s in decls.values() if s]``, so a structurally empty channel
    is dropped from the comparison instead of disagreeing with it. The named
    layer-drift recovery view reports a clean or partial verdict over a channel it
    cannot see.

    The fixtures elsewhere in this file set ``id: OBPI-0.0.64-04`` — the bare form,
    not the authored convention — which is why the existing diagnose test passed
    while the shipped command was blind. That test also mocks
    ``_channel_declarations_for_obpi`` outright, so it pins rendering and never
    resolution.
    """

    def test_a_full_slug_brief_resolves_from_the_bare_obpi_id(self) -> None:
        """The bare id the other three channels require must still find the brief."""
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _write_brief(
                root,
                {
                    **_BASE_FM,
                    "id": "OBPI-0.0.64-04-fixture",
                    "tasks": ["TASK-0.0.64-04-01-01", "TASK-0.0.64-04-02-01"],
                },
            )
            found = validate_task_envelope._frontmatter_channel_for_obpi(root, "OBPI-0.0.64-04")
            self.assertEqual(found, {"TASK-0.0.64-04-01-01", "TASK-0.0.64-04-02-01"})

    def test_a_full_slug_query_resolves_the_same_brief(self) -> None:
        """Either spelling names one OBPI, so either must reach the same tasks."""
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _write_brief(
                root,
                {**_BASE_FM, "id": "OBPI-0.0.64-04-fixture", "tasks": ["TASK-0.0.64-04-01-01"]},
            )
            self.assertEqual(
                validate_task_envelope._frontmatter_channel_for_obpi(
                    root, "OBPI-0.0.64-04-fixture"
                ),
                {"TASK-0.0.64-04-01-01"},
            )

    def test_a_bare_form_brief_still_resolves(self) -> None:
        """Briefs authored with a bare ``id:`` must not regress — exact hit stays first."""
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _write_brief(root, {**_BASE_FM, "tasks": ["TASK-0.0.64-04-01-01"]})
            self.assertEqual(
                validate_task_envelope._frontmatter_channel_for_obpi(root, "OBPI-0.0.64-04"),
                {"TASK-0.0.64-04-01-01"},
            )

    def test_a_different_obpi_does_not_borrow_this_briefs_tasks(self) -> None:
        """Widening the lookup must not make ch2 answer for an unrelated OBPI.

        The fallback matches on the bare form, so it must still distinguish
        ``-04`` from ``-05``; a prefix/substring widening would not.
        """
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _write_brief(
                root,
                {**_BASE_FM, "id": "OBPI-0.0.64-04-fixture", "tasks": ["TASK-0.0.64-04-01-01"]},
            )
            self.assertEqual(
                validate_task_envelope._frontmatter_channel_for_obpi(root, "OBPI-0.0.64-05"),
                set(),
            )

    def test_diagnose_renders_ch2_for_a_full_slug_brief(self) -> None:
        """End-to-end: the recovery view must show the tasks the brief declares.

        Deliberately does NOT mock ``_channel_declarations_for_obpi`` — the defect
        lives in the resolution the existing diagnose test mocks away.
        """
        import contextlib  # noqa: PLC0415
        import io  # noqa: PLC0415

        from gzkit.commands import task as task_cmd  # noqa: PLC0415

        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _write_brief(
                root,
                {
                    **_BASE_FM,
                    "id": "OBPI-0.0.64-04-fixture",
                    "tasks": ["TASK-0.0.64-04-01-01", "TASK-0.0.64-04-02-01"],
                },
            )
            buf = io.StringIO()
            with (
                mock.patch.object(task_cmd, "get_project_root", return_value=root),
                contextlib.redirect_stdout(buf),
            ):
                task_cmd.task_envelope_diagnose_cmd("OBPI-0.0.64-04-fixture", as_json=True)

            payload = json.loads(buf.getvalue())
            self.assertEqual(
                payload["channels"]["frontmatter tasks: (ch2)"],
                ["TASK-0.0.64-04-01-01", "TASK-0.0.64-04-02-01"],
            )


class TestSignatureCCommitTrailerChannel(unittest.TestCase):
    """Signature (c): the commit-trailer channel participates in drift detection.

    The temp-dir fixtures elsewhere are not git repos, so the commit-trailer
    channel is never exercised there. These mock the single ``git log`` walk to
    pin that commit-trailer declarations still feed drift detection across the
    hoisted (once-per-audit) code path.
    """

    @covers("REQ-0.0.64-04-03")
    def test_layer_drift_commit_trailer_vs_frontmatter_fails(self) -> None:
        """A commit-trailer TASK id disagreeing with frontmatter → drift violation."""
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            fm = {**_BASE_FM, "tasks": ["TASK-0.0.64-04-01-01"]}
            _write_brief(root, fm)
            # Commit trailer declares a DIFFERENT TASK for the same OBPI.
            git_log = "fix(x): change\n\nTask: TASK-0.0.64-04-01-02\n--EOC--\n"
            fake = mock.Mock(returncode=0, stdout=git_log)
            with mock.patch.object(validate_task_envelope.subprocess, "run", return_value=fake):
                errors = [
                    e
                    for e in _validate_task_envelope_coherence(root)
                    if "Signature (c)" in e.message or "layer-drift" in e.message.lower()
                ]
            self.assertGreater(len(errors), 0, "Expected commit-trailer vs frontmatter drift")

    @covers("REQ-0.0.64-04-03")
    def test_commit_trailer_agreeing_with_frontmatter_passes(self) -> None:
        """Same TASK id in commit trailer and frontmatter → no drift."""
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            fm = {**_BASE_FM, "tasks": ["TASK-0.0.64-04-01-01"]}
            _write_brief(root, fm)
            git_log = "fix(x): change\n\nTask: TASK-0.0.64-04-01-01\n--EOC--\n"
            fake = mock.Mock(returncode=0, stdout=git_log)
            with mock.patch.object(validate_task_envelope.subprocess, "run", return_value=fake):
                errors = [
                    e
                    for e in _validate_task_envelope_coherence(root)
                    if "Signature (c)" in e.message or "layer-drift" in e.message.lower()
                ]
            self.assertEqual(len(errors), 0)


class TestSignatureCSubsetIsNotDrift(unittest.TestCase):
    """Signature (c) fires on CONTRADICTION, never on incompleteness (GHI #820).

    `.claude/rules/task-discovery.md` § Layer-drift fail-close defines drift as a
    unit of labor surfacing "with **different TASK IDs**" across channels. A
    channel naming FEWER TASKs contradicts nothing.

    The distinction is load-bearing rather than pedantic, because the channels
    populate on incompatible schedules: `gz obpi pipeline` writes every
    `task_started` event AT LAUNCH, while commit trailers accrete one commit at a
    time. Under set-equality the two can agree only if every commit carries every
    TASK's trailer — falsified attribution, which the same rule forbids by name.
    A gate satisfiable only by the act its rule prohibits is worse than no gate.
    """

    @covers("REQ-0.0.64-04-03")
    def test_trailer_subset_of_ledger_is_not_drift(self) -> None:
        """A commit-trailer channel naming a SUBSET of declared TASKs must not fire."""
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            fm = {
                **_BASE_FM,
                "tasks": ["TASK-0.0.64-04-01-01", "TASK-0.0.64-04-01-02"],
            }
            _write_brief(root, fm)
            # One commit landed so far, naming one of the two declared TASKs.
            git_log = "fix(x): first increment\n\nTask: TASK-0.0.64-04-01-01\n--EOC--\n"
            fake = mock.Mock(returncode=0, stdout=git_log)
            with mock.patch.object(validate_task_envelope.subprocess, "run", return_value=fake):
                errors = [
                    e
                    for e in _validate_task_envelope_coherence(root)
                    if "Signature (c)" in e.message or "layer-drift" in e.message.lower()
                ]
            self.assertEqual(
                errors,
                [],
                "A trailer channel naming a subset of the declared TASKs names no TASK "
                "the other channels lack, so it contradicts nothing and must not "
                "report layer-drift (GHI #820).",
            )

    @covers("REQ-0.0.64-04-03")
    def test_contradiction_still_fires_under_the_narrowed_predicate(self) -> None:
        """The real signal survives: a channel holding an id no other channel knows fires."""
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            fm = {
                **_BASE_FM,
                "tasks": ["TASK-0.0.64-04-01-01", "TASK-0.0.64-04-01-02"],
            }
            _write_brief(root, fm)
            # Trailer names a THIRD TASK that no other channel declares.
            git_log = "fix(x): change\n\nTask: TASK-0.0.64-04-01-09\n--EOC--\n"
            fake = mock.Mock(returncode=0, stdout=git_log)
            with mock.patch.object(validate_task_envelope.subprocess, "run", return_value=fake):
                errors = [
                    e
                    for e in _validate_task_envelope_coherence(root)
                    if "Signature (c)" in e.message or "layer-drift" in e.message.lower()
                ]
            self.assertGreater(
                len(errors),
                0,
                "Narrowing the predicate must not disarm it: a channel naming a TASK "
                "no other channel knows is the contradiction the rule describes.",
            )


class TestSignatureCPerformance(unittest.TestCase):
    """Signature (c) scans git history once per audit, not once per OBPI."""

    @covers("REQ-0.0.64-04-03")
    def test_commit_history_scanned_once_regardless_of_obpi_count(self) -> None:
        """The git-log commit-trailer scan runs once per audit, not once per brief.

        Regression guard for the O(N) subprocess pattern: a fresh ``git log``
        per OBPI (562 briefs on this repo) made this audit the single largest
        time sink in ``gz check``. The semantic guarantee is that the number of
        git invocations is independent of the brief count.
        """
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            for obpi_id in ("OBPI-0.0.64-91", "OBPI-0.0.64-92", "OBPI-0.0.64-93"):
                _write_brief_with_id(root, obpi_id)
            fake = mock.Mock(returncode=0, stdout="")
            with mock.patch.object(
                validate_task_envelope.subprocess, "run", return_value=fake
            ) as run_mock:
                validate_task_envelope._sig_c_layer_drift(root)
            self.assertEqual(
                run_mock.call_count,
                1,
                "git history must be scanned once per audit, not once per OBPI "
                f"(saw {run_mock.call_count} subprocess calls for 3 briefs)",
            )


class TestObpiIdForTask(unittest.TestCase):
    """The TASK→OBPI grouping key mirrors ``_task_matches_obpi`` exactly."""

    @covers("REQ-0.0.64-04-03")
    def test_grouping_key_agrees_with_task_matches_obpi(self) -> None:
        """``_obpi_id_for_task`` returns the one OBPI a TASK matches (or None)."""
        from gzkit.commands.validate_task_envelope import _obpi_id_for_task, _task_matches_obpi

        cases = [
            "TASK-0.0.64-04-01-01",
            "TASK-1.2.3-07-02-05",
            "TASK-task-spine-restoration-#552",  # slug-form: no OBPI parent
            "not-a-task",
        ]
        for tid in cases:
            obpi = _obpi_id_for_task(tid)
            if obpi is None:
                self.assertFalse(
                    _task_matches_obpi(tid, "OBPI-0.0.64-04"),
                    f"{tid!r} mapped to no OBPI but matched one",
                )
            else:
                self.assertTrue(
                    _task_matches_obpi(tid, obpi),
                    f"{tid!r} mapped to {obpi!r} but did not match it",
                )
        self.assertEqual(_obpi_id_for_task("TASK-0.0.64-04-01-01"), "OBPI-0.0.64-04")
        self.assertIsNone(_obpi_id_for_task("TASK-task-spine-restoration-#552"))


class TestPendingObpiSigB(unittest.TestCase):
    """Scoped Signature-(b) check for an OBPI about to be completed (GHI #590).

    The chokepoint variant predicts the same residue the repo-wide validator
    flags, but *before* the completion event exists — so `gz obpi complete` can
    fail closed before the residue ever reaches `gz check`. Fixtures use
    full-slug ids matching the real ledger `task_started.obpi_id` shape, which
    guards the short-vs-full obpi_id divergence (a mismatch would make the check
    silently find zero tasks and pass — a false negative).
    """

    @covers("REQ-0.0.64-04-02")
    def test_residue_flagged_before_completion_event(self) -> None:
        """seq=01-only + no req_atomic → Sig(b) error, with NO completion event present."""
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            # Deliberately omit obpi_receipt_emitted/completed: the chokepoint
            # check must predict residue at completion time, not after.
            _write_ledger(
                root,
                [
                    json.dumps(
                        {
                            "event": "task_started",
                            "task_id": "TASK-0.0.64-04-01-01",
                            "obpi_id": "OBPI-0.0.64-04",
                            "id": "evt-1",
                            "schema_": "1.0",
                            "timestamp": "2026-05-30T15:00:00Z",
                        }
                    )
                ],
            )
            brief_path = _write_brief(root, _BASE_FM)
            err = validate_task_envelope.pending_obpi_sig_b_error(root, brief_path)
            self.assertIsNotNone(err, "Expected Sig(b) error for seq=01-only-without-req_atomic")
            assert err is not None  # narrow for type-checker
            self.assertIn("Signature (b)", err.message)

    @covers("REQ-0.0.64-04-02")
    def test_req_atomic_clears_pending_check(self) -> None:
        """req_atomic covering all REQs → no Sig(b) error at the chokepoint."""
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _write_ledger(
                root,
                [
                    json.dumps(
                        {
                            "event": "task_started",
                            "task_id": "TASK-0.0.64-04-01-01",
                            "obpi_id": "OBPI-0.0.64-04",
                            "id": "evt-1",
                            "schema_": "1.0",
                            "timestamp": "2026-05-30T15:00:00Z",
                        }
                    )
                ],
            )
            brief_path = _write_brief(root, {**_BASE_FM, "req_atomic": ["REQ-0.0.64-04-01"]})
            err = validate_task_envelope.pending_obpi_sig_b_error(root, brief_path)
            self.assertIsNone(err)

    @covers("REQ-0.0.64-04-02")
    def test_full_slug_brief_sees_short_form_subdivision_events(self) -> None:
        """seq=02 under the short spelling satisfies the full-slug chokepoint."""
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            full_slug = "OBPI-0.0.64-04-full-slug"
            _write_ledger(
                root,
                [
                    json.dumps(
                        {
                            "event": "task_started",
                            "task_id": "TASK-0.0.64-04-01-01",
                            "obpi_id": full_slug,
                        }
                    ),
                    json.dumps(
                        {
                            "event": "task_started",
                            "task_id": "TASK-0.0.64-04-01-02",
                            "obpi_id": "OBPI-0.0.64-04",
                        }
                    ),
                ],
            )
            brief_path = _write_brief(root, {**_BASE_FM, "id": full_slug})

            err = validate_task_envelope.pending_obpi_sig_b_error(root, brief_path)

            self.assertIsNone(err)


class TestPendingObpiAllSignatures(unittest.TestCase):
    """The chokepoint scopes ALL THREE task-envelope signatures, not just Sig (b) (GHI #590).

    `gz check` fails on Sig (a) (unattributed labor), Sig (b) (seq=01-only), and
    Sig (c) (layer-drift). The completion chokepoint must predict all three for the
    pending OBPI, or an OBPI can pass `gz obpi complete` clean and still reopen
    Tier 0 on the next session.
    """

    @covers("REQ-0.0.64-04-01")
    def test_sig_a_unattributed_labor_flagged(self) -> None:
        """A worklog event under this OBPI's active TASK with no task_id → Sig (a)."""
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _write_ledger(
                root,
                [
                    json.dumps(
                        {
                            "event": "task_started",
                            "task_id": "TASK-0.0.64-04-01-01",
                            "obpi_id": "OBPI-0.0.64-04",
                            "id": "evt-1",
                            "schema_": "1.0",
                            "timestamp": "2026-05-30T15:00:00Z",
                        }
                    ),
                    # A worklog event with NO task_id while the TASK is active.
                    # Was `artifact_edited` on a plain src/ path until GHI #947
                    # removed that type from `_TASK_WORKLOG_TYPES`; `gate_checked`
                    # carries a `task_id` and has no carve-out, so signature (a)
                    # is still exercised on its own terms.
                    json.dumps(
                        {
                            "event": "gate_checked",
                            "obpi_id": "OBPI-0.0.64-04",
                            "id": "evt-2",
                            "schema_": "1.0",
                            "timestamp": "2026-05-30T15:01:00Z",
                        }
                    ),
                ],
            )
            # req_atomic suppresses Sig (b) so Sig (a) is isolated.
            brief_path = _write_brief(root, {**_BASE_FM, "req_atomic": ["REQ-0.0.64-04-01"]})
            errs = validate_task_envelope.pending_obpi_task_envelope_errors(root, brief_path)
            self.assertTrue(
                any("Signature (a)" in e.message for e in errs), [e.message for e in errs]
            )

    @covers("REQ-0.0.64-04-01")
    def test_sig_a_attributed_labor_is_clean(self) -> None:
        """The same worklog event WITH a task_id raises no Sig (a) error."""
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _write_ledger(
                root,
                [
                    json.dumps(
                        {
                            "event": "task_started",
                            "task_id": "TASK-0.0.64-04-01-01",
                            "obpi_id": "OBPI-0.0.64-04",
                            "id": "evt-1",
                            "schema_": "1.0",
                            "timestamp": "2026-05-30T15:00:00Z",
                        }
                    ),
                    json.dumps(
                        {
                            "event": "artifact_edited",
                            "obpi_id": "OBPI-0.0.64-04",
                            "task_id": "TASK-0.0.64-04-01-01",
                            "path": "src/gzkit/foo.py",
                            "id": "evt-2",
                            "schema_": "1.0",
                            "timestamp": "2026-05-30T15:01:00Z",
                        }
                    ),
                ],
            )
            brief_path = _write_brief(root, {**_BASE_FM, "req_atomic": ["REQ-0.0.64-04-01"]})
            errs = validate_task_envelope.pending_obpi_task_envelope_errors(root, brief_path)
            self.assertFalse(any("Signature (a)" in e.message for e in errs))

    @covers("REQ-0.0.64-04-03")
    def test_sig_c_layer_drift_flagged(self) -> None:
        """Frontmatter tasks: and ledger task_started declare different TASKs → Sig (c)."""
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _write_ledger(
                root,
                [
                    json.dumps(
                        {
                            "event": "task_started",
                            "task_id": "TASK-0.0.64-04-01-02",
                            "obpi_id": "OBPI-0.0.64-04",
                            "id": "evt-1",
                            "schema_": "1.0",
                            "timestamp": "2026-05-30T15:00:00Z",
                        }
                    )
                ],
            )
            brief_path = _write_brief(root, {**_BASE_FM, "tasks": ["TASK-0.0.64-04-01-01"]})
            errs = validate_task_envelope.pending_obpi_task_envelope_errors(root, brief_path)
            self.assertTrue(
                any("Signature (c)" in e.message for e in errs), [e.message for e in errs]
            )

    @covers("REQ-0.0.64-04-02")
    def test_sig_b_flagged_through_combined_entrypoint(self) -> None:
        """seq=01-only without req_atomic is still caught via the combined entry point."""
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _write_ledger(
                root,
                [
                    json.dumps(
                        {
                            "event": "task_started",
                            "task_id": "TASK-0.0.64-04-01-01",
                            "obpi_id": "OBPI-0.0.64-04",
                            "id": "evt-1",
                            "schema_": "1.0",
                            "timestamp": "2026-05-30T15:00:00Z",
                        }
                    )
                ],
            )
            brief_path = _write_brief(root, _BASE_FM)
            errs = validate_task_envelope.pending_obpi_task_envelope_errors(root, brief_path)
            self.assertTrue(any("Signature (b)" in e.message for e in errs))


class TestPoolDemotionAttributionCutover(unittest.TestCase):
    """The ADR-0.34.0 cutover must be narrow and must EXPIRE (ADR-0.34.0 OBPI-04).

    `gz adr demote`'s `artifact_renamed` producer went unattributed until
    OBPI-0.34.0-04 repaired it. The ledger is append-only, so the rows that
    producer already wrote are grandfathered — but a grandfather that never
    expires is just a hole. These pin the four edges of the predicate so it can
    only ever tolerate the measured 51 pre-cutover `pool_demotion` renames.
    """

    def test_a_pre_cutover_unattributed_demotion_is_tolerated(self) -> None:
        self.assertTrue(
            validate_task_envelope._sig_a_is_grandfathered_demotion(
                {"reason": "pool_demotion", "ts": "2026-07-30T08:54:12+00:00"},
                "artifact_renamed",
                None,
            )
        )

    def test_a_post_cutover_unattributed_demotion_still_fails(self) -> None:
        """The expiry: a demotion run after the repair MUST carry task_id."""
        self.assertFalse(
            validate_task_envelope._sig_a_is_grandfathered_demotion(
                {"reason": "pool_demotion", "ts": "2026-08-01T00:00:00+00:00"},
                "artifact_renamed",
                None,
            )
        )


class TestSignatureE(unittest.TestCase):
    """Signature (e): a brief's ``tasks:`` entry names an unresolvable TASK (GHI #753).

    ``.gzkit/rules/task-discovery.md`` promised this enforcement and deferred it
    to OBPI-0.0.64-04, whose seven REQs never scoped it. The corpus-side check
    is not redundant with ``BriefStructure._validate_tasks``:
    ``_collect_obpi_brief_frontmatter`` parses raw YAML and never constructs the
    model, so a malformed id on disk reaches the channel comparison unchecked.
    """

    def test_malformed_task_id_in_frontmatter_flagged(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_brief(root, {**_BASE_FM, "tasks": ["not-a-task-id"]})
            errs = validate_task_envelope._sig_e_unresolvable_task_declaration(root)
            self.assertTrue(any("Signature (e)" in e.message for e in errs))
            self.assertTrue(any("not-a-task-id" in e.message for e in errs))

    def test_unknown_parent_req_flagged(self) -> None:
        """Well-formed id whose derived parent REQ exists in no brief."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_brief(root, {**_BASE_FM, "tasks": ["TASK-9.9.9-77-88-01"]})
            errs = validate_task_envelope._sig_e_unresolvable_task_declaration(root)
            self.assertTrue(any("REQ-9.9.9-77-88" in e.message for e in errs))

    def test_resolvable_task_declaration_is_clean(self) -> None:
        """The producer-stamped shape: parent REQ is in the same brief's reqs."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_brief(root, {**_BASE_FM, "tasks": ["TASK-0.0.64-04-01-01"]})
            self.assertEqual(validate_task_envelope._sig_e_unresolvable_task_declaration(root), [])

    def test_absent_tasks_key_is_clean(self) -> None:
        """Nearly every brief predates the producer stamp; absence is not a finding."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_brief(root, _BASE_FM)
            self.assertEqual(validate_task_envelope._sig_e_unresolvable_task_declaration(root), [])

    def test_parent_check_suppressed_when_no_reqs_discoverable(self) -> None:
        """An empty known-REQ set means the corpus was not readable, not that every
        declaration is unknown -- fail-closed here would flag the whole corpus."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_brief(
                root,
                {
                    **{k: v for k, v in _BASE_FM.items() if k != "reqs"},
                    "reqs": [],
                    "tasks": ["TASK-0.0.64-04-01-01"],
                },
            )
            self.assertEqual(validate_task_envelope._sig_e_unresolvable_task_declaration(root), [])

    def test_composite_includes_signature_e(self) -> None:
        """(e) must reach the same exit-3 route as (a)-(d), not sit uncalled."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_ledger(root, [])
            _write_brief(root, {**_BASE_FM, "tasks": ["not-a-task-id"]})
            errs = validate_task_envelope._validate_task_envelope_coherence(root)
            self.assertTrue(any("Signature (e)" in e.message for e in errs))
            self.assertTrue(all(e.type == "task_envelope_coherence" for e in errs))


class TestTaskGrammarSingleSourced(unittest.TestCase):
    """The TASK-ID grammar must have one spelling across its readers (GHI #753).

    ``4a256b7ac`` converged the REQ-ID grammar on one source for exactly this
    reason. This module carried its own copy of the TASK pattern; nothing
    asserted the copies agreed, which is the defect family
    ``ADR-pool.governance-document-structural-validation`` catalogues.
    """

    def test_module_copy_agrees_with_canonical_task_pattern(self) -> None:
        from gzkit.tasks import _TASK_PATTERN

        self.assertEqual(
            validate_task_envelope._SIG_B_TASK_ID_RE.pattern,
            _TASK_PATTERN.pattern,
        )

    def test_a_rename_that_is_not_a_pool_demotion_is_not_tolerated(self) -> None:
        """Narrowness: the tolerance is keyed to the demote producer alone."""
        self.assertFalse(
            validate_task_envelope._sig_a_is_grandfathered_demotion(
                {"reason": "something_else", "ts": "2026-07-30T08:54:12+00:00"},
                "artifact_renamed",
                None,
            )
        )

    def test_a_non_rename_worklog_event_is_not_tolerated(self) -> None:
        self.assertFalse(
            validate_task_envelope._sig_a_is_grandfathered_demotion(
                {"reason": "pool_demotion", "ts": "2026-07-30T08:54:12+00:00"},
                "artifact_edited",
                None,
            )
        )

    def test_an_unparseable_timestamp_is_not_tolerated(self) -> None:
        """Fail closed on a malformed ts rather than waving it through."""
        self.assertFalse(
            validate_task_envelope._sig_a_is_grandfathered_demotion(
                {"reason": "pool_demotion", "ts": "not-a-timestamp"},
                "artifact_renamed",
                None,
            )
        )


if __name__ == "__main__":
    unittest.main()
