"""OBPI brief finders and the TASK resolver follow the identity seam (drydock RO-2 tranche 3).

`docs/governance/harbor-ro2-identity-seam.md` § Tranches row 3. A short OBPI id
expands only across a ``-`` separator, and an id that stays ambiguous among the
briefs on disk names none of them: the separator-less ``{id}*.md`` glob took the
first sorted match, so ``OBPI-0.28.0-1`` read items 10 to 19.
"""

from __future__ import annotations

import json
import tempfile
import unittest
from collections.abc import Callable
from pathlib import Path

from gzkit.commands.obpi_precomplete import resolve_brief_path
from gzkit.commands.task import _resolve_obpi_id, _resolve_task_context
from gzkit.core.id_resolver import IdentityContext, resolve_full
from gzkit.ledger import Ledger
from gzkit.pipeline_markers import find_obpi_brief

_ADR_A = Path("design/adr/pre-release/ADR-0.28.0-focused-context-loader/obpis")
_ADR_B = Path("design/adr/pre-release/ADR-0.28.0-other/obpis")


def _brief(root: Path, rel_dir: Path, stem: str) -> Path:
    directory = root / rel_dir
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{stem}.md"
    path.write_text(f"---\nid: {stem}\n---\n# {stem}\n", encoding="utf-8")
    return path


class TestBriefFindersExpandOnlyAcrossASeparator(unittest.TestCase):
    """Two briefs under one item prefix are ambiguous; item 1 is not item 10."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)

    def _finders(self) -> tuple[Callable[[str], Path | None], Callable[[str], Path | None]]:
        return (
            lambda obpi_id: find_obpi_brief(self.root / "design" / "adr", obpi_id),
            lambda obpi_id: resolve_brief_path(self.root, obpi_id),
        )

    def test_item_prefix_does_not_reach_items_ten_to_nineteen(self) -> None:
        _brief(self.root, _ADR_A, "OBPI-0.28.0-10-ten")
        _brief(self.root, _ADR_A, "OBPI-0.28.0-11-eleven")
        for find in self._finders():
            self.assertIsNone(find("OBPI-0.28.0-1"))

    def test_short_id_naming_two_briefs_names_none_of_them(self) -> None:
        _brief(self.root, _ADR_A, "OBPI-0.28.0-01-context-core")
        _brief(self.root, _ADR_B, "OBPI-0.28.0-01-chores-cli")
        for find in self._finders():
            self.assertIsNone(find("OBPI-0.28.0-01"))

    def test_short_id_naming_one_brief_finds_it(self) -> None:
        path = _brief(self.root, _ADR_A, "OBPI-0.28.0-01-context-core")
        _brief(self.root, _ADR_A, "OBPI-0.28.0-10-ten")
        for find in self._finders():
            self.assertEqual(find("OBPI-0.28.0-01"), path)

    def test_full_id_is_exact_even_when_a_longer_slug_extends_it(self) -> None:
        path = _brief(self.root, _ADR_A, "OBPI-0.28.0-01-context")
        _brief(self.root, _ADR_A, "OBPI-0.28.0-01-context-core")
        for find in self._finders():
            self.assertEqual(find("OBPI-0.28.0-01-context"), path)

    def test_full_id_naming_no_brief_is_not_the_nearest_sibling(self) -> None:
        _brief(self.root, _ADR_A, "OBPI-0.28.0-01-context-core")
        for find in self._finders():
            self.assertIsNone(find("OBPI-0.28.0-01-chores-cli"))


def _ledger(root: Path, obpi_ids: list[str], parked: tuple[str, ...] = ()) -> Ledger:
    gz = root / ".gzkit"
    gz.mkdir(parents=True, exist_ok=True)
    path = gz / "ledger.jsonl"
    base = {"schema": "gzkit.ledger.v1", "ts": "2026-07-29T00:00:00+00:00", "agent": "test"}
    rows = [{**base, "event": "obpi_created", "id": obpi_id} for obpi_id in obpi_ids]
    rows += [{**base, "event": "obpi_parked", "id": obpi_id} for obpi_id in parked]
    path.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")
    return Ledger(path)


class TestTaskResolvesOBPIThroughTheSeam(unittest.TestCase):
    """The short OBPI id a TASK carries resolves by the one resolver."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)

    def test_item_prefix_never_expands_to_a_longer_item(self) -> None:
        ledger = _ledger(self.root, ["OBPI-0.28.0-10-ten"])
        self.assertEqual(_resolve_obpi_id(ledger, "OBPI-0.28.0-1"), "OBPI-0.28.0-1")

    def test_task_context_disambiguates_phantom_by_brief_when_given_the_root(self) -> None:
        real, phantom = "OBPI-0.28.0-01-context-core", "OBPI-0.28.0-01-insight-harvester"
        ledger = _ledger(self.root, [real, phantom])
        _brief(self.root, Path("docs") / _ADR_A, real)
        _, obpi_id, _ = _resolve_task_context(
            ledger, "TASK-0.28.0-01-01-01", project_root=self.root
        )
        self.assertEqual(obpi_id, real)

    def test_parked_sibling_yields_to_the_active_obpi_without_a_root(self) -> None:
        live, parked = "OBPI-0.28.0-01-context-core", "OBPI-0.28.0-01-chores-cli"
        ledger = _ledger(self.root, [live, parked], parked=(parked,))
        self.assertEqual(_resolve_obpi_id(ledger, "OBPI-0.28.0-01"), live)
        self.assertEqual(_resolve_task_context(ledger, "TASK-0.28.0-01-01-01")[1], live)


class TestResolveFullNamesTheSlugThePipelineRecords(unittest.TestCase):
    """``resolve_full`` prefers the one slug extension of a short form (GHI #653)."""

    @staticmethod
    def _context(*keys: str) -> IdentityContext:
        return IdentityContext(graph={key: {"type": "obpi"} for key in keys})

    def test_short_key_shadowing_one_slug_resolves_to_the_slug(self) -> None:
        context = self._context("OBPI-0.1.0-01", "OBPI-0.1.0-01-the-slug")
        self.assertEqual(
            resolve_full("OBPI-0.1.0-01", context).canonical_id, "OBPI-0.1.0-01-the-slug"
        )

    def test_short_key_alone_resolves_to_itself(self) -> None:
        context = self._context("OBPI-0.1.0-01")
        self.assertEqual(resolve_full("OBPI-0.1.0-01", context).canonical_id, "OBPI-0.1.0-01")

    def test_short_key_with_two_slugs_stays_the_short_key(self) -> None:
        context = self._context("OBPI-0.1.0-01", "OBPI-0.1.0-01-a", "OBPI-0.1.0-01-b")
        self.assertEqual(resolve_full("OBPI-0.1.0-01", context).canonical_id, "OBPI-0.1.0-01")


if __name__ == "__main__":
    unittest.main()
