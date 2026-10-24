"""The unit-tier profiler reports per-module time in a form two runs can be joined on (GHI #1171).

GHI #1171 asks why the unit tier takes two to three times as long on
windows-latest as on ubuntu-latest. Its exit condition is a per-module duration
table from both runners on one commit. The profiler printed a top-30 table for a
human; these tests pin the machine-readable record a CI run uploads, so the two
platforms' runs can be joined module by module.
"""

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

_MODULE_PATH = Path(__file__).resolve().parents[2] / "scripts" / "profile_unittest_modules.py"
_spec = importlib.util.spec_from_file_location("profile_unittest_modules", _MODULE_PATH)
assert _spec and _spec.loader
profiler = importlib.util.module_from_spec(_spec)
sys.modules["profile_unittest_modules"] = profiler
_spec.loader.exec_module(profiler)


class TestModuleOfATestId(unittest.TestCase):
    def test_a_test_id_belongs_to_the_module_before_its_class_and_method(self) -> None:
        self.assertEqual(
            "tests.commands.test_init",
            profiler.module_of("tests.commands.test_init.TestInit.test_creates_ledger"),
        )

    def test_a_module_level_failure_id_is_its_own_module(self) -> None:
        """A module that fails to import reports an id with no class or method."""
        self.assertEqual("unittest.loader", profiler.module_of("unittest.loader"))


class TestAggregate(unittest.TestCase):
    _TIMINGS = [
        ("tests.a.test_x.C.test_1", 2.0),
        ("tests.a.test_x.C.test_2", 1.0),
        ("tests.b.test_y.D.test_1", 0.5),
    ]

    def test_each_module_carries_its_summed_time_and_test_count(self) -> None:
        rows = {r["module"]: r for r in profiler.aggregate(self._TIMINGS)}
        self.assertEqual({"tests.a.test_x", "tests.b.test_y"}, set(rows))
        self.assertAlmostEqual(3.0, rows["tests.a.test_x"]["seconds"])
        self.assertEqual(2, rows["tests.a.test_x"]["tests"])
        self.assertAlmostEqual(0.5, rows["tests.b.test_y"]["seconds"])
        self.assertEqual(1, rows["tests.b.test_y"]["tests"])

    def test_modules_are_ranked_slowest_first(self) -> None:
        modules = [r["module"] for r in profiler.aggregate(self._TIMINGS)]
        self.assertEqual(["tests.a.test_x", "tests.b.test_y"], modules)

    def test_no_time_is_lost_or_invented(self) -> None:
        total = sum(r["seconds"] for r in profiler.aggregate(self._TIMINGS))
        self.assertAlmostEqual(sum(dt for _, dt in self._TIMINGS), total)


def _fixture_cases() -> tuple[type[unittest.TestCase], type[unittest.TestCase]]:
    """Return a passing and a failing case, built here so discovery never runs them."""

    class Passes(unittest.TestCase):
        def test_one(self) -> None:
            self.assertTrue(True)

    class Fails(unittest.TestCase):
        def test_one(self) -> None:
            self.fail("deliberate")

    return Passes, Fails


class TestProfileWritesAJoinableRecord(unittest.TestCase):
    """The record a CI run uploads: every module, every count, the verdict."""

    def _profile(self, *cases: type[unittest.TestCase]) -> dict:
        loader = unittest.TestLoader()
        suite = unittest.TestSuite(loader.loadTestsFromTestCase(c) for c in cases)
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "profile.json"
            profiler.profile(suite, json_path=out, top=5, stream=None)
            return json.loads(out.read_text(encoding="utf-8"))

    def test_the_record_names_the_platform_and_counts_every_test(self) -> None:
        record = self._profile(*_fixture_cases())
        self.assertEqual(sys.platform, record["platform"])
        self.assertEqual(2, record["tests"])
        self.assertEqual(2, sum(m["tests"] for m in record["modules"]))

    def test_a_failing_test_is_counted_not_hidden(self) -> None:
        """A profile of a broken tree must say so; its timings describe a different run."""
        record = self._profile(*_fixture_cases())
        self.assertEqual(1, record["failures"])
        self.assertFalse(record["successful"])

    def test_a_passing_suite_is_successful(self) -> None:
        record = self._profile(_fixture_cases()[0])
        self.assertEqual(0, record["failures"])
        self.assertEqual(0, record["errors"])
        self.assertTrue(record["successful"])

    def test_the_slowest_tests_are_bounded_by_top(self) -> None:
        record = self._profile(*_fixture_cases())
        self.assertLessEqual(len(record["slowest_tests"]), 5)
        self.assertTrue(all({"id", "seconds"} <= set(t) for t in record["slowest_tests"]))


if __name__ == "__main__":
    unittest.main()
