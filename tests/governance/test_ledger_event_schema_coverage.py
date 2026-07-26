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

import tempfile
import unittest
from pathlib import Path

from gzkit.commands import validate_cmd
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


class EventSchemasValidatorScope(unittest.TestCase):
    """The schema coupling is reachable at the validator tier, not tests only (GHI #581).

    ``audit_event_schemas`` held the factory/model -> schema coupling from the
    day it landed, but its only caller was this file. A guard that runs solely
    inside the test tier is invisible where operators and agents look for it,
    so it gets re-litigated -- GHI #581 proposed a 4,775-line six-registry
    collapse to build protection that already existed. These assertions pin the
    guard to the ``gz validate`` surface where it can be found.
    """

    def _registry(self) -> dict[str, validate_cmd._ScopeEntry]:
        return {entry.stem: entry for entry in validate_cmd.VALIDATOR_REGISTRY}

    def test_event_schemas_is_a_registered_validate_scope(self) -> None:
        self.assertIn(
            "event_schemas",
            self._registry(),
            "audit_event_schemas must be dispatchable as `gz validate --event-schemas`; "
            "a coupling enforced only from the test tier is invisible at the validator "
            "tier where it gets looked for (GHI #581).",
        )

    def test_event_schemas_scope_reports_an_event_missing_its_schema_entry(self) -> None:
        """The registered stem reaches the real audit, not a no-op runner."""
        entry = self._registry()["event_schemas"]
        with tempfile.TemporaryDirectory() as tmp:
            package = Path(tmp) / "src" / "gzkit"
            (package / "schemas").mkdir(parents=True)
            (package / "ledger_events.py").write_text(
                'def ghost_event():\n    return _emit(event="ghost_event")\n',
                encoding="utf-8",
            )
            (package / "events.py").write_text("", encoding="utf-8")
            (package / "schemas" / "ledger.json").write_text('{"events": {}}', encoding="utf-8")
            errors = entry.run(Path(tmp), None)

        self.assertTrue(
            any("ghost_event" in error.artifact for error in errors),
            f"Scope must surface the unregistered event type; got {errors!r}",
        )


if __name__ == "__main__":
    unittest.main()
