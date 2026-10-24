"""Ruff ALL under a counted shrink-ratchet baseline (RO-9 tranche 4).

`docs/governance/harbor-ro9-astral-toolchain.md` § Ruled for tranche 4: the
findings the tree carried when the selection widened are held per (file, rule)
with a count, and the verdict is exact. A new finding fails, a row above its
findings must be lowered, and a row whose findings are gone must be removed.
"""

import json
import tempfile
import unittest
from pathlib import Path
from typing import TYPE_CHECKING
from unittest import mock

from gzkit import ruff_baseline
from gzkit.ruff_baseline import (
    BaselineError,
    RuffFinding,
    RuffRunError,
    compare,
    lint_against_baseline,
    load_baseline,
    parse_ruff_json,
    ratchet_baseline,
    render_report,
    run_ruff_json,
)

if TYPE_CHECKING:
    from collections.abc import Sequence


def _item(root: Path, file: str, code: str | None, row: int = 1) -> dict[str, object]:
    return {
        "filename": str(root / file),
        "code": code,
        "location": {"row": row, "column": 1},
        "message": f"{code} here",
    }


class _FakeRuff:
    """Stands in for Ruff: returns a fixed report and records how it was called."""

    def __init__(self, items: list[dict[str, object]]) -> None:
        self.items = items
        self.calls: list[tuple[list[str], bool]] = []

    def __call__(self, _root: Path, targets: Sequence[str], *, fix: bool) -> str:
        self.calls.append((list(targets), fix))
        return json.dumps(self.items)


class _Tree:
    def __init__(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name).resolve()
        (self.root / "data").mkdir()

    def baseline(self, rows: list[dict[str, object]]) -> None:
        payload = {"_doc": "test baseline", "rows": rows}
        (self.root / "data" / "ruff_baseline.json").write_text(json.dumps(payload), "utf-8")

    def rows(self) -> list[dict[str, object]]:
        text = (self.root / "data" / "ruff_baseline.json").read_text("utf-8")
        return json.loads(text)["rows"]

    def close(self) -> None:
        self._tmp.cleanup()


class CompareTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tree = _Tree()
        self.addCleanup(self.tree.close)
        self.root = self.tree.root

    def _findings(self, *specs: tuple[str, str | None]) -> list[RuffFinding]:
        items = [_item(self.root, file, code, row) for row, (file, code) in enumerate(specs, 1)]
        return parse_ruff_json(json.dumps(items), self.root)

    def test_findings_at_their_rows_pass(self) -> None:
        findings = self._findings(("a.py", "T201"), ("a.py", "T201"))
        self.assertEqual(compare(findings, {("a.py", "T201"): 2}), [])

    def test_a_finding_no_row_holds_is_unheld_and_carries_its_location(self) -> None:
        findings = self._findings(("a.py", "T201"))
        [breach] = compare(findings, {})
        self.assertEqual((breach.kind, breach.file, breach.rule), ("unheld", "a.py", "T201"))
        self.assertEqual((breach.found, breach.held), (1, 0))
        self.assertEqual([(f.file, f.line) for f in breach.findings], [("a.py", 1)])

    def test_one_more_finding_than_the_row_holds_is_unheld(self) -> None:
        findings = self._findings(("a.py", "T201"), ("a.py", "T201"))
        [breach] = compare(findings, {("a.py", "T201"): 1})
        self.assertEqual((breach.kind, breach.found, breach.held), ("unheld", 2, 1))

    def test_a_row_above_its_findings_must_be_lowered(self) -> None:
        findings = self._findings(("a.py", "T201"))
        [breach] = compare(findings, {("a.py", "T201"): 3})
        self.assertEqual((breach.kind, breach.found, breach.held), ("lower", 1, 3))

    def test_a_row_whose_findings_are_gone_is_dead(self) -> None:
        [breach] = compare([], {("a.py", "T201"): 1})
        self.assertEqual((breach.kind, breach.file, breach.rule), ("dead", "a.py", "T201"))

    def test_a_partial_run_judges_only_the_rows_of_the_files_it_read(self) -> None:
        baseline = {("a.py", "T201"): 1, ("pkg/b.py", "T201"): 1, ("c.py", "T201"): 1}
        breaches = compare([], baseline, scope=["a.py", "pkg"])
        self.assertEqual(sorted(b.file for b in breaches), ["a.py", "pkg/b.py"])

    def test_a_syntax_error_has_a_rule_no_row_can_be_seeded_for_by_accident(self) -> None:
        [finding] = self._findings(("a.py", None))
        self.assertEqual(finding.rule, "invalid-syntax")


class LintAgainstBaselineTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tree = _Tree()
        self.addCleanup(self.tree.close)
        self.root = self.tree.root

    def test_a_tree_with_no_baseline_fails_every_finding_as_plain_ruff_does(self) -> None:
        ruff = _FakeRuff([_item(self.root, "a.py", "F401")])
        report = lint_against_baseline(self.root, runner=ruff)
        self.assertFalse(report.has_baseline)
        self.assertFalse(report.ok)
        self.assertEqual([b.kind for b in report.breaches], ["unheld"])

    def test_a_tree_with_no_baseline_and_no_findings_passes(self) -> None:
        self.assertTrue(lint_against_baseline(self.root, runner=_FakeRuff([])).ok)

    def test_held_findings_pass_and_the_whole_tree_is_the_default_target(self) -> None:
        self.tree.baseline([{"file": "a.py", "rule": "F401", "count": 1}])
        ruff = _FakeRuff([_item(self.root, "a.py", "F401")])
        report = lint_against_baseline(self.root, runner=ruff)
        self.assertTrue(report.ok)
        self.assertEqual(ruff.calls, [(["."], False)])

    def test_fix_is_passed_through_to_ruff(self) -> None:
        ruff = _FakeRuff([])
        lint_against_baseline(self.root, ["a.py"], fix=True, runner=ruff)
        self.assertEqual(ruff.calls, [(["a.py"], True)])

    def test_named_files_leave_other_files_rows_unjudged(self) -> None:
        self.tree.baseline([{"file": "other.py", "rule": "F401", "count": 1}])
        self.assertTrue(lint_against_baseline(self.root, ["a.py"], runner=_FakeRuff([])).ok)

    def test_the_whole_tree_judges_every_row(self) -> None:
        self.tree.baseline([{"file": "other.py", "rule": "F401", "count": 1}])
        report = lint_against_baseline(self.root, ["."], runner=_FakeRuff([]))
        self.assertEqual([b.kind for b in report.breaches], ["dead"])


class BaselineFileTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tree = _Tree()
        self.addCleanup(self.tree.close)

    def test_no_file_is_no_baseline(self) -> None:
        self.assertIsNone(load_baseline(self.tree.root))

    def test_a_row_held_twice_is_a_defect(self) -> None:
        row = {"file": "a.py", "rule": "F401", "count": 1}
        self.tree.baseline([row, row])
        with self.assertRaises(BaselineError):
            load_baseline(self.tree.root)

    def test_a_row_at_zero_is_a_defect(self) -> None:
        self.tree.baseline([{"file": "a.py", "rule": "F401", "count": 0}])
        with self.assertRaises(BaselineError):
            load_baseline(self.tree.root)

    def test_a_baseline_without_rows_is_malformed(self) -> None:
        (self.tree.root / "data" / "ruff_baseline.json").write_text("{}", "utf-8")
        with self.assertRaises(BaselineError):
            load_baseline(self.tree.root)


class RatchetTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tree = _Tree()
        self.addCleanup(self.tree.close)
        self.root = self.tree.root

    def test_ratchet_lowers_rows_and_drops_the_dead_one(self) -> None:
        self.tree.baseline(
            [
                {"file": "a.py", "rule": "F401", "count": 3},
                {"file": "b.py", "rule": "T201", "count": 1},
            ]
        )
        ruff = _FakeRuff([_item(self.root, "a.py", "F401")])
        removed = ratchet_baseline(self.root, runner=ruff)
        self.assertEqual(removed, 1)
        self.assertEqual(self.tree.rows(), [{"file": "a.py", "rule": "F401", "count": 1}])

    def test_ratchet_never_raises_a_row_or_adds_one(self) -> None:
        self.tree.baseline([{"file": "a.py", "rule": "F401", "count": 1}])
        ruff = _FakeRuff(
            [
                _item(self.root, "a.py", "F401"),
                _item(self.root, "a.py", "F401", 2),
                _item(self.root, "new.py", "T201"),
            ]
        )
        ratchet_baseline(self.root, runner=ruff)
        self.assertEqual(self.tree.rows(), [{"file": "a.py", "rule": "F401", "count": 1}])
        self.assertFalse(lint_against_baseline(self.root, runner=ruff).ok)

    def test_ratchet_without_a_baseline_is_refused(self) -> None:
        with self.assertRaises(BaselineError):
            ratchet_baseline(self.root, runner=_FakeRuff([]))


class RuffReportTest(unittest.TestCase):
    def test_a_report_that_is_not_json_is_a_run_error(self) -> None:
        with self.assertRaises(RuffRunError):
            parse_ruff_json("error: bad config", Path.cwd())

    def test_a_report_that_is_not_a_list_is_a_run_error(self) -> None:
        with self.assertRaisesRegex(RuffRunError, "not a list of diagnostics"):
            parse_ruff_json('{"code": "F401"}', Path.cwd())

    def test_a_diagnostic_without_a_filename_is_a_run_error(self) -> None:
        with self.assertRaises(RuffRunError):
            parse_ruff_json('[{"code": "F401"}]', Path.cwd())

    def test_a_diagnostic_whose_location_is_not_an_object_reads_as_line_0(self) -> None:
        [finding] = parse_ruff_json(
            '[{"code": "F401", "filename": "a.py", "location": 3}]', Path.cwd()
        )
        self.assertEqual((finding.rule, finding.line, finding.column), ("F401", 0, 0))


