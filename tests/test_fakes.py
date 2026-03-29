"""Protocol conformance tests for tests/fakes/ in-memory implementations.

Verifies that each fake satisfies its corresponding Protocol contract via
actual method calls, including round-trip behavior and edge cases.
"""

import inspect
import unittest
from pathlib import Path

from gzkit.traceability import covers
from tests.fakes import (
    InMemoryConfigStore,
    InMemoryFileStore,
    InMemoryLedgerStore,
    InMemoryProcessRunner,
)
from tests.fakes.config import InMemoryConfigStore as _ConfigStoreDirect
from tests.fakes.filesystem import InMemoryFileStore as _FileStoreDirect
from tests.fakes.ledger import InMemoryLedgerStore as _LedgerStoreDirect
from tests.fakes.process import InMemoryProcessRunner as _ProcessRunnerDirect


class TestFakesPackageImports(unittest.TestCase):
    """Verify __init__.py re-exports all four fakes."""

    @covers("REQ-0.0.3-04-01")
    def test_import_in_memory_file_store(self) -> None:
        self.assertIs(InMemoryFileStore, _FileStoreDirect)

    @covers("REQ-0.0.3-04-02")
    def test_import_in_memory_process_runner(self) -> None:
        self.assertIs(InMemoryProcessRunner, _ProcessRunnerDirect)

    @covers("REQ-0.0.3-04-03")
    def test_import_in_memory_ledger_store(self) -> None:
        self.assertIs(InMemoryLedgerStore, _LedgerStoreDirect)

    @covers("REQ-0.0.3-04-04")
    def test_import_in_memory_config_store(self) -> None:
        self.assertIs(InMemoryConfigStore, _ConfigStoreDirect)


class TestProtocolMethodPresence(unittest.TestCase):
    """Verify each fake exposes all methods required by its Protocol."""

    FILE_STORE_METHODS = ["read_text", "write_text", "exists", "iterdir"]
    PROCESS_RUNNER_METHODS = ["run"]
    LEDGER_STORE_METHODS = ["append", "read_all"]
    CONFIG_STORE_METHODS = ["load", "save"]

    def _assert_methods(self, cls: type, methods: list[str]) -> None:
        for method in methods:
            with self.subTest(method=method):
                self.assertTrue(
                    callable(getattr(cls, method, None)),
                    f"{cls.__name__} must expose callable '{method}'",
                )

    @covers("REQ-0.0.3-04-08")
    def test_file_store_protocol_methods(self) -> None:
        self._assert_methods(InMemoryFileStore, self.FILE_STORE_METHODS)

    def test_process_runner_protocol_methods(self) -> None:
        self._assert_methods(InMemoryProcessRunner, self.PROCESS_RUNNER_METHODS)

    def test_ledger_store_protocol_methods(self) -> None:
        self._assert_methods(InMemoryLedgerStore, self.LEDGER_STORE_METHODS)

    def test_config_store_protocol_methods(self) -> None:
        self._assert_methods(InMemoryConfigStore, self.CONFIG_STORE_METHODS)


class TestProtocolSignatures(unittest.TestCase):
    """Verify method signatures match the Protocol definitions."""

    def _get_params(self, cls: type, method: str) -> list[str]:
        sig = inspect.signature(getattr(cls, method))
        return list(sig.parameters.keys())

    def test_file_store_read_text_params(self) -> None:
        params = self._get_params(InMemoryFileStore, "read_text")
        self.assertIn("path", params)

    def test_file_store_write_text_params(self) -> None:
        params = self._get_params(InMemoryFileStore, "write_text")
        self.assertIn("path", params)
        self.assertIn("content", params)

    def test_file_store_exists_params(self) -> None:
        params = self._get_params(InMemoryFileStore, "exists")
        self.assertIn("path", params)

    def test_file_store_iterdir_params(self) -> None:
        params = self._get_params(InMemoryFileStore, "iterdir")
        self.assertIn("path", params)

    def test_process_runner_run_params(self) -> None:
        params = self._get_params(InMemoryProcessRunner, "run")
        self.assertIn("cmd", params)
        self.assertIn("cwd", params)

    def test_ledger_store_append_params(self) -> None:
        params = self._get_params(InMemoryLedgerStore, "append")
        self.assertIn("event", params)

    def test_config_store_save_params(self) -> None:
        params = self._get_params(InMemoryConfigStore, "save")
        self.assertIn("data", params)


