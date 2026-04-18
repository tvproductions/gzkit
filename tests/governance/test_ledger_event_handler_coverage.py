"""Every ledger event type must be claimed by the graph builder (GHI #193 class).

GHI #193 was a silent attestation blind-spot: ``obpi_receipt_emitted`` was the
only attestation path for OBPIs, but the graph builder only marked
``attested=True`` on ``event.event == "attested"``. The result was 100%
coverage of attested OBPIs silently falling out of graph state, poisoning
every downstream consumer.

This test enumerates every ledger event factory function in
``src/gzkit/ledger_events.py``, extracts the ``event=`` string each one emits,
and asserts every event type is either:

* **claimed** by a graph handler under ``Ledger`` (string-match against
  ``event.event == "..."`` or ``event.event != "..."`` in ``src/gzkit/ledger.py``), or
* **explicitly waived** in ``NO_GRAPH_IMPACT`` with a one-line rationale.

Adding a new event factory requires one of the two paths. The waiver must
name what the event *does* affect (e.g. lock file, release metadata)
so the decision is reviewable.
"""

from __future__ import annotations

import ast
import re
import unittest
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_LEDGER_EVENTS = _PROJECT_ROOT / "src" / "gzkit" / "ledger_events.py"
_LEDGER = _PROJECT_ROOT / "src" / "gzkit" / "ledger.py"


# Event types that intentionally have no graph-builder impact. Each entry must
# name the real durable destination (L2 scan, L3 lock file, etc.) so future
# maintainers see why the waiver exists.
NO_GRAPH_IMPACT: dict[str, str] = {
    "project_init": "Bootstrap sentinel; no artifact nodes emit from it.",
    "artifact_edited": "Session activity log; consumed by anchor analysis, not graph.",
    "obpi_lock_claimed": "L3 ephemeral lock file; consumed by gz obpi lock, not graph.",
    "obpi_lock_released": "L3 ephemeral lock file; consumed by gz obpi lock, not graph.",
    "patch-release": (
        "Release-line metadata (hyphenated per patch_release_event at "
        "src/gzkit/ledger_events.py:300). Consumed by gz patch release, "
        "not artifact graph."
    ),
    "audit_generated": "Heavy-lane audit trail; consumed by gz adr audit tooling, not graph.",
    "adr_eval_completed": "Evaluation scorecard; consumed by gz adr evaluate, not graph.",
    "lifecycle_transition": (
        "Transition log for state-doctrine audits; consumed by gz state, not graph directly."
    ),
    "artifact_renamed": (
        "Consumed by _build_rename_map during graph construction, not by a per-event handler."
    ),
    "gate_checked": (
        "Consumed by _build_latest_gate_states during graph construction, "
        "not by a per-event handler."
    ),
}


class LedgerEventHandlerCoverage(unittest.TestCase):
    """Every event factory output must be claimed by the graph or explicitly waived."""

    def test_every_event_type_claimed_or_waived(self) -> None:
        emitted = _collect_emitted_event_types(_LEDGER_EVENTS)
        claimed = _collect_claimed_event_types(_LEDGER)

        # Every emitted event must be either handled by the graph or waived.
        unclaimed = sorted(emitted - claimed - NO_GRAPH_IMPACT.keys())
        self.assertFalse(
            unclaimed,
            msg=(
                "Ledger event types emitted by src/gzkit/ledger_events.py but "
                "neither handled by a graph builder in src/gzkit/ledger.py nor "
                "waived in NO_GRAPH_IMPACT. Add a handler OR add a waiver with a "
                "rationale naming the event's real consumer.\n"
                f"Unclaimed: {unclaimed}"
            ),
        )

        # Any waiver that no longer names a real event type is stale — rot
        # accumulates if we don't scrub these.
        stale_waivers = sorted(NO_GRAPH_IMPACT.keys() - emitted)
        self.assertFalse(
            stale_waivers,
            msg=(
                "NO_GRAPH_IMPACT names event types that no longer appear in "
                "ledger_events.py. Remove the stale waiver entries.\n"
                f"Stale: {stale_waivers}"
            ),
        )


def _collect_emitted_event_types(source: Path) -> set[str]:
    """Parse ledger_events.py and return every string literal passed to ``event=``."""
    tree = ast.parse(source.read_text(encoding="utf-8"))
    emitted: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        for keyword in node.keywords:
            if keyword.arg != "event":
                continue
            value = keyword.value
            if isinstance(value, ast.Constant) and isinstance(value.value, str):
                emitted.add(value.value)
    return emitted


def _collect_claimed_event_types(source: Path) -> set[str]:
    """Return every event type string that appears as a literal in ledger.py.

    Claims include direct ``event.event == "<type>"`` comparisons and
    set/frozenset/list/tuple literals (e.g. the ``creation_events`` set used
    by ``_ensure_artifact_entry``). Both forms are valid dispatch paths, so
    both count as "claimed."
    """
    tree = ast.parse(source.read_text(encoding="utf-8"))
    claimed: set[str] = set()
    for node in ast.walk(tree):
        # event.event == "..." / event.event != "..."
        if (
            isinstance(node, ast.Compare)
            and isinstance(node.left, ast.Attribute)
            and node.left.attr == "event"
            and isinstance(node.left.value, ast.Name)
            and node.left.value.id == "event"
        ):
            for comparator in node.comparators:
                if isinstance(comparator, ast.Constant) and isinstance(comparator.value, str):
                    claimed.add(comparator.value)
        # set / frozenset / list / tuple of string literals used for membership checks
        if isinstance(node, (ast.Set, ast.List, ast.Tuple)):
            for elt in node.elts:
                if (
                    isinstance(elt, ast.Constant)
                    and isinstance(elt.value, str)
                    and _looks_like_event_type(elt.value)
                ):
                    claimed.add(elt.value)
    return claimed


def _looks_like_event_type(value: str) -> bool:
    """Heuristic: event types are short snake_case verbs (e.g. ``obpi_created``).

    Used to disambiguate event literals from other string constants. Tight
    enough to avoid false positives; loose enough to catch any event factory
    output emitted by ledger_events.py.
    """
    return bool(re.fullmatch(r"[a-z][a-z0-9]*(?:_[a-z0-9]+)*", value))


if __name__ == "__main__":
    unittest.main()
