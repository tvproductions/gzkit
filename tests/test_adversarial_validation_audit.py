"""Tests for the Step-4b adversarial-validation trust audit (GHI #676).

Assertions derive from the requirement — a heavy-lane completion may not exist
without a durably captured adversary verdict — not from a run of the audit.

The two invariants are deliberately tested apart: ledger coherence answers "did
the verdict outlive the session?" and brief evidence answers "can a reader see
what the adversary broke?". A change that silently collapses one into the other
must redden here.
"""

from __future__ import annotations

import datetime as dt
import json
import tempfile
import unittest
from pathlib import Path

from gzkit.commands.obpi_precomplete import _check_adversarial_validation
from gzkit.governance.trust_audits.adversarial_validation import (
    CUTOVER,
    audit_adversarial_validation,
)

_BEFORE = (CUTOVER - dt.timedelta(hours=8)).isoformat()
_AFTER = (CUTOVER + dt.timedelta(hours=8)).isoformat()

_STEP_4B = "### Step 4b — Independent Adversarial Validation (GHI #643)\n\nCodex refuted it.\n"


def _brief(lane: str = "heavy", status: str = "Completed", *, step_4b: bool = False) -> str:
    body = _STEP_4B if step_4b else "### Key Proof\n\nran it.\n"
    return f"---\nid: x\nlane: {lane}\nstatus: {status}\n---\n\n# Brief\n\n{body}"


class _Project:
    """A throwaway project tree: briefs on disk, events in the ledger."""

    def __init__(self, root: Path) -> None:
        self.root = root
        (root / ".gzkit").mkdir(parents=True, exist_ok=True)
        (root / "data").mkdir(parents=True, exist_ok=True)
        self.brief_dir = root / "docs" / "design" / "adr" / "foundation" / "ADR-x" / "obpis"
        self.brief_dir.mkdir(parents=True, exist_ok=True)
        self.events: list[dict] = []
        self.grandfather(*[])

    def brief(self, obpi_id: str, content: str) -> Path:
        path = self.brief_dir / f"{obpi_id}.md"
        path.write_text(content, encoding="utf-8")
        return path

    def receipt(self, obpi_id: str, ts: str) -> None:
        self.events.append(
            {"event": "obpi_receipt_emitted", "id": obpi_id, "ts": ts, "receipt_event": "completed"}
        )

    def verdict(self, obpi_id: str, verdict: str, resolution: str | None = None) -> None:
        event = {
            "event": "adversarial_validation",
            "obpi_id": obpi_id,
            "verdict": verdict,
            "adversary": "codex/gpt-5.4",
        }
        if resolution:
            event["resolution"] = resolution
        self.events.append(event)

    def grandfather(self, *obpi_ids: str) -> None:
        (self.root / "data" / "adversarial_validation_grandfather.json").write_text(
            json.dumps({"grandfathered_obpis": list(obpi_ids)}), encoding="utf-8"
        )

    def flush(self) -> None:
        (self.root / ".gzkit" / "ledger.jsonl").write_text(
            "".join(json.dumps(e) + "\n" for e in self.events), encoding="utf-8"
        )

    def audit(self) -> list:
        self.flush()
        return audit_adversarial_validation(self.root)


class _ProjectTest(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.p = _Project(Path(self._tmp.name))


class TestLedgerCoherence(_ProjectTest):
    """A heavy completion receipt after the cutover must carry a paired verdict."""

    OBPI = "OBPI-0.1.0-01-thing"

    def test_pre_cutover_receipt_needs_no_verdict(self) -> None:
        """The gate did not exist; demanding a verdict would force back-dating one."""
        self.p.brief(self.OBPI, _brief(step_4b=True))
        self.p.receipt(self.OBPI, _BEFORE)
        self.assertEqual(self.p.audit(), [])

    def test_post_cutover_receipt_without_verdict_is_flagged(self) -> None:
        self.p.brief(self.OBPI, _brief(step_4b=True))
        self.p.receipt(self.OBPI, _AFTER)
        errors = self.p.audit()
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0].artifact, self.OBPI)
        self.assertIn("no paired", errors[0].message)

    def test_post_cutover_receipt_with_verdict_passes(self) -> None:
        self.p.brief(self.OBPI, _brief(step_4b=True))
        self.p.receipt(self.OBPI, _AFTER)
        self.p.verdict(self.OBPI, "not-refuted")
        self.assertEqual(self.p.audit(), [])

    def test_refuted_without_resolution_is_flagged(self) -> None:
        """A known refutation may never be handed to the operator dressed as clean."""
        self.p.brief(self.OBPI, _brief(step_4b=True))
        self.p.receipt(self.OBPI, _AFTER)
        self.p.verdict(self.OBPI, "refuted")
        errors = self.p.audit()
        self.assertEqual(len(errors), 1)
        self.assertIn("resolution", errors[0].message)

    def test_refuted_with_resolution_passes(self) -> None:
        self.p.brief(self.OBPI, _brief(step_4b=True))
        self.p.receipt(self.OBPI, _AFTER)
        self.p.verdict(self.OBPI, "refuted", resolution="closed the enum; mutation now fails")
        self.assertEqual(self.p.audit(), [])

    def test_degraded_human_only_is_a_valid_capture(self) -> None:
        """The attested degraded floor is a verdict, not an absence of one."""
        self.p.brief(self.OBPI, _brief(step_4b=True))
        self.p.receipt(self.OBPI, _AFTER)
        self.p.verdict(self.OBPI, "degraded-human-only")
        self.assertEqual(self.p.audit(), [])

    def test_lite_lane_receipt_needs_no_verdict(self) -> None:
        """Step 4b is heavy-lane, matching the lane that carries Gate 3 and Gate 4."""
        self.p.brief(self.OBPI, _brief(lane="lite"))
        self.p.receipt(self.OBPI, _AFTER)
        self.assertEqual(self.p.audit(), [])

    def test_naive_timestamp_is_read_as_utc_not_crashed_on(self) -> None:
        naive = (CUTOVER + dt.timedelta(hours=8)).replace(tzinfo=None).isoformat()
        self.p.brief(self.OBPI, _brief(step_4b=True))
        self.p.receipt(self.OBPI, naive)
        errors = self.p.audit()
        self.assertEqual(len(errors), 1, "a naive post-cutover ts must still be judged")

    def test_unparseable_timestamp_is_skipped_not_raised(self) -> None:
        self.p.brief(self.OBPI, _brief(step_4b=True))
        self.p.receipt(self.OBPI, "not-a-timestamp")
        self.assertEqual(self.p.audit(), [])


