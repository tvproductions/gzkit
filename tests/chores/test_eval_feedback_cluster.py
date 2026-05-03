"""Tests for eval_feedback_cluster_lib — OBPI-0.0.26-03 clustering chore.

Validates that the chore correctly groups recurring weak-dimension patterns
from adr-evaluation ledger events and gz-justify artifacts, emits proposal
records when thresholds are met, and remains idempotent on re-run.

All tests use tempfile-backed fixtures per .gzkit/rules/tests.md.
"""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from gzkit.chores.eval_feedback_cluster_lib import (
    ProposalRecord,
    run_cluster,
)
from gzkit.commands.common import get_project_root
from gzkit.governance.trust_audits.chores import audit_chores_layout
from gzkit.traceability import covers

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _write_ledger(path: Path, events: list[dict]) -> None:
    """Write events as JSONL to path."""
    with path.open("w", encoding="utf-8") as fh:
        for event in events:
            fh.write(json.dumps(event) + "\n")


def _write_justify(dir_path: Path, anchor_id: str, content: str) -> None:
    """Write a minimal justify markdown file with frontmatter."""
    dir_path.mkdir(parents=True, exist_ok=True)
    slug = anchor_id.replace("/", "-").replace(":", "-")
    filepath = dir_path / f"{slug}-20260101T000000.md"
    filepath.write_text(content, encoding="utf-8")


def _make_eval_event(artifact_id: str, dimensions: dict[str, float]) -> dict:
    """Build a minimal adr-evaluation event dict."""
    return {
        "schema": "1.0",
        "event": "adr-evaluation",
        "id": f"evt-{artifact_id}",
        "ts": "2026-01-01T00:00:00Z",
        "artifact_id": artifact_id,
        "artifact_type": "adr",
        "dimensions": dimensions,
        "scores": dimensions,
        "weighted_total": sum(dimensions.values()) / max(len(dimensions), 1),
        "red_team_challenges_fired": [],
        "evaluator_persona": "test-evaluator",
        "timestamp": "2026-01-01T00:00:00Z",
    }


# ---------------------------------------------------------------------------
# Test class
# ---------------------------------------------------------------------------