class RunRuffJsonTest(unittest.TestCase):
    """The one runner: Ruff's JSON report, or a run error when Ruff itself fails."""

    def _run(self, *, returncode: int = 0, fix: bool = False, error: Exception | None = None):
        done = mock.Mock(returncode=returncode, stdout="[]", stderr="bad config")
        with mock.patch.object(
            ruff_baseline.subprocess, "run", return_value=done, side_effect=error
        ) as run:
            return run_ruff_json(Path("/repo"), ["a.py"], fix=fix), run

    def test_findings_exit_zero_so_the_report_is_returned(self) -> None:
        stdout, run = self._run()
        self.assertEqual(stdout, "[]")
        argv = run.call_args.args[0]
        self.assertEqual(argv[:4], ["uv", "run", "ruff", "check"])
        self.assertIn("--exit-zero", argv)
        self.assertEqual(argv[-1], "a.py")
        self.assertNotIn("--fix", argv)
        self.assertEqual(run.call_args.kwargs["cwd"], Path("/repo"))

    def test_fix_asks_ruff_for_its_safe_fixes(self) -> None:
        _, run = self._run(fix=True)
        self.assertIn("--fix", run.call_args.args[0])

    def test_ruff_failing_before_it_reports_is_a_run_error_naming_its_output(self) -> None:
        with self.assertRaises(RuffRunError) as caught:
            self._run(returncode=2)
        self.assertIn("bad config", str(caught.exception))

    def test_ruff_that_cannot_start_is_a_run_error(self) -> None:
        with self.assertRaises(RuffRunError):
            self._run(error=FileNotFoundError("uv"))


class RuffRuleCodesTest(unittest.TestCase):
    """Rule names (RUF201's form) translate to codes through Ruff's own table."""

    def setUp(self) -> None:
        ruff_baseline.ruff_rule_codes.cache_clear()
        self.addCleanup(ruff_baseline.ruff_rule_codes.cache_clear)

    def test_the_installed_ruff_maps_a_name_to_its_code(self) -> None:
        codes = ruff_baseline.ruff_rule_codes()
        self.assertEqual(codes["blind-except"], "BLE001")
        self.assertEqual(codes["line-too-long"], "E501")

    def test_ruff_failing_or_printing_no_table_is_a_run_error(self) -> None:
        for done in (
            mock.Mock(returncode=2, stdout="", stderr="no ruff"),
            mock.Mock(returncode=0, stdout="not json", stderr=""),
        ):
            with (
                self.subTest(done=done),
                mock.patch.object(ruff_baseline.subprocess, "run", return_value=done),
                self.assertRaises(RuffRunError),
            ):
                ruff_baseline.ruff_rule_codes()


class RenderReportRendering(unittest.TestCase):
    # output-contract: the recovery prose is the named contract of a fail-closed
    # surface (.gzkit/rules/guardrail-feedback-prose.md).
    def setUp(self) -> None:
        self.tree = _Tree()
        self.addCleanup(self.tree.close)
        self.root = self.tree.root

    def test_each_kind_names_the_finding_the_rule_and_a_runnable_next_step(self) -> None:
        self.tree.baseline(
            [
                {"file": "low.py", "rule": "F401", "count": 2},
                {"file": "gone.py", "rule": "F401", "count": 1},
            ]
        )
        ruff = _FakeRuff(
            [_item(self.root, "new.py", "T201", 7), _item(self.root, "low.py", "F401")]
        )
        text = render_report(lint_against_baseline(self.root, runner=ruff))
        self.assertIn("new.py:7:1 T201", text)
        self.assertIn("harbor-ro9-astral-toolchain.md", text)
        self.assertIn("then re-run `uv run gz lint`", text)
        self.assertEqual(text.count("uv run gz lint --ratchet"), 2)

    def test_a_kind_with_no_breach_renders_no_block(self) -> None:
        ruff = _FakeRuff([_item(self.root, "new.py", "T201")])
        text = render_report(lint_against_baseline(self.root, runner=ruff))
        self.assertNotIn("--ratchet", text)

    def test_a_long_report_is_cut_and_names_the_rerun(self) -> None:
        ruff = _FakeRuff([_item(self.root, "new.py", "T201", row) for row in range(1, 6)])
        text = render_report(lint_against_baseline(self.root, runner=ruff), max_lines=3)
        self.assertNotIn("new.py:4:1", text)
        self.assertIn("... 3 more lines; re-run `uv run gz lint`", text)


if __name__ == "__main__":
    unittest.main()