class TestBriefEvidence(_ProjectTest):
    """Terminal heavy briefs must let a reader see what the adversary broke."""

    OBPI = "OBPI-0.2.0-01-thing"

    def test_missing_section_is_flagged(self) -> None:
        self.p.brief(self.OBPI, _brief())
        errors = self.p.audit()
        self.assertEqual(len(errors), 1)
        self.assertIn("Step 4b", errors[0].message)

    def test_grandfathered_brief_is_exempt(self) -> None:
        self.p.brief(self.OBPI, _brief())
        self.p.grandfather(self.OBPI)
        self.assertEqual(self.p.audit(), [])

    def test_present_section_passes(self) -> None:
        self.p.brief(self.OBPI, _brief(step_4b=True))
        self.assertEqual(self.p.audit(), [])

    def test_lite_lane_brief_is_exempt(self) -> None:
        self.p.brief(self.OBPI, _brief(lane="lite"))
        self.assertEqual(self.p.audit(), [])

    def test_non_terminal_brief_is_not_yet_gated(self) -> None:
        """An in-flight brief has not claimed completion, so nothing is being laundered."""
        self.p.brief(self.OBPI, _brief(status="In-Progress"))
        self.assertEqual(self.p.audit(), [])

    def test_missing_grandfather_file_does_not_silently_exempt(self) -> None:
        """A deleted snapshot must redden, never wave 225 briefs through."""
        self.p.brief(self.OBPI, _brief())
        (self.p.root / "data" / "adversarial_validation_grandfather.json").unlink()
        self.assertEqual(len(self.p.audit()), 1)


class TestPrecompleteCheck(_ProjectTest):
    """`gz obpi precomplete` reads the brief; the ledger event does not exist yet."""

    OBPI = "OBPI-0.3.0-01-thing"

    def test_heavy_brief_without_section_blocks(self) -> None:
        path = self.p.brief(self.OBPI, _brief())
        result = _check_adversarial_validation(path)
        self.assertFalse(result.ok)
        self.assertIsNotNone(result.remediation)
        assert result.remediation is not None
        # Guardrail-feedback prose: the recovery names a runnable next step.
        self.assertIn("--adversary-verdict", result.remediation)
        self.assertIn("degraded-human-only", result.remediation)

    def test_heavy_brief_with_section_passes(self) -> None:
        path = self.p.brief(self.OBPI, _brief(step_4b=True))
        self.assertTrue(_check_adversarial_validation(path).ok)

    def test_lite_brief_is_exempt(self) -> None:
        path = self.p.brief(self.OBPI, _brief(lane="lite"))
        self.assertTrue(_check_adversarial_validation(path).ok)

    def test_unreadable_brief_blocks_rather_than_passing(self) -> None:
        result = _check_adversarial_validation(self.p.root / "does-not-exist.md")
        self.assertFalse(result.ok)


class TestShippedSnapshotIsRatchetRegistered(unittest.TestCase):
    """The grandfather snapshot must declare an honesty mechanism, not sit unregistered.

    Exercises the production validator rather than re-reading the JSON and asserting on
    its strings: an unregistered `*_grandfather*.json` under `data/` is a silent-bypass
    surface (ADR-0.0.73 BI#8), and `audit_waiver_ratchet` is what fails closed on it.
    """

    def test_audit_waiver_ratchet_accepts_the_snapshot(self) -> None:
        from gzkit.governance.trust_audits.waiver_ratchet import audit_waiver_ratchet

        root = Path(__file__).resolve().parents[1]
        errors = audit_waiver_ratchet(root)
        offending = [e for e in errors if "adversarial_validation_grandfather" in e.artifact]
        self.assertEqual(
            offending,
            [],
            "the snapshot must be registered in waiver_ratchet_registry.json with a "
            "declared mechanism; an unregistered waiver surface fails closed",
        )


if __name__ == "__main__":
    unittest.main()