class TestInMemoryFileStore(unittest.TestCase):
    """Behavioral contract tests for InMemoryFileStore."""

    def setUp(self) -> None:
        self.store = InMemoryFileStore()
        self.path = Path("some/dir/file.txt")

    # --- round-trip ---

    @covers("REQ-0.0.3-04-06")
    def test_write_then_read_round_trip(self) -> None:
        self.store.write_text(self.path, "hello world")
        result = self.store.read_text(self.path)
        self.assertEqual(result, "hello world")

    def test_overwrite_updates_content(self) -> None:
        self.store.write_text(self.path, "first")
        self.store.write_text(self.path, "second")
        self.assertEqual(self.store.read_text(self.path), "second")

    # --- exists ---

    def test_exists_returns_false_for_missing_path(self) -> None:
        self.assertFalse(self.store.exists(Path("no/such/file.txt")))

    def test_exists_returns_true_after_write(self) -> None:
        self.store.write_text(self.path, "data")
        self.assertTrue(self.store.exists(self.path))

    def test_exists_returns_true_for_parent_directory(self) -> None:
        self.store.write_text(Path("dir/sub/file.txt"), "content")
        self.assertTrue(self.store.exists(Path("dir")))

    def test_exists_returns_true_for_nested_parent(self) -> None:
        self.store.write_text(Path("a/b/c/file.txt"), "x")
        self.assertTrue(self.store.exists(Path("a/b")))

    # --- missing key raises FileNotFoundError ---

    def test_read_text_raises_file_not_found_for_missing_path(self) -> None:
        with self.assertRaises(FileNotFoundError):
            self.store.read_text(Path("nonexistent.txt"))

    def test_read_text_error_message_contains_path(self) -> None:
        missing = Path("ghost/file.txt")
        with self.assertRaises(FileNotFoundError) as ctx:
            self.store.read_text(missing)
        self.assertIn(str(missing), str(ctx.exception))

    # --- iterdir ---

    def test_iterdir_empty_directory(self) -> None:
        result = self.store.iterdir(Path("empty"))
        self.assertEqual(result, [])

    def test_iterdir_lists_direct_children(self) -> None:
        self.store.write_text(Path("root/a.txt"), "a")
        self.store.write_text(Path("root/b.txt"), "b")
        result = self.store.iterdir(Path("root"))
        self.assertIn(Path("root/a.txt"), result)
        self.assertIn(Path("root/b.txt"), result)

    def test_iterdir_returns_sorted_results(self) -> None:
        self.store.write_text(Path("dir/z.txt"), "z")
        self.store.write_text(Path("dir/a.txt"), "a")
        self.store.write_text(Path("dir/m.txt"), "m")
        result = self.store.iterdir(Path("dir"))
        self.assertEqual(result, sorted(result))

    def test_iterdir_deduplicates_subdirectories(self) -> None:
        self.store.write_text(Path("root/sub/x.txt"), "x")
        self.store.write_text(Path("root/sub/y.txt"), "y")
        result = self.store.iterdir(Path("root"))
        sub_paths = [p for p in result if p == Path("root/sub")]
        self.assertEqual(len(sub_paths), 1)

    def test_iterdir_does_not_cross_directory_boundaries(self) -> None:
        self.store.write_text(Path("a/file.txt"), "in a")
        self.store.write_text(Path("b/file.txt"), "in b")
        result = self.store.iterdir(Path("a"))
        for p in result:
            self.assertTrue(p.as_posix().startswith("a/"))

    # --- initial data ---

    def test_initial_data_is_readable(self) -> None:
        store = InMemoryFileStore(initial={"seed/file.txt": "seed content"})
        self.assertEqual(store.read_text(Path("seed/file.txt")), "seed content")

    def test_initial_data_does_not_mutate_original_dict(self) -> None:
        source: dict[str, str] = {"k.txt": "v"}
        store = InMemoryFileStore(initial=source)
        store.write_text(Path("k.txt"), "changed")
        self.assertEqual(source["k.txt"], "v")

    # --- table-driven write/read ---

    def test_table_driven_write_read(self) -> None:
        cases: list[tuple[str, str, str]] = [
            ("file.txt", "simple content", "simple content"),
            ("dir/nested.txt", "nested", "nested"),
            ("unicode.txt", "caf\u00e9", "caf\u00e9"),
            ("empty.txt", "", ""),
        ]
        for path_str, content, expected in cases:
            with self.subTest(path=path_str):
                p = Path(path_str)
                self.store.write_text(p, content)
                self.assertEqual(self.store.read_text(p), expected)


