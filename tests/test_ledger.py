"""Tests for gzkit ledger system."""

import tempfile
import unittest
from pathlib import Path

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

    def test_to_dict(self) -> None:
        """Event converts to dictionary correctly."""
        event = LedgerEvent(
            event="test_event",
            id="test-id",
            ts="2026-01-01T00:00:00+00:00",
        )
        d = event.to_dict()
        self.assertEqual(d["event"], "test_event")
        self.assertEqual(d["id"], "test-id")
        self.assertEqual(d["schema"], "gzkit.ledger.v1")

    def test_from_dict(self) -> None:
        """Event parses from dictionary correctly."""
        data = {
            "schema": "gzkit.ledger.v1",
            "event": "adr_created",
            "id": "ADR-0.1.0",
            "ts": "2026-01-01T00:00:00+00:00",
            "parent": "OBPI-core",
            "lane": "lite",
        }
        event = LedgerEvent.from_dict(data)
        self.assertEqual(event.event, "adr_created")
        self.assertEqual(event.id, "ADR-0.1.0")
        self.assertEqual(event.parent, "OBPI-core")
        self.assertEqual(event.extra["lane"], "lite")


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
            {},
            found_file=True,
            file_completed=False,
            implementation_evidence_ok=True,
            key_proof_ok=False,
            fallback_key_proof="uv run gz obpi status OBPI-0.10.0-01 --json",
        )
        self.assertEqual(semantics["runtime_state"], "in_progress")
        self.assertEqual(semantics["proof_state"], "recorded")

    def test_derive_obpi_semantics_uses_legacy_key_proof_for_completion(self) -> None:
        """Legacy completed receipts remain completed when brief key proof is substantive."""
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
        self.assertEqual(semantics["runtime_state"], "completed")
        self.assertEqual(semantics["proof_state"], "recorded")
        self.assertEqual(semantics["attestation_requirement"], "optional")
        self.assertTrue(semantics["completed"])
        self.assertEqual(semantics["anchor_state"], "not_tracked")

    def test_derive_obpi_semantics_requires_attestation_for_attested_completed(self) -> None:
        """Attested completion reports required attestation and records it when present."""
        semantics = derive_obpi_semantics(
            {
                "latest_receipt_event": "completed",
                "obpi_completion": "attested_completed",
                "ledger_completed": True,
                "latest_evidence": {"attestation_requirement": "required"},
            },
            found_file=True,
            file_completed=True,
            implementation_evidence_ok=True,
            key_proof_ok=True,
            fallback_key_proof="uv run gz obpi reconcile OBPI-0.10.0-01 --json",
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
                "latest_evidence": {},
            },
            found_file=True,
            file_completed=True,
            implementation_evidence_ok=True,
            key_proof_ok=True,
            fallback_key_proof="uv run gz obpi status OBPI-0.10.0-01 --json",
        )
        self.assertEqual(semantics["runtime_state"], "validated")
        self.assertEqual(semantics["proof_state"], "validated")

    def test_derive_obpi_semantics_reports_drift_when_ledger_and_file_disagree(self) -> None:
        """Ledger completion plus incomplete brief evidence is treated as drift."""
        semantics = derive_obpi_semantics(
            {
                "latest_receipt_event": "completed",
                "obpi_completion": "completed",
                "ledger_completed": True,
                "latest_evidence": {},
            },
            found_file=True,
            file_completed=False,
            implementation_evidence_ok=False,
            key_proof_ok=False,
        )
        self.assertEqual(semantics["runtime_state"], "drift")
        self.assertIn(
            "ledger says completed but brief file status is not Completed", semantics["issues"]
        )
        self.assertFalse(semantics["completed"])

    def test_derive_obpi_semantics_reports_scope_clean_when_head_advances_outside_scope(
        self,
    ) -> None:
        """Anchor mismatch without recorded-scope overlap remains complete and non-drifted."""
        semantics = derive_obpi_semantics(
            {
                "latest_receipt_event": "completed",
                "obpi_completion": "completed",
                "ledger_completed": True,
                "latest_evidence": {},
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
                "latest_evidence": {},
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
                "latest_evidence": {},
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
        self.assertEqual(semantics["runtime_state"], "drift")
        self.assertEqual(semantics["anchor_state"], "stale")
        self.assertEqual(semantics["anchor_drift_files"], ["src/gzkit/ledger.py"])
        self.assertIn("completion anchor drifted in recorded OBPI scope", semantics["issues"])
        self.assertTrue(semantics["completed"])

    def test_derive_obpi_semantics_reports_missing_anchor_for_tracked_receipts(self) -> None:
        """Structured completion receipts require anchor evidence for reconciliation."""
        semantics = derive_obpi_semantics(
            {
                "latest_receipt_event": "completed",
                "obpi_completion": "completed",
                "ledger_completed": True,
                "latest_evidence": {},
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
        self.assertEqual(semantics["runtime_state"], "drift")
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
                "latest_evidence": {},
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
        self.assertEqual(semantics["runtime_state"], "drift")
        self.assertEqual(semantics["anchor_state"], "degraded")
        self.assertIn(
            "completion git-sync evidence recorded blockers: Working tree is dirty.",
            semantics["issues"],
        )
        self.assertIn("completion receipt was captured from a dirty worktree", semantics["issues"])
        self.assertTrue(semantics["completed"])


if __name__ == "__main__":
    unittest.main()
