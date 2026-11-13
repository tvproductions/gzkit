"""Tests for @advances decorator and TASK attribution registry (OBPI-0.0.64-02).

Validates TASK ID format checking at decoration time, brief-backed parent-REQ
existence validation, TaskAttributionRecord registration, metadata-only
behavior on decorated functions, and registry query API.
"""

import re
import unittest
from pathlib import Path

from gzkit.tasks import (
    TaskAttributionRecord,
    advances,
    get_task_registry,
    reset_task_registry,
    set_known_task_reqs,
)
from gzkit.traceability import covers

_TEST_TASK_REQS = frozenset(
    {
        "REQ-0.0.64-02-01",
        "REQ-0.0.64-02-02",
        "REQ-0.0.64-02-03",
        "REQ-0.20.0-01-01",
    }
)


class TestAdvancesFormatValidation(unittest.TestCase):
    """TASK ID format validation at decoration time."""

    def setUp(self):
        reset_task_registry()
        set_known_task_reqs(_TEST_TASK_REQS)

    def tearDown(self):
        reset_task_registry()

    @covers("REQ-0.0.64-02-01")
    def test_valid_task_id_accepted(self):
        @advances("TASK-0.0.64-02-01-01")
        def task_fn():
            return 42

        self.assertEqual(task_fn(), 42)

    @covers("REQ-0.0.64-02-01")
    def test_invalid_format_raises_value_error(self):
        with self.assertRaises(ValueError) as ctx:

            @advances("INVALID")
            def task_fn():
                pass

        self.assertIn("Invalid TASK identifier", str(ctx.exception))

    @covers("REQ-0.0.64-02-01")
    def test_empty_string_raises_value_error(self):
        with self.assertRaises(ValueError):

            @advances("")
            def task_fn():
                pass

    @covers("REQ-0.0.64-02-01")
    def test_unknown_parent_req_raises_value_error(self):
        with self.assertRaises(ValueError) as ctx:

            @advances("TASK-9.9.9-99-99-01")
            def task_fn():
                pass

        self.assertIn("Unknown", str(ctx.exception))
        self.assertIn("REQ-9.9.9-99-99", str(ctx.exception))


class TestAdvancesRegistry(unittest.TestCase):
    """TaskAttributionRecord registration and registry query API."""

    def setUp(self):
        reset_task_registry()
        set_known_task_reqs(_TEST_TASK_REQS)

    def tearDown(self):
        reset_task_registry()

    @covers("REQ-0.0.64-02-02")
    def test_registry_initially_empty(self):
        self.assertEqual(get_task_registry(), [])

    @covers("REQ-0.0.64-02-02")
    def test_decoration_registers_record(self):
        @advances("TASK-0.0.64-02-01-01")
        def my_task_fn():
            return "ok"

        registry = get_task_registry()
        self.assertEqual(len(registry), 1)

        record = registry[0]
        self.assertIsInstance(record, TaskAttributionRecord)
        self.assertEqual(record.task_id, "TASK-0.0.64-02-01-01")
        self.assertIn("my_task_fn", record.source_fn)
        self.assertIsNotNone(record.source_file)
        # Path must be rendered via .as_posix() per cross-platform rule
        self.assertNotIn("\\", record.source_file or "")
        self.assertIsNotNone(record.source_line)
        self.assertGreater(record.source_line or 0, 0)

    @covers("REQ-0.0.64-02-02")
    def test_record_is_frozen(self):
        from pydantic import ValidationError

        @advances("TASK-0.0.64-02-01-01")
        def my_task_fn():
            return "ok"

        record = get_task_registry()[0]
        with self.assertRaises(ValidationError):
            record.task_id = "TASK-other"  # ty: ignore[invalid-assignment]

    @covers("REQ-0.0.64-02-02")
    def test_record_extra_forbid(self):
        from pydantic import ValidationError

        with self.assertRaises(ValidationError):
            TaskAttributionRecord.model_validate(
                {
                    "task_id": "TASK-0.0.64-02-01-01",
                    "source_fn": "fn",
                    "source_file": "x.py",
                    "source_line": 1,
                    "bogus_field": "x",
                }
            )

    @covers("REQ-0.0.64-02-02")
    def test_get_registry_returns_copy(self):
        @advances("TASK-0.0.64-02-01-01")
        def my_task_fn():
            return "ok"

        registry = get_task_registry()
        registry.clear()
        # Original registry unaffected
        self.assertEqual(len(get_task_registry()), 1)

    @covers("REQ-0.0.64-02-02")
    def test_decorated_function_behavior_unchanged(self):
        @advances("TASK-0.0.64-02-01-01")
        def my_task_fn(x, y):
            return x + y

        self.assertEqual(my_task_fn(2, 3), 5)


class TestAdvancesMultipleDecorations(unittest.TestCase):
    """Multiple @advances decorations and interleaving with @covers."""

    def setUp(self):
        reset_task_registry()
        set_known_task_reqs(_TEST_TASK_REQS)

    def tearDown(self):
        reset_task_registry()

    @covers("REQ-0.0.64-02-02")
    def test_multiple_functions_register_separately(self):
        @advances("TASK-0.0.64-02-01-01")
        def fn_a():
            pass

        @advances("TASK-0.0.64-02-02-01")
        def fn_b():
            pass

        registry = get_task_registry()
        self.assertEqual(len(registry), 2)
        task_ids = {r.task_id for r in registry}
        self.assertEqual(task_ids, {"TASK-0.0.64-02-01-01", "TASK-0.0.64-02-02-01"})


_RULE = Path(__file__).resolve().parents[2] / ".gzkit" / "rules" / "task-discovery.md"
_COUNT_WORDS = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5}


def _rule_channel_rows(text: str) -> list[str]:
    """Return the first cell of each data row in the rule's channel table."""
    section = text.split("## The ", 1)[1].split("\n## ", 1)[0]
    rows = [line for line in section.splitlines() if line.startswith("| ")]
    return [row.split("|")[1].strip() for row in rows[1:]]


class TestAdvancesIsNotCountedAsAChannel(unittest.TestCase):
    """The rule counts only the channels that carry attribution (GHI #1318).

    `@advances` has no producer, so the rule may keep it as an optional
    annotation but never as one of the channels its invariant counts. The
    invariant's count and the channel table must agree, so neither can cite
    the annotation as a channel without the other changing too.
    """

    def test_channel_table_excludes_advances(self):
        text = _RULE.read_text(encoding="utf-8")
        channels = _rule_channel_rows(text)
        self.assertTrue(channels, "the rule's channel table has no rows")
        self.assertFalse(
            [name for name in channels if "@advances" in name],
            "the rule's channel table still counts @advances as a channel",
        )

    def test_invariant_count_matches_channel_table(self):
        text = _RULE.read_text(encoding="utf-8")
        match = re.search(r"at least one of (\w+) discovery channels", text)
        self.assertIsNotNone(match, "the rule's invariant names no channel count")
        assert match is not None
        self.assertEqual(_COUNT_WORDS.get(match.group(1)), len(_rule_channel_rows(text)))


if __name__ == "__main__":
    unittest.main()
