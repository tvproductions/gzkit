"""Every ledger event type must be claimed by the graph builder (GHI #193 class).

Unit-test entry to the audit; the canonical logic lives in
``gzkit.governance.trust_audits.audit_event_handlers`` and is also exposed as
``gz validate --event-handlers``.
"""

from __future__ import annotations

import unittest
from pathlib import Path

from gzkit.governance.trust_audits import audit_event_handlers

_PROJECT_ROOT = Path(__file__).resolve().parents[2]


class LedgerEventHandlerCoverage(unittest.TestCase):
    """Every event factory output must be claimed by the graph or explicitly waived."""

    def test_every_event_type_claimed_or_waived(self) -> None:
        errors = audit_event_handlers(_PROJECT_ROOT)
        self.assertFalse(
            errors,
            msg=(
                "Ledger event types emitted by src/gzkit/ledger_events.py but "
                "neither handled by a graph builder in src/gzkit/ledger.py nor "
                "waived. Add a handler OR add a waiver with a rationale.\n"
                + "\n".join(f"  {e.artifact}: {e.message}" for e in errors)
            ),
        )


if __name__ == "__main__":
    unittest.main()
