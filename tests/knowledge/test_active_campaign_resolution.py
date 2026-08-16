"""The knowledge bundle's active-campaign source follows the registry.

``TRACER_SLICE`` names the campaign plan by path, and that path has now been
wrong twice in two different ways -- which is the argument for the shape it has
today.

First it was **hardcoded** to ``build-to-1.0-campaign-2026-06-30.md`` and stayed
there through two supersessions (06-30 -> 07-18 -> 08-16), so ``gz knowledge``
shipped an "Active Campaign" concept sourced from a plan that had not steered
since 2026-07-18. Then it was a **regex over each plan's prose** ``Status:``
line -- correct, but maintained in two copies on opposite sides of the wheel
boundary, over text one character from ambiguity (every superseded edition reads
``**SUPERSEDED -- was ACTIVE**``).

Now it reads ``data/active_campaign.json``. The operative difference is not that
JSON is tidier: a hardcoded path and a prose scan both fail *silently*, whereas
an undeclared edition fails ``tests/governance/test_active_campaign_registry.py``
closed. These tests cover the resolution; that module covers the declaration.
"""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from gzkit.knowledge.generate import (
    ACTIVE_CAMPAIGN_REGISTRY,
    TRACER_SLICE,
    resolve_active_campaign,
)


def _declared_active() -> Path:
    """The plan the registry names, read the way production reads it."""
    return Path(json.loads(ACTIVE_CAMPAIGN_REGISTRY.read_text(encoding="utf-8"))["active"])


class TestTracerSliceFollowsTheRegistry(unittest.TestCase):
    """The bundle sources the plan that governs, not one that governed once."""

    def test_tracer_slice_names_the_active_campaign(self) -> None:
        entries = dict(TRACER_SLICE)
        self.assertIn("active-campaign", entries)
        self.assertEqual(
            entries["active-campaign"],
            _declared_active(),
            "the knowledge bundle's active-campaign source does not follow the "
            "registry -- `gz knowledge` would ship a plan that no longer steers "
            "as canon",
        )


class TestResolverSelection(unittest.TestCase):
    """The resolver's decision logic, exercised without the live corpus.

    `gz validate --tautological-test-audit` refused this class's first form,
    which asserted that each tracer source ``is_file()``. It was right: file
    existence is content, not behavior (`.gzkit/rules/tests.md` § The
    discriminator -- *if the production code's behavior changed but its text did
    not, would this test fail?*). These exercise the selection rule instead, on
    a temp registry, so they fail when the rule changes rather than when the
    repository does.
    """

    def _registry(self, root: Path, active: str) -> Path:
        """Write a registry naming *active*, plus the plan file it points at."""
        plan = root / active
        plan.parent.mkdir(parents=True, exist_ok=True)
        plan.write_text("# Plan\n\nStatus: **ACTIVE**\n", encoding="utf-8")
        path = root / "active_campaign.json"
        path.write_text(json.dumps({"active": str(plan)}), encoding="utf-8")
        return path

    def test_the_registry_decides_not_the_filename_date(self) -> None:
        """An older edition wins when the registry names it.

        Newest-by-name is only the anomaly fallback; it must never outrank an
        explicit declaration, or supersession could not be reversed.
        """
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "build-to-1.0-campaign-2026-09-09.md").write_text("# newer\n", encoding="utf-8")
            registry = self._registry(root, "build-to-1.0-campaign-2026-01-01.md")
            self.assertEqual(
                resolve_active_campaign(registry).name,
                "build-to-1.0-campaign-2026-01-01.md",
            )

    def test_a_missing_registry_falls_back_rather_than_raising(self) -> None:
        """A governance-state anomaly must not fail bundle generation closed."""
        with tempfile.TemporaryDirectory() as tmp:
            resolved = resolve_active_campaign(Path(tmp) / "absent.json")
            self.assertTrue(resolved.name.endswith(".md"))

    def test_a_registry_naming_a_missing_plan_falls_back(self) -> None:
        """The hardcoded-pointer defect, in its new home.

        A registry can name a file that has been renamed or deleted, so pointing
        at the declaration is not by itself proof the declaration resolves. The
        anomaly is reported by the registry coherence tests; here it degrades.
        """
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            registry = root / "active_campaign.json"
            registry.write_text(json.dumps({"active": "docs/gone.md"}), encoding="utf-8")
            self.assertNotEqual(resolve_active_campaign(registry), Path("docs/gone.md"))

    def test_malformed_registry_json_falls_back(self) -> None:
        """Never crash the bundle on a half-written or hand-edited file."""
        with tempfile.TemporaryDirectory() as tmp:
            registry = Path(tmp) / "active_campaign.json"
            registry.write_text("{not json", encoding="utf-8")
            self.assertTrue(resolve_active_campaign(registry).name.endswith(".md"))

    def test_a_registry_without_an_active_key_falls_back(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            registry = Path(tmp) / "active_campaign.json"
            registry.write_text(json.dumps({"superseded": []}), encoding="utf-8")
            self.assertTrue(resolve_active_campaign(registry).name.endswith(".md"))


if __name__ == "__main__":
    unittest.main()
