"""A shipped chore's criteria run where the chore is delivered (GHI #1114).

`gz init` delivers every chore the registry does not mark ``projectLocal`` into
an adopter's ``.gzkit/chores/<slug>/``, scripts included. A criterion naming
``src/gzkit/…`` or gzkit's top-level ``scripts/…`` resolves only in the gzkit
tree, so eight delivered chores could not be run by the people they were sent
to. A script belongs at ``.gzkit/chores/<slug>/<script>.py``, the path that
resolves in both trees; a chore that only makes sense for gzkit is
``projectLocal`` and never delivered.
"""

from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
_CHORES = _ROOT / ".gzkit" / "chores"
_GZKIT_ONLY = re.compile(r"(?<![\w./-])(?:src/gzkit/|scripts/)[\w./-]+")


def _registry_slugs(*, project_local: bool) -> list[str]:
    registry = json.loads((_CHORES / "registry.json").read_text(encoding="utf-8"))
    return [c["slug"] for c in registry["chores"] if bool(c.get("projectLocal")) is project_local]


def _shipped_slugs() -> list[str]:
    return _registry_slugs(project_local=False)


def _commands(slug: str) -> list[str]:
    acceptance = _CHORES / slug / "acceptance.json"
    if not acceptance.is_file():
        return []
    criteria = json.loads(acceptance.read_text(encoding="utf-8")).get("criteria", [])
    return [c["command"] for c in criteria if isinstance(c.get("command"), str)]


def gzkit_only_paths(slugs: list[str]) -> list[str]:
    """Return ``slug: path`` for each gzkit-only path a shipped criterion names."""
    return [
        f"{slug}: {path}"
        for slug in slugs
        for command in _commands(slug)
        for path in _GZKIT_ONLY.findall(command)
    ]


class ShippedChoreCriteriaTests(unittest.TestCase):
    def test_no_shipped_criterion_names_a_gzkit_only_path(self) -> None:
        self.assertEqual(gzkit_only_paths(_shipped_slugs()), [])

    def test_the_check_sees_a_gzkit_only_path(self) -> None:
        """Control: run over a projectLocal chore, the check reports its gzkit-only path."""
        self.assertIn("frontier-model-card-currency", _registry_slugs(project_local=True))
        self.assertIn(
            "frontier-model-card-currency: scripts/check_proof_freshness.py",
            gzkit_only_paths(["frontier-model-card-currency"]),
        )


if __name__ == "__main__":
    unittest.main()
