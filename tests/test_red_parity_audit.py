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

    def witness(
        self,
        failure_class: str,
        req_id: str | None = None,
        *,
        base_provenance: str | None = None,
    ) -> None:
        event = {
            "event": "red_receipt_emitted",
            "req_id": req_id or self.REQ,
            "receipt_id": "arb-red-x",
            "failure_class": failure_class,
            "base_commit": "abc1234",
        }
        # Omitted by default on purpose: every witness emitted before GHI #849 lacks
        # the field, and the audit must read that absence as `working-tree`.
        if base_provenance is not None:
            event["base_provenance"] = base_provenance
        self.events.append(event)

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


class TestVoidWitnessesDoNotCount(_Project):
    """A run that could not tell is not a witness — on either of its two shapes.

    `not-applicable` was the first shape (GHI #839). The reconstructed base adds the
    second (GHI #849): a modern test grafted onto a tree months older than itself dies
    on an import, and `classify_failure` calls that `error`. Banking it would let a
    genuinely hollow test in old code satisfy this gate — a fail-OPEN direction, and
    the reason the reconstruction could not simply be switched on.
    """

    def test_an_error_on_a_reconstructed_base_does_not_satisfy_the_gate(self) -> None:
        self.brief(_brief())
        self.completed(_AFTER)
        self.witness("error", base_provenance="reconstructed")
        errors = self.audit()
        self.assertEqual(len(errors), 1)
        self.assertIn("no 'red_receipt_emitted' witness", errors[0].message)

    def test_an_error_with_no_provenance_still_satisfies_it(self) -> None:
        # Every witness banked before the field existed ran against HEAD, where an
        # error IS a legitimate weak RED. Reading the absence as "unknown" would
        # retroactively invalidate the whole pre-#849 corpus.
        self.brief(_brief())
        self.completed(_AFTER)
        self.witness("error")
        self.assertEqual(self.audit(), [])

    def test_an_assertion_on_a_reconstructed_base_does_satisfy_it(self) -> None:
        # Reconstruction is not distrusted wholesale — only the `error` class is
        # ambiguous on it. The test reached its assertion and the assertion failed,
        # which is the same evidence whichever tree it ran against.
        self.brief(_brief())
        self.completed(_AFTER)
        self.witness("assertion", base_provenance="reconstructed")
        self.assertEqual(self.audit(), [])

    def test_a_void_rerun_cannot_erase_an_earlier_genuine_witness(self) -> None:
        # The ordering trap this dict is exposed to: it keeps the LAST event per REQ,
        # so a later run that could not tell would otherwise overwrite a real finding
        # with silence. Pinned for the reconstructed-error shape as it already is for
        # `not-applicable`.
        self.brief(_brief())
        self.completed(_AFTER)
        self.witness("assertion")
        self.witness("error", base_provenance="reconstructed")
        self.assertEqual(self.audit(), [])

    def test_a_void_rerun_cannot_erase_an_earlier_hollow_finding_either(self) -> None:
        # And the same in the accusing direction: a `none` already found must not be
        # laundered away by a later run that witnessed nothing.
        self.brief(_brief())
        self.completed(_AFTER)
        self.witness("none")
        self.witness("error", base_provenance="reconstructed")
        errors = self.audit()
        self.assertEqual(len(errors), 1)
        self.assertIn("failure_class 'none'", errors[0].message)
