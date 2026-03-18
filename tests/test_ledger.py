"""Tests for gzkit ledger system."""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from gzkit.ledger import (
    Ledger,
    LedgerEvent,
    adr_created_event,
    artifact_renamed_event,
    attested_event,
    audit_receipt_emitted_event,
    closeout_initiated_event,
    constitution_created_event,
    derive_obpi_semantics,
    gate_checked_event,
    normalize_req_proof_inputs,
    obpi_created_event,
    obpi_receipt_emitted_event,
    prd_created_event,
    project_init_event,
)


class TestLedgerEvent(unittest.TestCase):
    """Tests for LedgerEvent dataclass."""

    def test_model_dump(self) -> None:
        """Event serializes via model_dump correctly."""
        event = LedgerEvent(
            event="test_event",
            id="test-id",
            ts="2026-01-01T00:00:00+00:00",
        )
        d = event.model_dump()
        self.assertEqual(d["event"], "test_event")
        self.assertEqual(d["id"], "test-id")
        self.assertEqual(d["schema"], "gzkit.ledger.v1")
        self.assertNotIn("schema_", d)
        self.assertNotIn("extra", d)

    def test_model_validate(self) -> None:
        """Event parses from dictionary via model_validate correctly."""
        data = {
            "schema": "gzkit.ledger.v1",
            "event": "adr_created",
            "id": "ADR-0.1.0",
            "ts": "2026-01-01T00:00:00+00:00",
            "parent": "OBPI-core",
            "lane": "lite",
        }
        event = LedgerEvent.model_validate(data)
        self.assertEqual(event.event, "adr_created")
        self.assertEqual(event.id, "ADR-0.1.0")
        self.assertEqual(event.parent, "OBPI-core")
        self.assertEqual(event.extra["lane"], "lite")

    def test_model_dump_flattens_extra(self) -> None:
        """model_dump flattens extra fields into top-level output."""
        event = LedgerEvent(
            event="adr_created",
            id="ADR-0.1.0",
            ts="2026-01-01T00:00:00+00:00",
            parent="OBPI-core",
            extra={"lane": "lite", "mode": "heavy"},
        )
        d = event.model_dump()
        self.assertEqual(d["lane"], "lite")
        self.assertEqual(d["mode"], "heavy")
        self.assertEqual(d["parent"], "OBPI-core")
        self.assertNotIn("extra", d)

    def test_model_roundtrip(self) -> None:
        """model_validate → model_dump roundtrip preserves data."""
        original = {
            "schema": "gzkit.ledger.v1",
            "event": "obpi_created",
            "id": "OBPI-0.1.0-01",
            "ts": "2026-01-01T00:00:00+00:00",
            "parent": "ADR-0.1.0",
            "lane": "lite",
        }
        event = LedgerEvent.model_validate(original)
        dumped = event.model_dump()
        self.assertEqual(dumped, original)


class TestEventFactories(unittest.TestCase):
    """Tests for event factory functions."""

    def test_project_init_event(self) -> None:
        """project_init_event creates correct event."""
        event = project_init_event("myproject", "lite")
        self.assertEqual(event.event, "project_init")
        self.assertEqual(event.id, "myproject")
        self.assertEqual(event.extra["mode"], "lite")

    def test_prd_created_event(self) -> None:
        """prd_created_event creates correct event."""
        event = prd_created_event("PRD-TEST-1.0.0")
        self.assertEqual(event.event, "prd_created")
        self.assertEqual(event.id, "PRD-TEST-1.0.0")

    def test_constitution_created_event(self) -> None:
        """constitution_created_event creates correct event."""
        event = constitution_created_event("charter")
        self.assertEqual(event.event, "constitution_created")
        self.assertEqual(event.id, "charter")

    def test_obpi_created_event(self) -> None:
        """obpi_created_event creates correct event with parent."""
        event = obpi_created_event("OBPI-core", "ADR-0.1.0")
        self.assertEqual(event.event, "obpi_created")
        self.assertEqual(event.id, "OBPI-core")
        self.assertEqual(event.parent, "ADR-0.1.0")

    def test_adr_created_event(self) -> None:
        """adr_created_event creates correct event with parent and lane."""
        event = adr_created_event("ADR-0.1.0", "OBPI-core", "lite")
        self.assertEqual(event.event, "adr_created")
        self.assertEqual(event.id, "ADR-0.1.0")
        self.assertEqual(event.parent, "OBPI-core")
        self.assertEqual(event.extra["lane"], "lite")

    def test_attested_event(self) -> None:
        """attested_event creates correct event."""
        event = attested_event("ADR-0.1.0", "completed", "testuser", "All done")
        self.assertEqual(event.event, "attested")
        self.assertEqual(event.id, "ADR-0.1.0")
        self.assertEqual(event.extra["status"], "completed")
        self.assertEqual(event.extra["by"], "testuser")
        self.assertEqual(event.extra["reason"], "All done")

    def test_artifact_renamed_event(self) -> None:
        """artifact_renamed_event captures old/new IDs."""
        event = artifact_renamed_event(
            "ADR-0.2.1-pool.gz-chores-system",
            "ADR-0.6.0-pool.gz-chores-system",
            "semver migration",
        )
        self.assertEqual(event.event, "artifact_renamed")
        self.assertEqual(event.id, "ADR-0.2.1-pool.gz-chores-system")
        self.assertEqual(event.extra["new_id"], "ADR-0.6.0-pool.gz-chores-system")
        self.assertEqual(event.extra["reason"], "semver migration")

    def test_obpi_receipt_emitted_event(self) -> None:
        """obpi_receipt_emitted_event creates correct event payload."""
        event = obpi_receipt_emitted_event(
            "OBPI-0.6.0-01-demo",
            "validated",
            "human:jeff",
            {"note": "observed"},
            parent_adr="ADR-0.6.0-demo",
            obpi_completion="not_completed",
        )
        self.assertEqual(event.event, "obpi_receipt_emitted")
        self.assertEqual(event.id, "OBPI-0.6.0-01-demo")
        self.assertEqual(event.parent, "ADR-0.6.0-demo")
        self.assertEqual(event.extra["receipt_event"], "validated")
        self.assertEqual(event.extra["attestor"], "human:jeff")
        self.assertEqual(event.extra["obpi_completion"], "not_completed")


