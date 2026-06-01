"""Schema-migration layer tests — OBPI-0.0.34-07.

Derived from REQ-0.0.34-07-{01..05}: schema_version field, migration
registry, auto-migration dispatch, fail-closed unknown versions, and
purity invariant.
"""

from __future__ import annotations

import unittest

from gzkit.content.migration import MIGRATIONS, MigrationError, apply_migrations
from gzkit.content.models import CONTENT_MODELS, Bullet, Rule
from gzkit.content.models.base import BaseContentModel
from gzkit.content.parse import parse
from gzkit.content.render import render
from gzkit.traceability import covers


def _bump_rule_v1_to_v2(model: BaseContentModel) -> BaseContentModel:
    """Test migration: bump Rule schema_version 1 -> 2 (no field changes)."""
    return model.model_copy(update={"schema_version": 2})


def _bump_rule_v2_to_v3(model: BaseContentModel) -> BaseContentModel:
    """Test migration: bump Rule schema_version 2 -> 3 (no field changes)."""
    return model.model_copy(update={"schema_version": 3})


class TestSchemaVersionField(unittest.TestCase):
    """REQ-0.0.34-07-01: schema_version: int on every content-model base."""

    @covers("REQ-0.0.34-07-01")
    def test_base_model_declares_schema_version_default_one(self) -> None:
        """BaseContentModel declares schema_version: int = 1 at class level."""
        field = BaseContentModel.model_fields["schema_version"]
        self.assertEqual(field.default, 1)
        self.assertIs(field.annotation, int)

    @covers("REQ-0.0.34-07-01")
    def test_all_content_models_inherit_schema_version(self) -> None:
        """Every model in CONTENT_MODELS exposes schema_version with default 1."""
        for type_name, model_cls in CONTENT_MODELS.items():
            with self.subTest(content_type=type_name):
                self.assertIn(
                    "schema_version",
                    model_cls.model_fields,
                    f"{type_name} missing schema_version field",
                )
                self.assertEqual(model_cls.model_fields["schema_version"].default, 1)


class TestMigrationRegistry(unittest.TestCase):
    """REQ-0.0.34-07-02: MIGRATIONS dict structure and key shape."""

    @covers("REQ-0.0.34-07-02")
    def test_migrations_is_dict(self) -> None:
        """MIGRATIONS is the public dict[tuple[str, int, int], Callable] export."""
        self.assertIsInstance(MIGRATIONS, dict)

    @covers("REQ-0.0.34-07-02")
    def test_apply_migrations_is_identity_when_versions_equal(self) -> None:
        """apply_migrations(model, ..., v, v) returns the model unchanged."""
        model = Rule(title="T", version="1.0.0", paths=[], body=[])
        result = apply_migrations(model, "Rule", source_version=1, target_version=1)
        self.assertEqual(result, model)


class TestAutoMigrationOnParse(unittest.TestCase):
    """REQ-0.0.34-07-03: parser auto-migrates when source schema_version differs."""

    def setUp(self) -> None:
        self._registered_keys: list[tuple[str, int, int]] = []

    def tearDown(self) -> None:
        for key in self._registered_keys:
            MIGRATIONS.pop(key, None)

    def _register(self, key: tuple[str, int, int], fn) -> None:
        MIGRATIONS[key] = fn
        self._registered_keys.append(key)

    @covers("REQ-0.0.34-07-03")
    def test_sequential_migrations_applied_in_order(self) -> None:
        """apply_migrations chains registered v_n -> v_{n+1} migrations."""
        self._register(("Rule", 1, 2), _bump_rule_v1_to_v2)
        self._register(("Rule", 2, 3), _bump_rule_v2_to_v3)
        model = Rule(title="T", version="1.0.0", paths=[], body=[])
        result = apply_migrations(model, "Rule", source_version=1, target_version=3)
        self.assertEqual(result.schema_version, 3)

    @covers("REQ-0.0.34-07-03")
    def test_parse_stable_when_source_matches_current_version(self) -> None:
        """parse() returns a model with schema_version=1 when source omits the line."""
        model = Rule(
            title="Sample",
            version="0.1.0",
            paths=["src/**/*.py"],
            body=[Bullet(text="b1", indent=0)],
        )
        rendered = render(model, "claude").decode("utf-8")
        parsed = parse(rendered, "Rule")
        self.assertEqual(parsed.schema_version, 1)
        self.assertEqual(parsed, model)


