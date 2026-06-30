"""Tests for `gz obpi status` runtime-state rendering and repudiation handling.

Regression home for GHI #634: a repudiated OBPI must not render as
"ATTESTED COMPLETED". `gz obpi repudiate` reverses Gate-5 (ADR-0.0.71), so the
status surface must reflect a REPUDIATED runtime state — not the stale
pre-repudiation completion receipt the graph node still carries.
"""

from __future__ import annotations

import unittest
from typing import Any

from gzkit.commands.status_obpi import _render_obpi_runtime_state
from gzkit.ledger import derive_obpi_semantics


def _attested_then_repudiated_node() -> dict[str, Any]:
    """An OBPI graph node carrying a fully-attested completion receipt that a
    later ``obpi_completion_repudiated`` event reversed (the GHI #634 repro).

    The stale receipt fields persist on the node (``obpi_completion`` plus full
    attestation evidence); only ``ledger_completed`` flips False and
    ``repudiated`` flips True — mirroring how ``ledger.py`` applies the
    repudiation event over the prior completion receipt.
    """
    return {
        "type": "obpi",
        "repudiated": True,
        "repudiated_reason": "model-induced-fabrication",
        "obpi_completion": "attested_completed",
        "ledger_completed": False,
        "latest_receipt_event": "completed",
        "latest_evidence": {
            "value_narrative": "the committed-rendition store was built",
            "key_proof": "uv run gz check -> exit 0",
            "human_attestation": True,
            "attestation_text": "completed",
            "attestation_date": "2026-06-14",
        },
    }


class TestRepudiatedRuntimeState(unittest.TestCase):
    def test_repudiation_overrides_stale_attested_completion(self) -> None:
        """A repudiated node derives runtime_state='repudiated', never the
        stale 'attested_completed' receipt it still carries (GHI #634)."""
        semantics = derive_obpi_semantics(
            _attested_then_repudiated_node(),
            obpi_id="OBPI-0.0.37-22-x",
            found_file=True,
            file_completed=False,
            implementation_evidence_ok=True,
            key_proof_ok=True,
        )
        self.assertEqual(semantics["runtime_state"], "repudiated")
        self.assertFalse(semantics["completed"])
        self.assertFalse(semantics["ledger_completed"])
        self.assertNotEqual(semantics["attestation_state"], "recorded")

    def test_render_repudiated_is_not_attested_completed(self) -> None:
        """The runtime-state renderer labels 'repudiated' as REPUDIATED, not the
        green ATTESTED COMPLETED a repudiated OBPI used to show (GHI #634)."""
        label = _render_obpi_runtime_state("repudiated", True)
        self.assertIn("REPUDIATED", label)
        self.assertNotIn("ATTESTED COMPLETED", label)

    def test_genuine_recompletion_clears_repudiated_and_renders_completed(self) -> None:
        """A later genuine completion resets repudiated=False (ledger.py
        666-667); such a node must still render attested-completed, proving the
        short-circuit keys on the live flag rather than becoming sticky."""
        node = _attested_then_repudiated_node()
        node["repudiated"] = False
        node["repudiated_reason"] = None
        node["ledger_completed"] = True
        semantics = derive_obpi_semantics(
            node,
            obpi_id="OBPI-0.0.37-22-x",
            found_file=True,
            file_completed=False,
            implementation_evidence_ok=True,
            key_proof_ok=True,
        )
        self.assertEqual(semantics["runtime_state"], "attested_completed")


if __name__ == "__main__":
    unittest.main()