class TestLedger(unittest.TestCase):
    """Tests for Ledger class."""

    def test_create(self) -> None:
        """Ledger creates empty file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            ledger_path = Path(tmpdir) / ".gzkit" / "ledger.jsonl"
            ledger = Ledger(ledger_path)
            ledger.create()
            self.assertTrue(ledger_path.exists())

    def test_append_and_read(self) -> None:
        """Ledger appends and reads events."""
        with tempfile.TemporaryDirectory() as tmpdir:
            ledger_path = Path(tmpdir) / "ledger.jsonl"
            ledger = Ledger(ledger_path)

            event1 = prd_created_event("PRD-1")
            event2 = obpi_created_event("OBPI-1", "ADR-0.1.0")

            ledger.append(event1)
            ledger.append(event2)

            events = ledger.read_all()
            self.assertEqual(len(events), 2)
            self.assertEqual(events[0].id, "PRD-1")
            self.assertEqual(events[1].id, "OBPI-1")

    def test_query_by_type(self) -> None:
        """Ledger queries events by type."""
        with tempfile.TemporaryDirectory() as tmpdir:
            ledger_path = Path(tmpdir) / "ledger.jsonl"
            ledger = Ledger(ledger_path)

            ledger.append(prd_created_event("PRD-1"))
            ledger.append(obpi_created_event("OBPI-1", "ADR-0.1.0"))
            ledger.append(adr_created_event("ADR-0.1.0", "OBPI-1", "lite"))

            prds = ledger.query(event_type="prd_created")
            self.assertEqual(len(prds), 1)
            self.assertEqual(prds[0].id, "PRD-1")

    def test_query_by_artifact_id(self) -> None:
        """Ledger queries events by artifact ID."""
        with tempfile.TemporaryDirectory() as tmpdir:
            ledger_path = Path(tmpdir) / "ledger.jsonl"
            ledger = Ledger(ledger_path)

            ledger.append(adr_created_event("ADR-0.1.0", "OBPI-1", "lite"))
            ledger.append(attested_event("ADR-0.1.0", "completed", "user"))

            events = ledger.query(artifact_id="ADR-0.1.0")
            self.assertEqual(len(events), 2)

    def test_get_artifact_graph(self) -> None:
        """Ledger builds artifact graph."""
        with tempfile.TemporaryDirectory() as tmpdir:
            ledger_path = Path(tmpdir) / "ledger.jsonl"
            ledger = Ledger(ledger_path)

            ledger.append(prd_created_event("PRD-1"))
            ledger.append(obpi_created_event("OBPI-1", "ADR-0.1.0"))
            ledger.append(adr_created_event("ADR-0.1.0", "OBPI-1", "lite"))
            ledger.append(attested_event("ADR-0.1.0", "completed", "user"))

            graph = ledger.get_artifact_graph()
            self.assertIn("PRD-1", graph)
            self.assertIn("OBPI-1", graph)
            self.assertIn("ADR-0.1.0", graph)
            self.assertTrue(graph["ADR-0.1.0"]["attested"])

    def test_get_pending_attestations(self) -> None:
        """Ledger finds ADRs without attestation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            ledger_path = Path(tmpdir) / "ledger.jsonl"
            ledger = Ledger(ledger_path)

            ledger.append(adr_created_event("ADR-0.1.0", "OBPI-1", "lite"))
            ledger.append(adr_created_event("ADR-0.2.0", "OBPI-1", "lite"))
            ledger.append(attested_event("ADR-0.1.0", "completed", "user"))

            pending = ledger.get_pending_attestations()
            self.assertEqual(pending, ["ADR-0.2.0"])

    def test_get_latest_gate_statuses_uses_latest_event(self) -> None:
        """Latest gate_checked event wins per gate."""
        with tempfile.TemporaryDirectory() as tmpdir:
            ledger_path = Path(tmpdir) / "ledger.jsonl"
            ledger = Ledger(ledger_path)

            ledger.append(gate_checked_event("ADR-0.1.0", 2, "pass", "test", 0))
            ledger.append(gate_checked_event("ADR-0.1.0", 2, "fail", "test", 1))
            ledger.append(gate_checked_event("ADR-0.1.0", 1, "pass", "test", 0))
            ledger.append(gate_checked_event("ADR-0.2.0", 2, "pass", "test", 0))

            statuses = ledger.get_latest_gate_statuses("ADR-0.1.0")
            self.assertEqual(statuses, {1: "pass", 2: "fail"})

    def test_get_artifact_graph_collapses_renamed_ids(self) -> None:
        """Renamed artifact IDs collapse to canonical ID in graph output."""
        with tempfile.TemporaryDirectory() as tmpdir:
            ledger_path = Path(tmpdir) / "ledger.jsonl"
            ledger = Ledger(ledger_path)

            ledger.append(adr_created_event("ADR-0.2.1-pool.gz-chores-system", "", "heavy"))
            ledger.append(
                artifact_renamed_event(
                    "ADR-0.2.1-pool.gz-chores-system",
                    "ADR-0.6.0-pool.gz-chores-system",
                )
            )
            ledger.append(attested_event("ADR-0.2.1-pool.gz-chores-system", "completed", "user"))

            graph = ledger.get_artifact_graph()
            self.assertIn("ADR-0.6.0-pool.gz-chores-system", graph)
            self.assertNotIn("ADR-0.2.1-pool.gz-chores-system", graph)
            self.assertTrue(graph["ADR-0.6.0-pool.gz-chores-system"]["attested"])

    def test_get_latest_gate_statuses_resolves_renamed_ids(self) -> None:
        """Gate status query resolves old IDs through rename events."""
        with tempfile.TemporaryDirectory() as tmpdir:
            ledger_path = Path(tmpdir) / "ledger.jsonl"
            ledger = Ledger(ledger_path)

            ledger.append(
                gate_checked_event("ADR-0.2.1-pool.gz-chores-system", 2, "pass", "test", 0)
            )
            ledger.append(
                artifact_renamed_event(
                    "ADR-0.2.1-pool.gz-chores-system",
                    "ADR-0.6.0-pool.gz-chores-system",
                )
            )

            statuses = ledger.get_latest_gate_statuses("ADR-0.6.0-pool.gz-chores-system")
            self.assertEqual(statuses, {2: "pass"})

    def test_get_artifact_graph_tracks_closeout_and_validation_receipt(self) -> None:
        """Graph captures closeout initiation and validation receipts for ADR semantics."""
        with tempfile.TemporaryDirectory() as tmpdir:
            ledger_path = Path(tmpdir) / "ledger.jsonl"
            ledger = Ledger(ledger_path)

            ledger.append(adr_created_event("ADR-0.1.0", "", "heavy"))
            ledger.append(closeout_initiated_event("ADR-0.1.0", "human", "heavy"))
            ledger.append(attested_event("ADR-0.1.0", "completed", "human"))
            ledger.append(audit_receipt_emitted_event("ADR-0.1.0", "validated", "human"))

            graph = ledger.get_artifact_graph()
            adr = graph["ADR-0.1.0"]
            self.assertTrue(adr["closeout_initiated"])
            self.assertEqual(adr["latest_receipt_event"], "validated")
            self.assertTrue(adr["validated"])

    def test_obpi_scoped_validation_receipt_does_not_mark_adr_validated(self) -> None:
        """OBPI-scoped receipts must not imply ADR-level validation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            ledger_path = Path(tmpdir) / "ledger.jsonl"
            ledger = Ledger(ledger_path)

            ledger.append(adr_created_event("ADR-0.1.0", "", "heavy"))
            ledger.append(
                audit_receipt_emitted_event(
                    "ADR-0.1.0",
                    "validated",
                    "human",
                    evidence={
                        "scope": "OBPI-0.1.0-01",
                        "adr_completion": "not_completed",
                        "obpi_completion": "attested_completed",
                    },
                )
            )

            graph = ledger.get_artifact_graph()
            adr = graph["ADR-0.1.0"]
            self.assertEqual(adr["latest_receipt_event"], "validated")
            self.assertFalse(adr["validated"])

    def test_get_artifact_graph_tracks_obpi_validation_receipt(self) -> None:
        """Graph captures OBPI receipt state independently from ADR lifecycle."""
        with tempfile.TemporaryDirectory() as tmpdir:
            ledger_path = Path(tmpdir) / "ledger.jsonl"
            ledger = Ledger(ledger_path)

            ledger.append(adr_created_event("ADR-0.6.0-demo", "", "heavy"))
            ledger.append(obpi_created_event("OBPI-0.6.0-01-demo", "ADR-0.6.0-demo"))
            ledger.append(
                obpi_receipt_emitted_event(
                    "OBPI-0.6.0-01-demo",
                    "validated",
                    "human:jeff",
                    {"acceptance": "observed"},
                )
            )

            graph = ledger.get_artifact_graph()
            obpi = graph["OBPI-0.6.0-01-demo"]
            self.assertEqual(obpi["latest_receipt_event"], "validated")
            self.assertTrue(obpi["validated"])

    def test_derive_adr_semantics_maps_lifecycle_and_terms(self) -> None:
        """Derived semantics map attestation and receipts to canonical lifecycle fields."""
        completed = Ledger.derive_adr_semantics({"attestation_status": "completed"})
        self.assertEqual(completed["lifecycle_status"], "Completed")
        self.assertEqual(completed["attestation_term"], "Completed")

        abandoned = Ledger.derive_adr_semantics({"attestation_status": "dropped"})
        self.assertEqual(abandoned["lifecycle_status"], "Abandoned")
        self.assertEqual(abandoned["attestation_term"], "Dropped")

        validated = Ledger.derive_adr_semantics(
            {"attestation_status": "completed", "validated": True}
        )
        self.assertEqual(validated["lifecycle_status"], "Validated")
        self.assertEqual(validated["closeout_phase"], "validated")

    def test_normalize_req_proof_inputs_falls_back_to_legacy_key_proof(self) -> None:
        """Legacy key_proof text is normalized into a machine-readable proof input."""
        inputs = normalize_req_proof_inputs(
            None,
            fallback_key_proof="uv run gz adr status ADR-0.1.0 --json",
        )
        self.assertEqual(inputs[0]["name"], "key_proof")
        self.assertEqual(inputs[0]["kind"], "legacy_key_proof")
        self.assertEqual(inputs[0]["status"], "present")

    def test_normalize_req_proof_inputs_preserves_scope_and_gap_reason(self) -> None:
        """Optional proof-input metadata is preserved when valid."""
        inputs = normalize_req_proof_inputs(
            [
                {
                    "name": "audit_gap",
                    "kind": "artifact",
                    "source": "docs/proof.txt",
                    "status": "missing",
                    "scope": "OBPI-0.10.0-01",
                    "gap_reason": "receipt not recorded yet",
                }
            ]
        )
        self.assertEqual(inputs[0]["scope"], "OBPI-0.10.0-01")
        self.assertEqual(inputs[0]["gap_reason"], "receipt not recorded yet")

    def test_derive_obpi_semantics_reports_pending_without_proof(self) -> None:
        """Absent proof and brief completion remain pending."""
        semantics = derive_obpi_semantics(
            {},
            found_file=True,
            file_completed=False,
            implementation_evidence_ok=False,
            key_proof_ok=False,
        )
        self.assertEqual(semantics["runtime_state"], "pending")
        self.assertEqual(semantics["proof_state"], "missing")
        self.assertEqual(semantics["attestation_requirement"], "optional")

    def test_derive_obpi_semantics_reports_in_progress_with_partial_proof(self) -> None:
        """Partial proof keeps runtime state in progress instead of completed."""
        semantics = derive_obpi_semantics(
            {
                "latest_evidence": {
                    "value_narrative": "The runtime engine is partially wired but missing proof.",
                }
            },
            found_file=True,
            file_completed=False,
            implementation_evidence_ok=True,
            key_proof_ok=False,
            fallback_key_proof="uv run gz obpi status OBPI-0.10.0-01 --json",
        )
        self.assertEqual(semantics["runtime_state"], "in_progress")
        self.assertEqual(semantics["proof_state"], "missing")

    def test_derive_obpi_semantics_requires_receipt_proof_for_completion(self) -> None:
        """Brief-only proof no longer upgrades a completed receipt to canonical completion."""
        semantics = derive_obpi_semantics(
            {
                "latest_receipt_event": "completed",
                "obpi_completion": "completed",
                "ledger_completed": True,
                "latest_evidence": {},
            },
            found_file=True,
            file_completed=True,
            implementation_evidence_ok=True,
            key_proof_ok=True,
            fallback_key_proof="uv run gz adr status ADR-0.1.0 --json",
        )
        self.assertEqual(semantics["runtime_state"], "drift")
        self.assertEqual(semantics["proof_state"], "missing")
        self.assertEqual(semantics["attestation_requirement"], "optional")
        self.assertIn("completed receipt evidence is missing value narrative", semantics["issues"])
        self.assertIn("completed receipt evidence is missing key proof", semantics["issues"])
        self.assertFalse(semantics["completed"])
        self.assertEqual(semantics["anchor_state"], "not_tracked")

    def test_derive_obpi_semantics_requires_attestation_for_attested_completed(self) -> None:
        """Attested completion reports required attestation and records it when present."""
        semantics = derive_obpi_semantics(
            {
                "latest_receipt_event": "completed",
                "obpi_completion": "attested_completed",
                "ledger_completed": True,
                "latest_evidence": {
                    "attestation_requirement": "required",
                    "value_narrative": "The runtime engine now persists canonical stage state.",
                    "key_proof": "uv run gz obpi reconcile OBPI-0.10.0-01 --json",
                    "human_attestation": True,
                    "attestation_text": "Accepted by the human reviewer.",
                    "attestation_date": "2026-03-10",
                },
            },
            found_file=True,
            file_completed=True,
            implementation_evidence_ok=True,
            key_proof_ok=True,
            human_attestation={
                "present": True,
                "valid": True,
                "attestor": "human:jeff",
                "date": "2026-03-10",
            },
        )
        self.assertEqual(semantics["runtime_state"], "attested_completed")
        self.assertEqual(semantics["attestation_requirement"], "required")
        self.assertEqual(semantics["attestation_state"], "recorded")

    def test_derive_obpi_semantics_reports_validated_state(self) -> None:
        """Validated receipts promote proof state to validated on top of completed proof."""
        semantics = derive_obpi_semantics(
            {
                "latest_receipt_event": "validated",
                "obpi_completion": "completed",
                "ledger_completed": True,
                "validated": True,
                "latest_evidence": {
                    "value_narrative": "Structured outputs now flow through the runtime surface.",
                    "key_proof": "uv run gz obpi status OBPI-0.10.0-01 --json",
                },
            },
            found_file=True,
            file_completed=True,
            implementation_evidence_ok=True,
            key_proof_ok=True,
        )
        self.assertEqual(semantics["runtime_state"], "validated")
        self.assertEqual(semantics["proof_state"], "validated")

    def test_derive_obpi_semantics_reports_reflection_drift_without_downgrading_completion(
        self,
    ) -> None:
        """Ledger completion remains canonical when only the markdown reflection drifts."""
        semantics = derive_obpi_semantics(
            {
                "latest_receipt_event": "completed",
                "obpi_completion": "completed",
                "ledger_completed": True,
                "latest_evidence": {
                    "value_narrative": "The runtime engine is unified behind one command.",
                    "key_proof": "uv run gz obpi pipeline OBPI-0.13.0-05 --json",
                },
            },
            found_file=True,
            file_completed=False,
            implementation_evidence_ok=False,
            key_proof_ok=False,
        )
        self.assertEqual(semantics["runtime_state"], "completed")
        self.assertEqual(semantics["issues"], [])
        self.assertEqual(
            semantics["reflection_issues"],
            [
                "brief reflection is not marked Completed",
                "brief implementation summary is missing or placeholder",
                "brief key proof is missing or placeholder",
            ],
        )
        self.assertTrue(semantics["completed"])

    def test_derive_obpi_semantics_reports_scope_clean_when_head_advances_outside_scope(
        self,
    ) -> None:
        """Anchor mismatch without recorded-scope overlap remains complete and non-drifted."""
        semantics = derive_obpi_semantics(
            {
                "latest_receipt_event": "completed",
                "obpi_completion": "completed",
                "ledger_completed": True,
                "latest_evidence": {
                    "value_narrative": "The runtime stage state persists across sessions.",
                    "key_proof": "uv run gz obpi status OBPI-0.10.0-02 --json",
                },
                "latest_completion_evidence": {
                    "scope_audit": {
                        "allowlist": ["src/module.py"],
                        "changed_files": ["src/module.py"],
                        "out_of_scope_files": [],
                    }
                },
                "latest_completion_anchor": {"commit": "abc1234", "semver": "0.10.0"},
            },
            found_file=True,
            file_completed=True,
            implementation_evidence_ok=True,
            key_proof_ok=True,
            current_head="def5678",
            files_since_anchor=["docs/guide.md"],
        )
        self.assertEqual(semantics["runtime_state"], "completed")
        self.assertEqual(semantics["anchor_state"], "scope_clean")
        self.assertEqual(semantics["anchor_drift_files"], [])
        self.assertEqual(semantics["issues"], [])
        self.assertTrue(semantics["completed"])

    def test_derive_obpi_semantics_ignores_transient_hook_state_for_anchor_drift(self) -> None:
        """Transient hook state should not stale a completed OBPI anchor."""
        semantics = derive_obpi_semantics(
            {
                "latest_receipt_event": "completed",
                "obpi_completion": "completed",
                "ledger_completed": True,
                "latest_evidence": {
                    "value_narrative": "Transient hook state is ignored during anchor checks.",
                    "key_proof": "uv run gz obpi status OBPI-0.10.0-02 --json",
                },
                "latest_completion_evidence": {
                    "scope_audit": {
                        "allowlist": [".claude/hooks/**"],
                        "changed_files": [".claude/hooks/README.md"],
                        "out_of_scope_files": [],
                    }
                },
                "latest_completion_anchor": {"commit": "abc1234", "semver": "0.10.0"},
            },
            found_file=True,
            file_completed=True,
            implementation_evidence_ok=True,
            key_proof_ok=True,
            current_head="def5678",
            files_since_anchor=[".claude/hooks/.instruction-state.json"],
        )
        self.assertEqual(semantics["runtime_state"], "completed")
        self.assertEqual(semantics["anchor_state"], "scope_clean")
        self.assertEqual(semantics["anchor_drift_files"], [])
        self.assertEqual(semantics["issues"], [])
        self.assertTrue(semantics["completed"])

    def test_derive_obpi_semantics_reports_stale_anchor_when_scope_changes(self) -> None:
        """Anchor drift is surfaced when files changed since completion overlap recorded scope."""
        semantics = derive_obpi_semantics(
            {
                "latest_receipt_event": "completed",
                "obpi_completion": "completed",
                "ledger_completed": True,
                "latest_evidence": {
                    "value_narrative": "Anchor drift is isolated to files inside recorded scope.",
                    "key_proof": "uv run gz obpi reconcile OBPI-0.10.0-02 --json",
                },
                "latest_completion_evidence": {
                    "scope_audit": {
                        "allowlist": ["src/gzkit/ledger.py", "tests/**"],
                        "changed_files": ["src/gzkit/ledger.py"],
                        "out_of_scope_files": [],
                    }
                },
                "latest_completion_anchor": {"commit": "abc1234", "semver": "0.10.0"},
            },
            found_file=True,
            file_completed=True,
            implementation_evidence_ok=True,
            key_proof_ok=True,
            current_head="def5678",
            files_since_anchor=["src/gzkit/ledger.py", "docs/guide.md"],
        )
        self.assertEqual(semantics["runtime_state"], "completed")
        self.assertEqual(semantics["anchor_state"], "stale")
        self.assertEqual(semantics["anchor_drift_files"], ["src/gzkit/ledger.py"])
        self.assertIn("completion anchor drifted in recorded OBPI scope", semantics["issues"])
        self.assertTrue(semantics["completed"])

    @patch("gzkit.ledger.list_changed_files_between")
    def test_derive_obpi_semantics_ignores_changes_absorbed_by_later_completed_sibling(
        self, list_changed_files_between_mock
    ) -> None:
        """Later sibling completion scope should absorb shared-file drift from earlier siblings."""
        list_changed_files_between_mock.return_value = []
        info = {
            "parent": "ADR-0.13.0",
            "latest_receipt_event": "completed",
            "obpi_completion": "completed",
            "ledger_completed": True,
            "latest_evidence": {
                "value_narrative": "Later sibling completions absorb shared-file drift safely.",
                "key_proof": "uv run gz obpi status OBPI-0.13.0-01 --json",
            },
            "latest_completion_evidence": {
                "scope_audit": {
                    "allowlist": ["src/gzkit/cli.py"],
                    "changed_files": ["src/gzkit/cli.py"],
                    "out_of_scope_files": [],
                }
            },
            "latest_completion_anchor": {"commit": "abc1234", "semver": "0.13.0"},
            "latest_completion_ts": "2026-03-14T10:00:00+00:00",
        }
        artifact_graph = {
            "OBPI-0.13.0-01-runtime-command-contract": {
                **info,
                "type": "obpi",
            },
            "OBPI-0.13.0-03-structured-stage-outputs": {
                "type": "obpi",
                "parent": "ADR-0.13.0",
                "ledger_completed": True,
                "latest_completion_ts": "2026-03-14T11:00:00+00:00",
                "latest_completion_evidence": {
                    "scope_audit": {
                        "allowlist": ["src/gzkit/cli.py"],
                        "changed_files": ["src/gzkit/cli.py"],
                        "out_of_scope_files": [],
                    }
                },
                "latest_completion_anchor": {"commit": "def5678", "semver": "0.13.0"},
            },
        }

        semantics = derive_obpi_semantics(
            info,
            obpi_id="OBPI-0.13.0-01-runtime-command-contract",
            artifact_graph=artifact_graph,
            found_file=True,
            file_completed=True,
            implementation_evidence_ok=True,
            key_proof_ok=True,
            project_root=Path("/tmp/fake"),
            current_head="fedcba9",
            files_since_anchor=["src/gzkit/cli.py"],
        )

        self.assertEqual(semantics["runtime_state"], "completed")
        self.assertEqual(semantics["anchor_state"], "scope_clean")
        self.assertEqual(semantics["anchor_drift_files"], [])
        self.assertEqual(semantics["issues"], [])
        self.assertTrue(semantics["completed"])

    def test_derive_obpi_semantics_reports_missing_anchor_for_tracked_receipts(self) -> None:
        """Structured completion receipts require anchor evidence for reconciliation."""
        semantics = derive_obpi_semantics(
            {
                "latest_receipt_event": "completed",
                "obpi_completion": "completed",
                "ledger_completed": True,
                "latest_evidence": {
                    "value_narrative": "Tracked receipts require explicit completion anchors.",
                    "key_proof": "uv run gz obpi reconcile OBPI-0.10.0-02 --json",
                },
                "latest_completion_evidence": {
                    "scope_audit": {
                        "allowlist": ["src/module.py"],
                        "changed_files": ["src/module.py"],
                        "out_of_scope_files": [],
                    }
                },
            },
            found_file=True,
            file_completed=True,
            implementation_evidence_ok=True,
            key_proof_ok=True,
            current_head="def5678",
        )
        self.assertEqual(semantics["runtime_state"], "completed")
        self.assertEqual(semantics["anchor_state"], "missing")
        self.assertIn("completion anchor evidence is missing", semantics["issues"])
        self.assertTrue(semantics["completed"])

    def test_derive_obpi_semantics_reports_degraded_git_sync_receipt_state(self) -> None:
        """Recorder-time git-sync blockers are surfaced as anchor-aware drift."""
        semantics = derive_obpi_semantics(
            {
                "latest_receipt_event": "completed",
                "obpi_completion": "completed",
                "ledger_completed": True,
                "latest_evidence": {
                    "value_narrative": (
                        "Git-sync blockers are preserved with the completion receipt."
                    ),
                    "key_proof": "uv run gz obpi status OBPI-0.10.0-02 --json",
                },
                "latest_completion_evidence": {
                    "scope_audit": {
                        "allowlist": ["src/module.py"],
                        "changed_files": ["src/module.py"],
                        "out_of_scope_files": [],
                    },
                    "git_sync_state": {
                        "dirty": True,
                        "ahead": 0,
                        "behind": 0,
                        "diverged": False,
                        "blockers": ["Working tree is dirty."],
                    },
                },
                "latest_completion_anchor": {"commit": "abc1234", "semver": "0.10.0"},
            },
            found_file=True,
            file_completed=True,
            implementation_evidence_ok=True,
            key_proof_ok=True,
            current_head="abc1234",
        )
        self.assertEqual(semantics["runtime_state"], "completed")
        self.assertEqual(semantics["anchor_state"], "degraded")
        self.assertIn(
            "completion git-sync evidence recorded blockers: Working tree is dirty.",
            semantics["issues"],
        )
        self.assertIn("completion receipt was captured from a dirty worktree", semantics["issues"])
        self.assertTrue(semantics["completed"])


class TestTypedEventModels(unittest.TestCase):
    """Tests for typed event models and discriminated union parsing."""

    def test_parse_typed_event_project_init(self) -> None:
        """Discriminated union parses project_init into ProjectInitEvent."""
        from gzkit.events import ProjectInitEvent, parse_typed_event

        data = {
            "schema": "gzkit.ledger.v1",
            "event": "project_init",
            "id": "myproject",
            "ts": "2026-01-01T00:00:00+00:00",
            "mode": "lite",
        }
        event = parse_typed_event(data)
        self.assertIsInstance(event, ProjectInitEvent)
        self.assertEqual(event.mode, "lite")
        self.assertEqual(event.id, "myproject")

    def test_parse_typed_event_adr_created(self) -> None:
        """Discriminated union parses adr_created into AdrCreatedEvent."""
        from gzkit.events import AdrCreatedEvent, parse_typed_event

        data = {
            "schema": "gzkit.ledger.v1",
            "event": "adr_created",
            "id": "ADR-0.1.0",
            "ts": "2026-01-01T00:00:00+00:00",
            "parent": "OBPI-core",
            "lane": "lite",
        }
        event = parse_typed_event(data)
        self.assertIsInstance(event, AdrCreatedEvent)
        self.assertEqual(event.lane, "lite")
        self.assertEqual(event.parent, "OBPI-core")

    def test_parse_typed_event_obpi_receipt(self) -> None:
        """Discriminated union parses obpi_receipt_emitted into ObpiReceiptEmittedEvent."""
        from gzkit.events import ObpiReceiptEmittedEvent, parse_typed_event

        data = {
            "schema": "gzkit.ledger.v1",
            "event": "obpi_receipt_emitted",
            "id": "OBPI-0.6.0-01-demo",
            "parent": "ADR-0.6.0-demo",
            "ts": "2026-01-01T00:00:00+00:00",
            "receipt_event": "validated",
            "attestor": "human:jeff",
            "evidence": {"acceptance": "observed"},
            "obpi_completion": "completed",
        }
        event = parse_typed_event(data)
        self.assertIsInstance(event, ObpiReceiptEmittedEvent)
        self.assertEqual(event.receipt_event, "validated")
        self.assertEqual(event.obpi_completion, "completed")

    def test_typed_event_backward_compat_extra(self) -> None:
        """Typed event .extra property returns event-specific fields as dict."""
        from gzkit.events import AdrCreatedEvent, parse_typed_event

        data = {
            "schema": "gzkit.ledger.v1",
            "event": "adr_created",
            "id": "ADR-0.1.0",
            "ts": "2026-01-01T00:00:00+00:00",
            "lane": "lite",
        }
        event = parse_typed_event(data)
        self.assertIsInstance(event, AdrCreatedEvent)
        self.assertEqual(event.extra["lane"], "lite")

    def test_typed_event_model_dump_roundtrip(self) -> None:
        """Typed event model_dump produces same output as LedgerEvent."""
        from gzkit.events import parse_typed_event

        data = {
            "schema": "gzkit.ledger.v1",
            "event": "adr_created",
            "id": "ADR-0.1.0",
            "ts": "2026-01-01T00:00:00+00:00",
            "parent": "OBPI-core",
            "lane": "lite",
        }
        typed = parse_typed_event(data)
        legacy = LedgerEvent.model_validate(data)
        self.assertEqual(typed.model_dump(), legacy.model_dump())

    def test_parse_typed_event_unknown_type_raises(self) -> None:
        """Unknown event type raises ValueError from discriminated union."""
        from pydantic import ValidationError as PydanticValidationError

        from gzkit.events import parse_typed_event

        data = {
            "schema": "gzkit.ledger.v1",
            "event": "mystery_event",
            "id": "ADR-0.1.0",
            "ts": "2026-01-01T00:00:00+00:00",
        }
        with self.assertRaises(PydanticValidationError):
            parse_typed_event(data)


class TestNestedEvidenceModels(unittest.TestCase):
    """Tests for Pydantic nested evidence models."""

    def test_valid_req_proof_input(self) -> None:
        """Valid ReqProofInput parses successfully."""
        from gzkit.events import ReqProofInput

        data = {
            "name": "key_proof",
            "kind": "command",
            "source": "uv run gz test",
            "status": "present",
        }
        proof = ReqProofInput.model_validate(data)
        self.assertEqual(proof.name, "key_proof")
        self.assertEqual(proof.kind, "command")

    def test_invalid_req_proof_kind_rejected(self) -> None:
        """Invalid kind in ReqProofInput raises validation error."""
        from pydantic import ValidationError as PydanticValidationError

        from gzkit.events import ReqProofInput

        data = {
            "name": "key_proof",
            "kind": "unknown",
            "source": "uv run gz test",
            "status": "present",
        }
        with self.assertRaises(PydanticValidationError):
            ReqProofInput.model_validate(data)

    def test_valid_obpi_receipt_evidence(self) -> None:
        """Valid ObpiReceiptEvidence parses successfully."""
        from gzkit.events import ObpiReceiptEvidence

        data = {
            "parent_lane": "heavy",
            "attestation_requirement": "required",
            "scope_audit": {
                "allowlist": ["docs/design/**"],
                "changed_files": ["docs/design/adr.md"],
                "out_of_scope_files": [],
            },
            "git_sync_state": {
                "branch": "main",
                "remote": "origin",
                "head": "abc1234",
                "remote_head": "abc1234",
                "dirty": False,
                "ahead": 0,
                "behind": 0,
                "diverged": False,
                "actions": [],
                "warnings": [],
                "blockers": [],
            },
        }
        evidence = ObpiReceiptEvidence.model_validate(data)
        self.assertEqual(evidence.parent_lane, "heavy")
        self.assertIsNotNone(evidence.scope_audit)
        self.assertIsNotNone(evidence.git_sync_state)

    def test_pydantic_loc_to_field_path(self) -> None:
        """Field path conversion produces expected dotted paths with indices."""
        from gzkit.events import pydantic_loc_to_field_path

        self.assertEqual(
            pydantic_loc_to_field_path("evidence", ("req_proof_inputs", 0, "kind")),
            "evidence.req_proof_inputs[0].kind",
        )
        self.assertEqual(
            pydantic_loc_to_field_path("evidence", ("scope_audit", "allowlist", 0)),
            "evidence.scope_audit.allowlist[0]",
        )
        self.assertEqual(
            pydantic_loc_to_field_path("evidence", ("git_sync_state", "dirty")),
            "evidence.git_sync_state.dirty",
        )


if __name__ == "__main__":
    unittest.main()