class TestUnknownVersionFailClosed(unittest.TestCase):
    """REQ-0.0.34-07-04: unknown / missing migration paths fail-closed."""

    def setUp(self) -> None:
        self._registered_keys: list[tuple[str, int, int]] = []

    def tearDown(self) -> None:
        for key in self._registered_keys:
            MIGRATIONS.pop(key, None)

    def _register(self, key: tuple[str, int, int], fn) -> None:
        MIGRATIONS[key] = fn
        self._registered_keys.append(key)

    @covers("REQ-0.0.34-07-04")
    def test_future_source_version_raises_migration_error(self) -> None:
        """source_version > target_version raises MigrationError naming the version."""
        model = Rule(title="T", version="1.0.0", paths=[], body=[])
        with self.assertRaises(MigrationError) as ctx:
            apply_migrations(model, "Rule", source_version=999, target_version=1)
        self.assertIn("999", str(ctx.exception))

    @covers("REQ-0.0.34-07-04")
    def test_missing_migration_step_raises_migration_error(self) -> None:
        """A gap in the migration chain raises MigrationError; we NEVER guess."""
        # Register only 1->2; ask for 1->3 so the (Rule, 2, 3) step is missing.
        self._register(("Rule", 1, 2), _bump_rule_v1_to_v2)
        model = Rule(title="T", version="1.0.0", paths=[], body=[])
        with self.assertRaises(MigrationError) as ctx:
            apply_migrations(model, "Rule", source_version=1, target_version=3)
        message = str(ctx.exception)
        self.assertIn("Rule", message)
        self.assertIn("2", message)
        self.assertIn("3", message)


class TestMigrationPurity(unittest.TestCase):
    """REQ-0.0.34-07-05: migrations are deterministic and side-effect-free."""

    @covers("REQ-0.0.34-07-05")
    def test_migration_callable_yields_equal_outputs_on_repeat(self) -> None:
        """Calling a registered migration twice on the same input produces equal output."""
        model = Rule(title="T", version="1.0.0", paths=[], body=[])
        first = _bump_rule_v1_to_v2(model)
        second = _bump_rule_v1_to_v2(model)
        self.assertEqual(first, second)
        # Source model is unchanged (frozen + pure).
        self.assertEqual(model.schema_version, 1)


class TestReverseParseFullContract(unittest.TestCase):
    """OBPI-0.0.37-13: full-contract reverse parse of AGENTS.md into the master model."""

    def _import_agents_md(self):
        from pathlib import Path  # noqa: PLC0415

        agents = Path(__file__).resolve().parents[2] / "AGENTS.md"
        return parse(agents.read_text(encoding="utf-8"), "AgentContract", file_path=str(agents))

    @covers("REQ-0.0.37-13-01")
    def test_import_populates_a_pillar_for_every_section(self) -> None:
        """Every ## section becomes a Pillar whose body is captured verbatim — not the
        name+purpose stub (regression floor: the old parser yielded a 161-byte model)."""
        model = self._import_agents_md()
        self.assertGreater(len(model.pillars), 5, "pillars must cover the ## sections")
        titles = {p.title for p in model.pillars}
        self.assertIn("Behavior Rules", titles)
        behavior = next(p for p in model.pillars if p.title == "Behavior Rules")
        self.assertIn("AGENTS.md", "\n".join(behavior.lines))
        self.assertTrue(behavior.bullets, "Behavior Rules must yield rule bullets")

    @covers("REQ-0.0.37-13-01")
    def test_import_beats_the_stub_size(self) -> None:
        """Structural faithfulness: the serialized model is orders larger than the 161-byte stub."""
        model = self._import_agents_md()
        self.assertGreater(len(model.model_dump_json()), 5000)

    @covers("REQ-0.0.37-13-02")
    def test_classification_joined_from_advisory_scorecard(self) -> None:
        """Per-bullet classification is joined from the advisory scorecard, not inferred from
        prose: the scorecard scores 'Never prefix `uv run gz` ...' Mechanical."""
        model = self._import_agents_md()
        bullets = [b for p in model.pillars for b in p.bullets]
        match = next(b for b in bullets if "Never prefix" in b.text and "uv run gz" in b.text)
        self.assertEqual(match.classification, "Mechanical")

    @covers("REQ-0.0.37-13-03")
    def test_agents_local_content_present_as_model_rows(self) -> None:
        """The .gzkit/agents.local.md content (spliced into AGENTS.md) is captured as model
        rows. Physical removal of the source file is OBPI-14 (scope correction, Option A)."""
        model = self._import_agents_md()
        rows = "\n".join(line for p in model.pillars for line in p.lines)
        self.assertIn("Operator PII", rows)  # a rule authored in .gzkit/agents.local.md

    @covers("REQ-0.0.37-13-05")
    def test_unmatched_bullet_defaults_to_ambiguous(self) -> None:
        """A bullet with no scorecard match classifies Ambiguous — never silently Mechanical,
        which would let the density dial thin an unenforced rule."""
        text = (
            "# Contract\n\nPurpose line.\n\n"
            "## Custom Section\n\n- zzz unmatchable qpwoeiruty rule\n"
        )
        model = parse(text, "AgentContract")
        custom = next(p for p in model.pillars if p.title == "Custom Section")
        self.assertEqual(len(custom.bullets), 1)
        self.assertEqual(custom.bullets[0].classification, "Ambiguous")


if __name__ == "__main__":
    unittest.main()
