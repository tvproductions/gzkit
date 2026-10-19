"""The identity seam's resolver and parent lookup (drydock RO-2 tranche 1).

`docs/governance/harbor-ro2-identity-seam.md` § The seam, items 2 and 3: one
``resolve`` over the rename fold and the active-prefix rule, failing closed on
ambiguity, and one ``parent_of`` that reads stored fields before it falls back to
an id's spelling. The fixture is the reused ``OBPI-0.28.0-01`` slot: parked
``chores-cli`` under a pool ADR, live ``context-core`` under ``ADR-0.28.0``.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from typing import Any

from gzkit.core.id_resolver import (
    IdentityContext,
    IdResolutionError,
    load_identity_context,
    parent_of,
    resolve,
)
from gzkit.core.models import IdKind

_POOL = "ADR-pool.chores-system-maturity-absorption"
_LIVE_ADR = "ADR-0.28.0-focused-context-loader"
_PARKED = "OBPI-0.28.0-01-chores-cli"
_LIVE = "OBPI-0.28.0-01-context-core"


def _graph() -> dict[str, dict[str, Any]]:
    return {
        _POOL: {"type": "adr", "parent": "PRD-GZKIT-1.0.0"},
        _LIVE_ADR: {"type": "adr", "parent": "PRD-GZKIT-1.0.0"},
        _PARKED: {"type": "obpi", "parent": _POOL, "parked": True},
        _LIVE: {"type": "obpi", "parent": _LIVE_ADR},
        "OBPI-0.1.0-10-tenth": {"type": "obpi", "parent": "ADR-0.1.0-x"},
        "OBPI-0.2.0-01-left": {"type": "obpi", "parent": "ADR-0.2.0-y"},
        "OBPI-0.2.0-01-right": {"type": "obpi", "parent": "ADR-0.2.0-y"},
        "OBPI-0.3.0-01-gone": {"type": "obpi", "parent": "ADR-0.3.0-z", "withdrawn": True},
        "ADR-0.1.0-x": {"type": "adr"},
        "ADR-0.2.0-y": {"type": "adr"},
        "ADR-0.3.0-z": {"type": "adr"},
    }


def _context(**overrides: Any) -> IdentityContext:
    fields: dict[str, Any] = {
        "graph": _graph(),
        "renames": {"OBPI-0.28.0-01-old-name": _LIVE},
        "brief_parents": {_LIVE: _LIVE_ADR, _PARKED: _POOL},
        "req_owners": {
            "REQ-0.28.0-01-01": (_PARKED, _LIVE),
            "REQ-0.28.0-01-09": (_PARKED,),
        },
        "task_obpis": {"TASK-0.28.0-01-01-01": "OBPI-0.28.0-01"},
    }
    fields.update(overrides)
    return IdentityContext(**fields)


class TestResolveTheReusedSlot(unittest.TestCase):
    """``OBPI-0.28.0-01`` resolves both ways."""

    def test_the_short_id_names_the_live_obpi(self) -> None:
        resolution = resolve("OBPI-0.28.0-01", _context())
        self.assertEqual(resolution.canonical_id, _LIVE)
        self.assertIs(resolution.kind, IdKind.OBPI)
        self.assertEqual(resolution.state, "active")

    def test_the_parked_full_id_resolves_to_itself_recorded_parked(self) -> None:
        resolution = resolve(_PARKED, _context())
        self.assertEqual(resolution.canonical_id, _PARKED)
        self.assertEqual(resolution.state, "parked")

    def test_a_renamed_id_follows_the_fold(self) -> None:
        self.assertEqual(resolve("OBPI-0.28.0-01-old-name", _context()).canonical_id, _LIVE)

    def test_a_short_adr_id_expands(self) -> None:
        self.assertEqual(resolve("ADR-0.28.0", _context()).canonical_id, _LIVE_ADR)
        self.assertEqual(resolve(_POOL, _context()).canonical_id, _POOL)


class TestResolveFailsClosed(unittest.TestCase):
    def test_an_ambiguous_short_id_names_every_candidate(self) -> None:
        with self.assertRaises(IdResolutionError) as caught:
            resolve("OBPI-0.2.0-01", _context())
        self.assertEqual(caught.exception.candidates, ("OBPI-0.2.0-01-left", "OBPI-0.2.0-01-right"))

    def test_a_short_id_expands_only_across_a_separator(self) -> None:
        with self.assertRaises(IdResolutionError) as caught:
            resolve("OBPI-0.1.0-1", _context())
        self.assertEqual(caught.exception.candidates, ())

    def test_an_unknown_id_and_a_non_id_are_refused(self) -> None:
        for value in (
            "OBPI-9.9.9-01",
            "ADR-9.9.9",
            "GHI-12",
            "TASK-0.9.0-01-01-01",
            "REQ-0.15.0",
            "REQ-0.28.0-1-1",
        ):
            with self.subTest(value=value), self.assertRaises(IdResolutionError):
                resolve(value, _context())

    def test_a_withdrawn_sole_candidate_resolves_recorded_withdrawn(self) -> None:
        self.assertEqual(resolve("OBPI-0.3.0-01", _context()).state, "withdrawn")


class TestResolveReqAndTask(unittest.TestCase):
    def test_a_reused_req_takes_the_active_owner(self) -> None:
        resolution = resolve("REQ-0.28.0-01-01", _context())
        self.assertEqual(resolution.canonical_id, "REQ-0.28.0-01-01")
        self.assertIs(resolution.kind, IdKind.REQ)
        self.assertEqual(resolution.state, "active")

    def test_a_req_owned_only_by_a_parked_obpi_is_recorded_parked(self) -> None:
        self.assertEqual(resolve("REQ-0.28.0-01-09", _context()).state, "parked")

    def test_a_req_no_brief_owns_is_refused(self) -> None:
        with self.assertRaises(IdResolutionError):
            resolve("REQ-0.28.0-01-02", _context())

    def test_a_briefless_req_of_a_parked_obpi_is_recorded_parked(self) -> None:
        """A pool demotion removes the brief; the parked OBPI still owns its REQs."""
        context = _context(
            graph={**_graph(), "OBPI-0.7.0-01-demoted": {"type": "obpi", "parked": True}}
        )
        self.assertEqual(resolve("REQ-0.7.0-01-01", context).state, "parked")
        link = parent_of("REQ-0.7.0-01-01", context)
        self.assertEqual((link.parent_id, link.source), ("OBPI-0.7.0-01-demoted", "spelling"))
        live = _context(graph={**_graph(), "OBPI-0.7.0-01-live": {"type": "obpi"}})
        with self.assertRaises(IdResolutionError):
            resolve("REQ-0.7.0-01-01", live)

    def test_a_req_two_active_obpis_own_is_ambiguous(self) -> None:
        context = _context(
            req_owners={"REQ-0.2.0-01-01": ("OBPI-0.2.0-01-left", "OBPI-0.2.0-01-right")}
        )
        with self.assertRaises(IdResolutionError) as caught:
            resolve("REQ-0.2.0-01-01", context)
        self.assertEqual(caught.exception.candidates, ("OBPI-0.2.0-01-left", "OBPI-0.2.0-01-right"))

    def test_a_brief_whose_own_id_names_nothing_is_skipped_as_an_owner(self) -> None:
        context = _context(req_owners={"REQ-0.28.0-01-01": ("OBPI-9.9.9-01-ghost", _LIVE)})
        self.assertEqual(resolve("REQ-0.28.0-01-01", context).state, "active")

    def test_an_unstarted_task_is_refused_as_not_started(self) -> None:
        with self.assertRaises(IdResolutionError) as caught:
            resolve("TASK-0.28.0-01-01-02", _context())
        self.assertIn("started TASK", str(caught.exception))

    def test_a_started_task_resolves(self) -> None:
        self.assertIs(resolve("TASK-0.28.0-01-01-01", _context()).kind, IdKind.TASK)


class TestParentOf(unittest.TestCase):
    def test_an_obpi_parent_is_its_stored_field_not_its_spelling(self) -> None:
        link = parent_of(_PARKED, _context())
        self.assertEqual((link.parent_id, link.source), (_POOL, "ledger"))
        self.assertEqual(parent_of("OBPI-0.28.0-01", _context()).parent_id, _LIVE_ADR)

    def test_an_obpi_outside_the_ledger_reads_its_brief(self) -> None:
        context = _context(brief_parents={"OBPI-0.4.0-01-new": "ADR-0.4.0-w"})
        context.graph["OBPI-0.4.0-01-new"] = {"type": "obpi"}
        link = parent_of("OBPI-0.4.0-01-new", context)
        self.assertEqual((link.parent_id, link.source), ("ADR-0.4.0-w", "brief"))

    def test_an_obpi_with_no_stored_parent_falls_back_to_spelling_marked(self) -> None:
        context = _context(brief_parents={})
        context.graph["OBPI-0.5.0-01-bare"] = {"type": "obpi"}
        link = parent_of("OBPI-0.5.0-01-bare", context)
        self.assertEqual((link.parent_id, link.source), ("ADR-0.5.0", "spelling"))

    def test_a_req_parent_is_its_owning_brief(self) -> None:
        link = parent_of("REQ-0.28.0-01-01", _context())
        self.assertEqual((link.parent_id, link.source), (_LIVE, "brief"))

    def test_a_task_parent_req_is_spelled_and_says_so(self) -> None:
        link = parent_of("TASK-0.28.0-01-01-01", _context())
        self.assertEqual((link.parent_id, link.source), ("REQ-0.28.0-01-01", "spelling"))

    def test_an_adr_with_no_stored_parent_has_none(self) -> None:
        self.assertIsNone(parent_of("ADR-0.1.0-x", _context()))

    def test_an_adr_parent_is_its_stored_field(self) -> None:
        link = parent_of(_LIVE_ADR, _context())
        self.assertEqual((link.parent_id, link.source), ("PRD-GZKIT-1.0.0", "ledger"))


class TestLoadIdentityContext(unittest.TestCase):
    """The loader reads the ledger and the briefs it is handed, nothing else."""

    def test_it_folds_renames_indexes_briefs_and_started_tasks(self) -> None:
        events = [
            SimpleNamespace(
                event="artifact_renamed", id="OBPI-0.6.0-01-a", extra={"new_id": "OBPI-0.6.0-01-b"}
            ),
            SimpleNamespace(
                event="task_started", id="TASK-0.6.0-01-01-01", extra={"obpi_id": "OBPI-0.6.0-01"}
            ),
        ]
        ledger = SimpleNamespace(
            get_artifact_graph=lambda: {
                "OBPI-0.6.0-01-b": {"type": "obpi", "parent": "ADR-0.6.0-v"}
            },
            read_all=lambda: events,
        )
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            obpis = root / "docs" / "design" / "adr" / "pre-release" / "ADR-0.6.0-v" / "obpis"
            obpis.mkdir(parents=True)
            (obpis / "OBPI-0.6.0-01-b.md").write_text(
                "---\nid: OBPI-0.6.0-01-b\nparent: ADR-0.6.0-v\n---\n\n"
                "## Acceptance Criteria\n\n- [x] REQ-0.6.0-01-01 [BEHAVIOR]: works\n",
                encoding="utf-8",
            )
            (obpis / "notes.md").write_text(
                "---\nid: ADR-0.6.0-v\n---\n\n## Acceptance Criteria\n\n"
                "- [x] REQ-0.6.0-09-01 [BEHAVIOR]: not a brief\n",
                encoding="utf-8",
            )
            context = load_identity_context(ledger, root, "docs/design")

        self.assertEqual(context.renames, {"OBPI-0.6.0-01-a": "OBPI-0.6.0-01-b"})
        self.assertEqual(context.brief_parents, {"OBPI-0.6.0-01-b": "ADR-0.6.0-v"})
        self.assertEqual(context.req_owners, {"REQ-0.6.0-01-01": ("OBPI-0.6.0-01-b",)})
        self.assertEqual(context.task_obpis, {"TASK-0.6.0-01-01-01": "OBPI-0.6.0-01"})
        self.assertEqual(resolve("OBPI-0.6.0-01-a", context).canonical_id, "OBPI-0.6.0-01-b")


if __name__ == "__main__":
    unittest.main()
