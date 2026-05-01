"""Every ledger event type must have a paired ``schemas/ledger.json`` entry (GHI #374 class).

Symmetric audit to ``test_ledger_event_handler_coverage.py``: that file
covers the graph-handler side of DO IT RIGHT 1a (coupled-surface
coherence); this file covers the schema side. A factory in
``src/gzkit/ledger_events.py`` or a typed model in ``src/gzkit/events.py``
that emits an event without a schema entry breaks ``gz validate --ledger``
with ``Unknown event type`` errors as soon as the event lands on the
ledger.

Canonical logic lives in ``gzkit.governance.trust_audits.events.audit_event_schemas``.
"""

from __future__ import annotations

import unittest
from pathlib import Path

from gzkit.governance.trust_audits import audit_event_schemas

_PROJECT_ROOT = Path(__file__).resolve().parents[2]


class LedgerEventSchemaCoverage(unittest.TestCase):
    """Every event factory and typed model output must have a schema entry."""

    def test_every_factory_event_has_schema_entry(self) -> None:
        errors = audit_event_schemas(_PROJECT_ROOT)
        self.assertFalse(
            errors,
            msg=(
                "Ledger event types emitted by src/gzkit/ledger_events.py or "
                "declared on _EventBase subclasses in src/gzkit/events.py but "
                "missing a paired entry in src/gzkit/schemas/ledger.json. "
                "Add the schema entry, or remove the stale factory/model.\n"
                + "\n".join(f"  {e.artifact}: {e.message}" for e in errors)
            ),
        )


if __name__ == "__main__":
    unittest.main()