class TestInMemoryProcessRunner(unittest.TestCase):
    """Behavioral contract tests for InMemoryProcessRunner."""

    def setUp(self) -> None:
        self.runner = InMemoryProcessRunner()

    # --- default response ---

    def test_default_response_is_zero_empty(self) -> None:
        code, out, err = self.runner.run(["any", "cmd"])
        self.assertEqual(code, 0)
        self.assertEqual(out, "")
        self.assertEqual(err, "")

    def test_custom_default_response(self) -> None:
        runner = InMemoryProcessRunner(default=(1, "default out", "default err"))
        code, out, err = runner.run(["unknown"])
        self.assertEqual(code, 1)
        self.assertEqual(out, "default out")
        self.assertEqual(err, "default err")

    # --- registered responses ---

    def test_registered_response_is_returned(self) -> None:
        self.runner.register(["git", "status"], (0, "On branch main", ""))
        code, out, err = self.runner.run(["git", "status"])
        self.assertEqual(code, 0)
        self.assertEqual(out, "On branch main")
        self.assertEqual(err, "")

    def test_unregistered_command_returns_default(self) -> None:
        self.runner.register(["git", "status"], (0, "branch info", ""))
        code, out, err = self.runner.run(["git", "diff"])
        self.assertEqual(code, 0)
        self.assertEqual(out, "")

    def test_registered_failure_response(self) -> None:
        self.runner.register(["make", "build"], (2, "", "build failed"))
        code, _out, err = self.runner.run(["make", "build"])
        self.assertEqual(code, 2)
        self.assertEqual(err, "build failed")

    # --- call recording ---

    def test_run_records_call(self) -> None:
        self.runner.run(["git", "log"])
        self.assertEqual(len(self.runner.calls), 1)
        cmd, cwd = self.runner.calls[0]
        self.assertEqual(cmd, ["git", "log"])
        self.assertIsNone(cwd)

    def test_run_records_cwd(self) -> None:
        cwd = Path("/some/dir")
        self.runner.run(["ls"], cwd=cwd)
        _, recorded_cwd = self.runner.calls[0]
        self.assertEqual(recorded_cwd, cwd)

    def test_multiple_calls_recorded_in_order(self) -> None:
        self.runner.run(["cmd1"])
        self.runner.run(["cmd2"])
        self.runner.run(["cmd3"])
        self.assertEqual(len(self.runner.calls), 3)
        self.assertEqual(self.runner.calls[0][0], ["cmd1"])
        self.assertEqual(self.runner.calls[1][0], ["cmd2"])
        self.assertEqual(self.runner.calls[2][0], ["cmd3"])

    def test_cmd_list_is_copied_in_calls(self) -> None:
        cmd: list[str] = ["git", "status"]
        self.runner.run(cmd)
        cmd.append("--short")
        self.assertEqual(self.runner.calls[0][0], ["git", "status"])

    # --- return type ---

    def test_run_returns_three_tuple(self) -> None:
        result = self.runner.run(["echo", "hi"])
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 3)

    # --- table-driven ---

    def test_table_driven_registered_responses(self) -> None:
        runner = InMemoryProcessRunner(default=(127, "", "not found"))
        cases: list[tuple[list[str], tuple[int, str, str]]] = [
            (["git", "status"], (0, "clean", "")),
            (["git", "push"], (1, "", "rejected")),
            (["uv", "run", "test"], (0, "all passed", "")),
        ]
        for cmd, response in cases:
            runner.register(cmd, response)
        for cmd, expected in cases:
            with self.subTest(cmd=cmd):
                result = runner.run(cmd)
                self.assertEqual(result, expected)


