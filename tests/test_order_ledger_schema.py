"""The ledger schema witnesses what the order writer requires at accepted and closed.

RP-12 rulings 73 and 86 have the order writer refuse an ``accepted`` move that books
no ``acceptance_ready`` and a ``closed`` move with no Gate 5 attestor and words; the
schema's conditional rules hold the same at Layer 2, so a row the writer would refuse
fails ``gz validate --ledger`` (the docs review of O2 task 4, finding 15).
"""

import tempfile
import unittest
from pathlib import Path

from gzkit.events import OrderTransitionedEvent
from gzkit.ledger import Ledger, ledger_row
from gzkit.validate_pkg.ledger_check import validate_ledger

_BASE = {
    "event": "order_transitioned",
    "id": "ORD-01-import",
    "order": "ORD-01-import",
    "work_package": "WP-01-stamp",
    "evidence": "E",
}


class TestOrderRowsAgainstTheSchema(unittest.TestCase):
    def messages(self, **fields: object) -> list[str]:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "ledger.jsonl"
            event = OrderTransitionedEvent.model_validate({**_BASE, **fields})
            Ledger(path).append(ledger_row(event))
            return [error.message for error in validate_ledger(path)]

    def test_an_accepted_row_booking_readiness_passes(self) -> None:
        self.assertEqual(
            self.messages(from_state="commenced", to_state="accepted", acceptance_ready=False),
            [],
        )

    def test_an_accepted_row_booking_no_readiness_fails(self) -> None:
        """Ruling 86: an accepted move books whether the order read ready."""
        found = self.messages(from_state="commenced", to_state="accepted")
        self.assertTrue(any("acceptance_ready" in m and "accepted" in m for m in found), found)

    def test_a_closed_row_with_its_gate_5_passes(self) -> None:
        self.assertEqual(
            self.messages(
                from_state="opened",
                to_state="closed",
                decision="terminate",
                attestor="g0",
                attestation_text="terminate it",
            ),
            [],
        )

    def test_a_closed_row_with_no_attestor_fails(self) -> None:
        """Ruling 73: an order closes only through Gate 5, on an attestor's words."""
        found = self.messages(
            from_state="opened", to_state="closed", decision="terminate", attestation_text="x"
        )
        self.assertTrue(any("attestor" in m and "closed" in m for m in found), found)

    def test_each_decision_requires_its_own_field(self) -> None:
        """Ruling 73: proceed, redirect and pause each carry the field the decision names."""
        for decision, field in (
            ("proceed", "residual_risk"),
            ("redirect", "superseded_by"),
            ("pause", "revisit_condition"),
        ):
            with self.subTest(decision=decision):
                gate_5 = {
                    "from_state": "accepted",
                    "to_state": "closed",
                    "decision": decision,
                    "attestor": "g0",
                    "attestation_text": "x",
                }
                found = self.messages(**gate_5)
                self.assertTrue(any(field in m and decision in m for m in found), found)
                self.assertEqual(self.messages(**gate_5, **{field: "named"}), [])

    def test_a_frozen_row_needs_neither(self) -> None:
        self.assertEqual(
            self.messages(
                from_state="opened",
                to_state="frozen",
                baseline=[{"req": "REQ-1", "revision": 1}],
                risk_note="r",
                review_receipt="rv",
            ),
            [],
        )


if __name__ == "__main__":
    unittest.main()
