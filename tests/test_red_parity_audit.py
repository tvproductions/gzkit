"""Tests for the RED-parity trust audit (GHI #642).

Assertions derive from the requirement — a completed heavy-lane BEHAVIOR REQ must
carry a witness that its covering test can fail — not from a run of the audit.
"""

from __future__ import annotations

import datetime as dt
import json
import tempfile
import unittest
from pathlib import Path

from gzkit.governance.trust_audits.red_parity import CUTOVER, audit_red_parity

_BEFORE = (CUTOVER - dt.timedelta(hours=8)).isoformat()
_AFTER = (CUTOVER + dt.timedelta(hours=8)).isoformat()


def _brief(lane: str = "heavy", status: str = "Completed", *, kind: str = "behavior") -> str:
    return (
        f"---\nid: x\nlane: {lane}\nstatus: {status}\n---\n\n"
        "## Acceptance Criteria\n\n"
        f"- [x] REQ-0.1.0-01-01 [{kind}]: the system does X when Y\n"
    )


class _Project(unittest.TestCase):
    OBPI = "OBPI-0.1.0-01-thing"
    REQ = "REQ-0.1.0-01-01"

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)
        (self.root / ".gzkit").mkdir(parents=True)
        self.brief_dir = self.root / "docs" / "design" / "adr" / "foundation" / "ADR-x" / "obpis"
        self.brief_dir.mkdir(parents=True)
        self.events: list[dict] = []

    def brief(self, content: str) -> None:
        (self.brief_dir / f"{self.OBPI}.md").write_text(content, encoding="utf-8")

    def completed(self, ts: str) -> None:
        self.events.append(
            {
                "event": "obpi_receipt_emitted",
                "id": self.OBPI,
                "ts": ts,
                "receipt_event": "completed",
            }
        )

    def witness(self, failure_class: str, req_id: str | None = None) -> None:
        self.events.append(
            {
                "event": "red_receipt_emitted",
                "req_id": req_id or self.REQ,
                "receipt_id": "arb-red-x",
                "failure_class": failure_class,
                "base_commit": "abc1234",
            }
        )

    def audit(self) -> list:
        (self.root / ".gzkit" / "ledger.jsonl").write_text(
            "".join(json.dumps(e) + "\n" for e in self.events), encoding="utf-8"
        )
        return audit_red_parity(self.root)


class TestRedParity(_Project):
    def test_pre_cutover_completion_needs_no_witness(self) -> None:
        """The gate did not exist; synthesising a witness would fabricate the evidence."""
        self.brief(_brief())
        self.completed(_BEFORE)
        self.assertEqual(self.audit(), [])

    def test_post_cutover_behavior_req_without_witness_is_flagged(self) -> None:
        self.brief(_brief())
        self.completed(_AFTER)
        errors = self.audit()
        self.assertEqual(len(errors), 1)
        self.assertIn("no 'red_receipt_emitted' witness", errors[0].message)
        self.assertIn("gz arb red", errors[0].message)

    def test_assertion_witness_passes(self) -> None:
        self.brief(_brief())
        self.completed(_AFTER)
        self.witness("assertion")
        self.assertEqual(self.audit(), [])

    def test_weak_error_witness_passes(self) -> None:
        """A weak RED still witnesses falsifiability; it is recorded, not rejected."""
        self.brief(_brief())
        self.completed(_AFTER)
        self.witness("error")
        self.assertEqual(self.audit(), [])

    def test_failure_class_none_is_flagged_as_unfalsifiable(self) -> None:
        """The test passed without its implementation. It cannot fail (Rule 6)."""
        self.brief(_brief())
        self.completed(_AFTER)
        self.witness("none")
        errors = self.audit()
        self.assertEqual(len(errors), 1)
        self.assertIn("cannot fail", errors[0].message)

    def test_support_req_is_exempt_by_proof_channel(self) -> None:
        """SUPPORT REQs have no @covers test, so no RED witness is possible."""
        self.brief(_brief(kind="support"))
        self.completed(_AFTER)
        self.assertEqual(self.audit(), [])

    def test_structural_fence_req_is_exempt_by_proof_channel(self) -> None:
        self.brief(_brief(kind="structural-fence"))
        self.completed(_AFTER)
        self.assertEqual(self.audit(), [])

    def test_untagged_req_defaults_to_behavior_and_is_gated(self) -> None:
        """A missing [kind] tag defaults to BEHAVIOR — the fail-closed default."""
        self.brief(
            "---\nid: x\nlane: heavy\nstatus: Completed\n---\n\n"
            "## Acceptance Criteria\n\n- [x] REQ-0.1.0-01-01: legacy untagged REQ\n"
        )
        self.completed(_AFTER)
        self.assertEqual(len(self.audit()), 1)

    def test_lite_lane_is_exempt(self) -> None:
        self.brief(_brief(lane="lite"))
        self.completed(_AFTER)
        self.assertEqual(self.audit(), [])

    def test_non_terminal_brief_is_not_yet_gated(self) -> None:
        self.brief(_brief(status="In-Progress"))
        self.completed(_AFTER)
        self.assertEqual(self.audit(), [])

    def test_brief_without_a_completion_receipt_is_out_of_scope(self) -> None:
        self.brief(_brief())
        self.assertEqual(self.audit(), [])

    def test_witness_for_a_different_req_does_not_satisfy_this_one(self) -> None:
        """The witness must name THIS REQ; any-witness-counts would be a hollow gate."""
        self.brief(_brief())
        self.completed(_AFTER)
        self.witness("assertion", req_id="REQ-9.9.9-99-99")
        self.assertEqual(len(self.audit()), 1)


if __name__ == "__main__":
    unittest.main()
