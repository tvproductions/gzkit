"""The constitution artifact type has one state set and one location (GHI #1134).

Four declarations disagreed: the registry and the transition table allowed
`Amended`, while the frontmatter model and `schemas/constitution.json` allowed
`Review` but not `Amended`, so a legal transition target failed validation and
a schema-valid state had no transition. The registry's path pattern named
`docs/governance/**/constitution*.md`, where `gz constitute` never writes.
Operator rulings 2026-09-28, verbatim: "Keep Amended (Recommended)",
"Configured path (Recommended)" and "Five states, with Review (Recommended)" --
the last reconciling the docket with the 2026-06-14 ratified lifecycle
Draft→Review→Ratified→Amended→Superseded.
"""

from __future__ import annotations

import json
import typing
import unittest
from importlib.resources import files
from pathlib import PurePosixPath

from gzkit.commands.init_cmd import _canonicalize_constitution_id
from gzkit.config import PathConfig
from gzkit.core.lifecycle import CONSTITUTION_TRANSITIONS, get_all_states
from gzkit.core.models import ConstitutionFrontmatter
from gzkit.registry import REGISTRY

_CANONICAL = {"Draft", "Review", "Ratified", "Amended", "Superseded"}


def _schema_states() -> set[str]:
    schema = json.loads(files("gzkit.schemas").joinpath("constitution.json").read_text("utf-8"))
    return set(schema["properties"]["frontmatter"]["properties"]["status"]["enum"])


def _model_states() -> set[str]:
    return set(typing.get_args(ConstitutionFrontmatter.model_fields["status"].annotation))


class TestConstitutionStateSet(unittest.TestCase):
    """Registry, transitions, model and schema declare the same states."""

    def test_every_source_declares_the_canonical_set(self) -> None:
        sources = {
            "registry": set(REGISTRY.get("Constitution").lifecycle_states),
            "transitions": set(get_all_states("Constitution")),
            "model": _model_states(),
            "schema": _schema_states(),
        }
        for name, states in sources.items():
            with self.subTest(source=name):
                self.assertEqual(states, _CANONICAL)

    def test_registry_points_at_the_model_and_schema_it_agrees_with(self) -> None:
        constitution = REGISTRY.get("Constitution")
        self.assertIs(constitution.frontmatter_model, ConstitutionFrontmatter)
        self.assertEqual(constitution.schema_name, "constitution")

    def test_every_state_is_reachable_from_draft(self) -> None:
        reached, frontier = {"Draft"}, ["Draft"]
        while frontier:
            state = frontier.pop()
            for rule in CONSTITUTION_TRANSITIONS:
                if rule.from_state == state and rule.to_state not in reached:
                    reached.add(rule.to_state)
                    frontier.append(rule.to_state)
        self.assertEqual(reached, _schema_states())


class TestConstitutionLocation(unittest.TestCase):
    """The registry pattern matches where `gz constitute` writes."""

    def test_constitute_output_matches_registry_pattern(self) -> None:
        pattern = REGISTRY.get("Constitution").canonical_path_pattern
        stem, _ = _canonicalize_constitution_id("Charter")
        for root in (PathConfig().constitutions, "docs/design/constitutions"):
            with self.subTest(root=root):
                written = PurePosixPath(root) / f"{stem}.md"
                self.assertTrue(written.full_match(pattern), f"{written} !~ {pattern}")

    def test_pattern_rejects_a_non_constitution_file(self) -> None:
        pattern = REGISTRY.get("Constitution").canonical_path_pattern
        self.assertFalse(PurePosixPath("design/constitutions/README.md").full_match(pattern))


if __name__ == "__main__":
    unittest.main()