class TestEvalFeedbackCluster(unittest.TestCase):
    """Policy-level pins for the eval-feedback-cluster chore."""

    @covers("REQ-0.0.26-03-02")
    def test_zero_evidence_no_proposals(self) -> None:
        """Zero-evidence run: empty ledger, no justify artifacts -> no proposals."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            ledger_path = root / ".gzkit" / "ledger.jsonl"
            ledger_path.parent.mkdir(parents=True, exist_ok=True)
            _write_ledger(ledger_path, [])

            proofs_dir = root / ".gzkit" / "chores" / "eval-feedback-cluster" / "proofs"
            justify_root = root / "artifacts" / "justify"

            result = run_cluster(
                root,
                ledger_path=ledger_path,
                justify_root=justify_root,
                proofs_dir=proofs_dir,
            )

            self.assertEqual(result, [])
            # No files written to proofs dir when no proposals
            if proofs_dir.exists():
                self.assertEqual(list(proofs_dir.glob("proposal-*.json")), [])

    @covers("REQ-0.0.26-03-02")
    def test_below_threshold_no_proposal(self) -> None:
        """Below-threshold: 2 events sharing same weak dimension -> no proposal emitted."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            ledger_path = root / ".gzkit" / "ledger.jsonl"
            ledger_path.parent.mkdir(parents=True, exist_ok=True)

            events = [
                _make_eval_event("ADR-0.1.0", {"clarity": 1.5}),
                _make_eval_event("ADR-0.2.0", {"clarity": 1.5}),
            ]
            _write_ledger(ledger_path, events)

            proofs_dir = root / ".gzkit" / "chores" / "eval-feedback-cluster" / "proofs"
            justify_root = root / "artifacts" / "justify"

            result = run_cluster(
                root,
                ledger_path=ledger_path,
                justify_root=justify_root,
                proofs_dir=proofs_dir,
                cluster_min_recurrence=3,
            )

            self.assertEqual(result, [])

    @covers("REQ-0.0.26-03-03")
    def test_at_threshold_emits_proposal(self) -> None:
        """At-threshold: 3 events with clarity score=2.7 (band=low) -> 1 proposal emitted."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            ledger_path = root / ".gzkit" / "ledger.jsonl"
            ledger_path.parent.mkdir(parents=True, exist_ok=True)

            events = [
                _make_eval_event("ADR-0.1.0", {"clarity": 2.7}),
                _make_eval_event("ADR-0.2.0", {"clarity": 2.7}),
                _make_eval_event("ADR-0.3.0", {"clarity": 2.7}),
            ]
            _write_ledger(ledger_path, events)

            proofs_dir = root / ".gzkit" / "chores" / "eval-feedback-cluster" / "proofs"
            justify_root = root / "artifacts" / "justify"

            result = run_cluster(
                root,
                ledger_path=ledger_path,
                justify_root=justify_root,
                proofs_dir=proofs_dir,
                cluster_min_recurrence=3,
                score_threshold=3.0,
            )

            self.assertEqual(len(result), 1)
            proposal = result[0]
            self.assertIsInstance(proposal, ProposalRecord)
            self.assertEqual(proposal.cluster_key, "dim:clarity:low")
            self.assertEqual(proposal.recurrence_count, 3)
            self.assertEqual(
                sorted(proposal.source_artifact_ids),
                ["ADR-0.1.0", "ADR-0.2.0", "ADR-0.3.0"],
            )
            self.assertTrue(proposal.summary)
            self.assertTrue(proposal.proposed_rule_target)

            # Proposal file written to proofs_dir
            written = list(proofs_dir.glob("proposal-*.json"))
            self.assertEqual(len(written), 1)

    @covers("REQ-0.0.26-03-03")
    def test_multiple_clusters_multiple_proposals(self) -> None:
        """Two independent dimension clusters each with 3 events -> 2 proposals."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            ledger_path = root / ".gzkit" / "ledger.jsonl"
            ledger_path.parent.mkdir(parents=True, exist_ok=True)

            events = [
                _make_eval_event("ADR-0.1.0", {"clarity": 2.7, "scope": 2.7}),
                _make_eval_event("ADR-0.2.0", {"clarity": 2.7, "scope": 2.7}),
                _make_eval_event("ADR-0.3.0", {"clarity": 2.7, "scope": 2.7}),
            ]
            _write_ledger(ledger_path, events)

            proofs_dir = root / ".gzkit" / "chores" / "eval-feedback-cluster" / "proofs"
            justify_root = root / "artifacts" / "justify"

            result = run_cluster(
                root,
                ledger_path=ledger_path,
                justify_root=justify_root,
                proofs_dir=proofs_dir,
                cluster_min_recurrence=3,
                score_threshold=3.0,
            )

            self.assertEqual(len(result), 2)
            keys = sorted(p.cluster_key for p in result)
            self.assertIn("dim:clarity:low", keys)
            self.assertIn("dim:scope:low", keys)

            written = list(proofs_dir.glob("proposal-*.json"))
            self.assertEqual(len(written), 2)

    @covers("REQ-0.0.26-03-04")
    def test_idempotent_rerun(self) -> None:
        """Idempotent: run with 3 events -> 1 proposal. Re-run same data -> 0 new proposals."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            ledger_path = root / ".gzkit" / "ledger.jsonl"
            ledger_path.parent.mkdir(parents=True, exist_ok=True)

            events = [
                _make_eval_event("ADR-0.1.0", {"clarity": 2.7}),
                _make_eval_event("ADR-0.2.0", {"clarity": 2.7}),
                _make_eval_event("ADR-0.3.0", {"clarity": 2.7}),
            ]
            _write_ledger(ledger_path, events)

            proofs_dir = root / ".gzkit" / "chores" / "eval-feedback-cluster" / "proofs"
            justify_root = root / "artifacts" / "justify"

            kwargs = {
                "ledger_path": ledger_path,
                "justify_root": justify_root,
                "proofs_dir": proofs_dir,
                "cluster_min_recurrence": 3,
                "score_threshold": 3.0,
            }

            first_run = run_cluster(root, **kwargs)
            self.assertEqual(len(first_run), 1)

            second_run = run_cluster(root, **kwargs)
            self.assertEqual(
                second_run,
                [],
                msg="Idempotent re-run must return [] when no new evidence",
            )

            # Total files on disk remains 1
            written = list(proofs_dir.glob("proposal-*.json"))
            self.assertEqual(len(written), 1)

    @covers("REQ-0.0.26-03-04")
    def test_readonly_no_writes_outside_proofs(self) -> None:
        """Read-only contract: chore writes only inside proofs_dir, nowhere else."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            ledger_path = root / ".gzkit" / "ledger.jsonl"
            ledger_path.parent.mkdir(parents=True, exist_ok=True)

            events = [
                _make_eval_event("ADR-0.1.0", {"clarity": 2.7}),
                _make_eval_event("ADR-0.2.0", {"clarity": 2.7}),
                _make_eval_event("ADR-0.3.0", {"clarity": 2.7}),
            ]
            _write_ledger(ledger_path, events)

            proofs_dir = root / ".gzkit" / "chores" / "eval-feedback-cluster" / "proofs"
            justify_root = root / "artifacts" / "justify"

            # Collect only files (not directories) before run
            def _all_files(base: Path) -> set[Path]:
                return {p for p in base.rglob("*") if p.is_file()} if base.exists() else set()

            before_run = _all_files(root)

            run_cluster(
                root,
                ledger_path=ledger_path,
                justify_root=justify_root,
                proofs_dir=proofs_dir,
                cluster_min_recurrence=3,
                score_threshold=3.0,
            )

            after_run = _all_files(root)
            new_files = after_run - before_run

            # All new files must be under proofs_dir
            for new_file in new_files:
                self.assertTrue(
                    str(new_file).startswith(str(proofs_dir)),
                    msg=f"Chore wrote outside proofs_dir: {new_file}",
                )

    @covers("REQ-0.0.26-03-01")
    def test_chore_registered_in_registry(self) -> None:
        """Chore registration: eval-feedback-cluster slug appears in chores registry."""
        registry_path = Path(__file__).parents[2] / "src" / "gzkit" / "chores" / "registry.json"
        self.assertTrue(registry_path.exists(), "registry.json not found")
        data = json.loads(registry_path.read_text(encoding="utf-8"))
        slugs = [entry["slug"] for entry in data.get("chores", [])]
        self.assertIn("eval-feedback-cluster", slugs)

    @covers("REQ-0.0.26-03-05")
    def test_chores_layout_validation_passes(self) -> None:
        """Layout validation: eval-feedback-cluster two-surface layout has no violations."""
        project_root = get_project_root()
        errors = audit_chores_layout(project_root)
        cluster_errors = [e for e in errors if "eval-feedback-cluster" in str(e)]
        self.assertEqual(
            cluster_errors,
            [],
            msg=f"Chores layout violations for eval-feedback-cluster: {cluster_errors}",
        )