class TestInMemoryLedgerStore(unittest.TestCase):
    """Behavioral contract tests for InMemoryLedgerStore."""

    def setUp(self) -> None:
        self.store = InMemoryLedgerStore()

    # --- initial state ---

    def test_read_all_empty_initially(self) -> None:
        self.assertEqual(self.store.read_all(), [])

    # --- round-trip ---

    def test_append_then_read_all_round_trip(self) -> None:
        event = {"type": "gate_pass", "adr": "ADR-0.1.0"}
        self.store.append(event)
        results = self.store.read_all()
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0], event)

    def test_multiple_appends_preserve_order(self) -> None:
        events = [
            {"seq": 1, "msg": "first"},
            {"seq": 2, "msg": "second"},
            {"seq": 3, "msg": "third"},
        ]
        for e in events:
            self.store.append(e)
        results = self.store.read_all()
        self.assertEqual(results, events)

    # --- isolation ---

    def test_append_copies_event(self) -> None:
        original: dict = {"key": "value"}
        self.store.append(original)
        original["key"] = "mutated"
        stored = self.store.read_all()
        self.assertEqual(stored[0]["key"], "value")

    def test_read_all_returns_copies(self) -> None:
        self.store.append({"x": 1})
        first_read = self.store.read_all()
        first_read[0]["x"] = 999
        second_read = self.store.read_all()
        self.assertEqual(second_read[0]["x"], 1)

    # --- table-driven ---

    def test_table_driven_append_counts(self) -> None:
        cases: list[tuple[int, list[dict]]] = [
            (0, []),
            (1, [{"a": 1}]),
            (3, [{"a": 1}, {"b": 2}, {"c": 3}]),
        ]
        for expected_count, events in cases:
            with self.subTest(count=expected_count):
                store = InMemoryLedgerStore()
                for e in events:
                    store.append(e)
                self.assertEqual(len(store.read_all()), expected_count)


class TestInMemoryConfigStore(unittest.TestCase):
    """Behavioral contract tests for InMemoryConfigStore."""

    def setUp(self) -> None:
        self.store = InMemoryConfigStore()

    # --- initial state ---

    def test_load_returns_empty_dict_initially(self) -> None:
        self.assertEqual(self.store.load(), {})

    # --- round-trip ---

    def test_save_then_load_round_trip(self) -> None:
        data = {"key": "value", "count": 42}
        self.store.save(data)
        result = self.store.load()
        self.assertEqual(result, data)

    def test_save_overwrites_previous(self) -> None:
        self.store.save({"first": True})
        self.store.save({"second": True})
        result = self.store.load()
        self.assertNotIn("first", result)
        self.assertIn("second", result)

    # --- isolation ---

    def test_save_copies_data(self) -> None:
        data: dict = {"key": "original"}
        self.store.save(data)
        data["key"] = "mutated"
        self.assertEqual(self.store.load()["key"], "original")

    def test_load_returns_copy(self) -> None:
        self.store.save({"x": 1})
        first_load = self.store.load()
        first_load["x"] = 999
        self.assertEqual(self.store.load()["x"], 1)

    # --- initial data ---

    def test_initial_data_is_loaded(self) -> None:
        store = InMemoryConfigStore(initial={"env": "test"})
        self.assertEqual(store.load(), {"env": "test"})

    def test_initial_data_does_not_mutate_original(self) -> None:
        source: dict = {"k": "v"}
        store = InMemoryConfigStore(initial=source)
        store.save({"k": "changed"})
        self.assertEqual(source["k"], "v")

    # --- table-driven ---

    def test_table_driven_save_load(self) -> None:
        cases: list[dict] = [
            {},
            {"simple": "value"},
            {"nested": {"a": 1}},
            {"list_val": [1, 2, 3]},
        ]
        for data in cases:
            with self.subTest(data=data):
                store = InMemoryConfigStore()
                store.save(data)
                self.assertEqual(store.load(), data)


class TestFakesDeterminism(unittest.TestCase):
    """Verify fakes are deterministic — no randomness, no I/O dependency."""

    def test_file_store_same_result_for_same_input(self) -> None:
        for _ in range(3):
            store = InMemoryFileStore()
            store.write_text(Path("f.txt"), "consistent")
            self.assertEqual(store.read_text(Path("f.txt")), "consistent")

    def test_process_runner_same_response_each_call(self) -> None:
        runner = InMemoryProcessRunner()
        runner.register(["cmd"], (0, "output", ""))
        results = [runner.run(["cmd"]) for _ in range(3)]
        self.assertTrue(all(r == results[0] for r in results))

    def test_ledger_store_same_content_after_same_appends(self) -> None:
        events = [{"i": i} for i in range(5)]
        store = InMemoryLedgerStore()
        for e in events:
            store.append(e)
        self.assertEqual(store.read_all(), events)

    def test_config_store_same_content_after_same_save(self) -> None:
        data = {"stable": True, "version": "1.0"}
        store = InMemoryConfigStore()
        store.save(data)
        self.assertEqual(store.load(), data)
        self.assertEqual(store.load(), data)


if __name__ == "__main__":
    unittest.main()