class TestProposalRecordFiledFields(unittest.TestCase):
    """Tests for optional filed/ghi_url/advisory fields on ProposalRecord (REQ-0.0.26-04-10)."""

    @covers("REQ-0.0.26-04-10")
    def test_proposal_record_filed_fields(self) -> None:
        """ProposalRecord accepts optional filed/ghi_url/advisory fields."""
        record = ProposalRecord(
            cluster_key="dim:clarity:low",
            recurrence_count=3,
            source_artifact_ids=["ADR-0.1.0", "ADR-0.2.0", "ADR-0.3.0"],
            source_artifact_paths=["path/a", "path/b", "path/c"],
            summary="Clarity scored low across 3 artifacts.",
            proposed_rule_target=".gzkit/rules/clarity-improvement.md",
            content_hash="abcdef1234567890",
            filed=True,
            ghi_url="https://github.com/va/gzkit/issues/999",
            advisory=False,
        )
        self.assertTrue(record.filed)
        self.assertEqual(record.ghi_url, "https://github.com/va/gzkit/issues/999")
        self.assertFalse(record.advisory)

    @covers("REQ-0.0.26-04-10")
    def test_proposal_record_backward_compat(self) -> None:
        """ProposalRecord with no filed/ghi_url/advisory fields parses with defaults."""
        data = {
            "cluster_key": "dim:clarity:low",
            "recurrence_count": 3,
            "source_artifact_ids": ["ADR-0.1.0", "ADR-0.2.0", "ADR-0.3.0"],
            "source_artifact_paths": ["path/a", "path/b", "path/c"],
            "summary": "Clarity scored low across 3 artifacts.",
            "proposed_rule_target": ".gzkit/rules/clarity-improvement.md",
            "content_hash": "abcdef1234567890",
        }
        record = ProposalRecord(**data)
        self.assertFalse(record.filed)
        self.assertIsNone(record.ghi_url)
        self.assertFalse(record.advisory)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
