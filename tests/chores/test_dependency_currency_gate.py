"""The dependency-currency chore's currency and scan-record gates (GHI #1369).

The chore's original criteria witnessed an intact toolchain and never a current
one, so a bare run passed on a lagging tree and its PASS block moved the band.
These tests drive the gate's pure functions with synthetic text and fake
upstream readers; nothing here touches the network.
"""

import contextlib
import importlib.util
import io
import json
import subprocess
import sys
import tempfile
import unittest
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import TYPE_CHECKING, ClassVar
from unittest import mock

from gzkit.commands.common import get_project_root

if TYPE_CHECKING:
    from types import ModuleType

# The canonical authored copy; `gz agent sync control-surfaces` mirrors it to
# `src/gzkit/chores/`, and `gz validate --distribution` fails on drift.
_SCRIPT = get_project_root() / ".gzkit" / "chores" / "dependency-currency" / "check_currency.py"


def _load_gate() -> ModuleType:
    """Import the chore script by path; its directory name is not an identifier."""
    spec = importlib.util.spec_from_file_location("_dependency_currency_gate", _SCRIPT)
    if spec is None or spec.loader is None:
        msg = f"cannot load {_SCRIPT}"
        raise unittest.SkipTest(msg)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


GATE = _load_gate()

UV_TREE = """py-gzkit v0.34.9
├── cohesion v1.2.0
├── rich v15.0.0 (latest: v15.1.0)
├── ty v0.0.109 (group: dev) (latest: v0.0.111)
└── mkdocs v1.6.1 (group: docs)
"""

PYPROJECT = """[project]
dependencies = [
    "rich>=15.0",
]
[dependency-groups]
dev = [
    # Tracks ty forward, never pinned backward (GHI #789).
    "ty>=0.0.109",
]
"""

HOOKS = """repos:
  - repo: local
    hooks:
      - id: lint
  - repo: https://github.com/astral-sh/uv-pre-commit
    rev: 0.13.9
  - repo: https://github.com/pre-commit/pre-commit-hooks
    # held: GHI #42, v6.0.0 cannot be installed on Windows
    rev: v5.0.0
"""

WORKFLOW = """jobs:
  build:
    steps:
      - uses: actions/checkout@v6
      - uses: ./.github/actions/local
      - name: Install uv
        uses: astral-sh/setup-uv@1c37ad07a6a961277cf70c0d37d6f313000f5884 # v10.3.0
      - uses: owner/tool@0123456789abcdef0123456789abcdef01234567
"""


DOWNLOADS = json.dumps(
    [
        {"version": "3.16.0a2", "implementation": "cpython", "variant": "default"},
        {"version": "3.15.2", "implementation": "cpython", "variant": "default"},
        {"version": "3.14.11", "implementation": "cpython", "variant": "freethreaded"},
        {"version": "3.14.10", "implementation": "cpython", "variant": "default"},
        {"version": "3.14.9", "implementation": "cpython", "variant": "default"},
        {"version": "3.14.12", "implementation": "pypy", "variant": "default"},
    ]
)

BUILD = """[build-system]
requires = ["uv_build>=0.13.1,<0.14"]

[tool.uv]
# held: GHI #77, 0.14 cannot resolve on the floor
required-version = ">=0.13.1"
build-constraint-dependencies = ["setuptools==84.2.1"]
"""


def _pin(**fields: object) -> object:
    base = {"surface": "python", "name": "pkg", "current": "1.0.0", "location": "x:1"}
    return GATE.Pin(**(base | fields))


class TestBehindComparesVersionsNotStrings(unittest.TestCase):
    def test_a_lower_release_is_behind(self) -> None:
        self.assertTrue(GATE.is_behind("0.0.109", "v0.0.111"))
        self.assertTrue(GATE.is_behind("v5.0.0", "v6.0.0"))
        self.assertTrue(GATE.is_behind("0.9.0", "0.10.0"))

    def test_the_latest_release_is_not_behind(self) -> None:
        self.assertFalse(GATE.is_behind("v8.30.1", "v8.30.1"))
        self.assertFalse(GATE.is_behind("0.10.0", "0.9.0"))

    def test_a_major_tag_is_behind_only_when_the_major_moved(self) -> None:
        self.assertFalse(GATE.is_behind("v7", "v7.0.1"))
        self.assertTrue(GATE.is_behind("v6", "v7.0.1"))


class TestPinsAreReadFromEverySurface(unittest.TestCase):
    def test_python_pins_are_the_outdated_rows_of_uv_tree(self) -> None:
        pins = GATE.python_pins(UV_TREE, PYPROJECT)
        self.assertEqual(
            [(p.name, p.current, p.latest) for p in pins],
            [("rich", "15.0.0", "15.1.0"), ("ty", "0.0.109", "0.0.111")],
        )
        self.assertEqual([p.location for p in pins], ["pyproject.toml:3", "pyproject.toml:8"])

    def test_a_rationale_comment_citing_a_ghi_is_not_a_hold(self) -> None:
        ty = GATE.python_pins(UV_TREE, PYPROJECT)[1]
        self.assertIsNone(ty.hold_ghi)

    def test_hook_revs_skip_local_repos_and_read_held_markers(self) -> None:
        pins = GATE.hook_pins(HOOKS)
        self.assertEqual(
            [(p.name, p.current, p.hold_ghi) for p in pins],
            [
                ("astral-sh/uv-pre-commit", "0.13.9", None),
                ("pre-commit/pre-commit-hooks", "v5.0.0", 42),
            ],
        )

    def test_action_pins_read_tags_and_sha_comments(self) -> None:
        pins = GATE.action_pins(WORKFLOW, ".github/workflows/ci.yml")
        self.assertEqual(
            [(p.name, p.current) for p in pins],
            [("actions/checkout", "v6"), ("astral-sh/setup-uv", "v10.3.0"), ("owner/tool", None)],
        )


class TestJudgeRefusesWhatIsBehindAndUnheld(unittest.TestCase):
    def _judge(self, pin: object, latest: str = "2.0.0", open_issues: frozenset[int] = frozenset()):
        return GATE.judge([pin], lambda _pin: latest, lambda number: number in open_issues)

    def test_a_current_pin_passes(self) -> None:
        self.assertEqual(self._judge(_pin(current="2.0.0")), [])

    def test_a_behind_pin_with_no_hold_is_refused(self) -> None:
        findings = self._judge(_pin())
        self.assertEqual([f.reason for f in findings], ["behind upstream, no hold"])

    def test_a_behind_pin_held_by_an_open_ghi_passes(self) -> None:
        self.assertEqual(self._judge(_pin(hold_ghi=7), open_issues=frozenset({7})), [])

    def test_a_hold_whose_ghi_closed_is_refused(self) -> None:
        findings = self._judge(_pin(hold_ghi=7))
        self.assertEqual([f.reason for f in findings], ["held by GHI #7, which is closed"])

    def test_a_pin_naming_no_version_is_refused(self) -> None:
        findings = self._judge(_pin(surface="action", current=None))
        self.assertEqual([f.reason for f in findings], ["pin names no version"])

    def test_a_known_latest_is_not_fetched_again(self) -> None:
        def refuse(_pin: object) -> str:
            msg = "upstream was queried for a pin that carried its latest"
            raise AssertionError(msg)

        findings = GATE.judge([_pin(latest="1.0.0")], refuse, lambda _n: False)
        self.assertEqual(findings, [])

    def test_an_unreachable_upstream_raises_rather_than_passing(self) -> None:
        def unreachable(_pin: object) -> str:
            msg = "offline"
            raise GATE.UpstreamUnavailableError(msg)

        with self.assertRaises(GATE.UpstreamUnavailableError):
            GATE.judge([_pin()], unreachable, lambda _n: True)


class TestScanRecordMustBeWithinItsPeriod(unittest.TestCase):
    NOW = datetime(2026, 11, 25, 12, tzinfo=UTC)

    def test_no_record_is_a_breach(self) -> None:
        self.assertIsNotNone(GATE.scan_breach(None, self.NOW, 1))

    def test_a_record_older_than_the_period_is_a_breach(self) -> None:
        self.assertIsNotNone(GATE.scan_breach(self.NOW - timedelta(days=3), self.NOW, 1))

    def test_a_record_within_the_period_passes(self) -> None:
        self.assertIsNone(GATE.scan_breach(self.NOW - timedelta(hours=20), self.NOW, 1))


class TestHoldMarkersAreReadWhereTheyAreWritten(unittest.TestCase):
    def test_a_hold_on_the_pinning_line_is_read(self) -> None:
        self.assertEqual(GATE.hold_ghi(['"pkg==1.0",  # held: GHI #9, yanked'], 0), 9)

    def test_a_hold_further_up_its_comment_block_is_read(self) -> None:
        lines = ["# held: GHI #11, 2.0 cannot resolve", "# on Windows runners", '"pkg==1.0",']
        self.assertEqual(GATE.hold_ghi(lines, 2), 11)

    def test_a_hold_beyond_the_comment_block_is_not_this_pins(self) -> None:
        lines = ["# held: GHI #11", '"other==1.0",', '"pkg==1.0",']
        self.assertIsNone(GATE.hold_ghi(lines, 2))

    def test_an_undeclared_outdated_package_is_located_in_the_lock(self) -> None:
        pins = GATE.python_pins("├── idna v3.9 (latest: v3.10)\n", PYPROJECT)
        self.assertEqual(
            [(p.name, p.location, p.hold_ghi) for p in pins], [("idna", "uv.lock", None)]
        )


class _FakeUpstream:
    """Canned answers per argv prefix, recording every call."""

    def __init__(self, answers: dict[tuple[str, ...], str]) -> None:
        self.answers = answers
        self.calls: list[list[str]] = []

    def __call__(self, argv: list[str]) -> str:
        self.calls.append(argv)
        for prefix, answer in self.answers.items():
            if tuple(argv[: len(prefix)]) == prefix:
                return answer
        msg = f"no canned answer for {argv}"
        raise GATE.UpstreamUnavailableError(msg)


def _tree(root: Path, *, behind: bool) -> None:
    (root / "pyproject.toml").write_text(PYPROJECT, encoding="utf-8")
    (root / ".python-version").write_text("3.14.10\n", encoding="utf-8")
    (root / ".pre-commit-config.yaml").write_text(
        "repos:\n  - repo: https://github.com/gitleaks/gitleaks\n    rev: v8.30.1\n",
        encoding="utf-8",
    )
    workflows = root / ".github" / "workflows"
    workflows.mkdir(parents=True)
    checkout = "v6" if behind else "v7"
    (workflows / "ci.yml").write_text(
        f"      - uses: actions/checkout@{checkout}\n", encoding="utf-8"
    )


def _upstream(*, uv_tree: str = "py-gzkit v1.0.0\n") -> _FakeUpstream:
    return _FakeUpstream(
        {
            ("uv", "tree"): uv_tree,
            ("uv", "self"): "0.13.10\n",
            ("uv", "python", "list"): DOWNLOADS,
            ("gh", "api", "repos/astral-sh/uv/releases/latest"): "0.13.10\n",
            ("gh", "api", "repos/gitleaks/gitleaks/releases/latest"): "v8.30.1\n",
            ("gh", "api", "repos/actions/checkout/releases/latest"): "v7.0.1\n",
        }
    )


class TestCurrencyGateReadsEverySurface(unittest.TestCase):
    def test_collect_pins_reads_python_uv_hooks_and_actions(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _tree(root, behind=True)
            pins = GATE.collect_pins(root, _upstream(uv_tree=UV_TREE))
        self.assertEqual(
            sorted({p.surface for p in pins}), ["action", "hook", "python", "python-version", "uv"]
        )
        self.assertIn(("uv", "0.13.10"), [(p.name, p.current) for p in pins])
        self.assertIn(".github/workflows/ci.yml:1", [p.location for p in pins])

    def test_a_current_tree_exits_zero(self) -> None:
        with tempfile.TemporaryDirectory() as tmp, contextlib.redirect_stdout(io.StringIO()):
            root = Path(tmp)
            _tree(root, behind=False)
            self.assertEqual(GATE.check_currency(root, _upstream()), 0)

    def test_a_lagging_tree_exits_three_with_recovery_prose(self) -> None:
        err = io.StringIO()
        with tempfile.TemporaryDirectory() as tmp, contextlib.redirect_stderr(err):
            root = Path(tmp)
            _tree(root, behind=True)
            code = GATE.check_currency(root, _upstream())
        self.assertEqual(code, 3)
        text = err.getvalue()
        self.assertIn(".github/workflows/ci.yml:1", text)  # what failed
        self.assertIn("Why:", text)
        self.assertIn("gz-deps-upgrade", text)  # the governed next step

    def test_an_unreachable_upstream_exits_two(self) -> None:
        with tempfile.TemporaryDirectory() as tmp, contextlib.redirect_stderr(io.StringIO()):
            root = Path(tmp)
            _tree(root, behind=False)
            self.assertEqual(GATE.check_currency(root, _FakeUpstream({})), 2)

    def test_each_repository_is_queried_once(self) -> None:
        upstream = _upstream()
        latest = GATE.github_latest(upstream)
        pin = _pin(surface="action", name="actions/checkout")
        latest(pin)
        latest(pin)
        self.assertEqual(sum(call[:2] == ["gh", "api"] for call in upstream.calls), 1)

    def test_the_uv_binary_is_compared_with_uvs_own_releases(self) -> None:
        latest = GATE.github_latest(_upstream())
        self.assertEqual(latest(_pin(surface="uv", name="uv")), "0.13.10")

    def test_issue_state_is_read_from_github(self) -> None:
        is_open = GATE.issue_is_open(_FakeUpstream({("gh", "issue", "view", "5"): "OPEN\n"}))
        is_closed = GATE.issue_is_open(_FakeUpstream({("gh", "issue", "view", "5"): "CLOSED\n"}))
        self.assertTrue(is_open(5))
        self.assertFalse(is_closed(5))


class TestTheRunnerNeverPassesAFailure(unittest.TestCase):
    def test_a_command_that_succeeds_returns_its_output(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = GATE.subprocess_runner(Path(tmp))(["uv", "--version"])
        self.assertTrue(out.startswith("uv "))

    def test_a_command_that_fails_raises(self) -> None:
        with tempfile.TemporaryDirectory() as tmp, self.assertRaises(GATE.UpstreamUnavailableError):
            GATE.subprocess_runner(Path(tmp))(["uv", "no-such-subcommand"])

    def test_a_missing_tool_raises(self) -> None:
        with tempfile.TemporaryDirectory() as tmp, self.assertRaises(GATE.UpstreamUnavailableError):
            GATE.subprocess_runner(Path(tmp))(["gz-no-such-tool-1369"])


def _registry(root: Path, staleness: dict[str, object] | None) -> None:
    chores = root / ".gzkit" / "chores"
    chores.mkdir(parents=True)
    entry: dict[str, object] = {"slug": "dependency-currency"}
    if staleness is not None:
        entry["staleness"] = staleness
    (chores / "registry.json").write_text(json.dumps({"chores": [entry]}), encoding="utf-8")


class TestScanRecordGateReadsTheDeclaration(unittest.TestCase):
    NOW = datetime(2026, 11, 25, 12, tzinfo=UTC)
    RECORD = ".gzkit/chores/dependency-currency/proofs/drift-report.md"
    DECLARED: ClassVar[dict[str, object]] = {
        "signal": "elapsed-time",
        "periodDays": 1,
        "artifacts": [RECORD],
    }

    def _gate(
        self, staleness: dict[str, object] | None, newest: datetime | None
    ) -> tuple[int, str]:
        err = io.StringIO()
        seen: list[tuple[str, ...]] = []

        def changed(artifacts: tuple[str, ...]) -> datetime | None:
            seen.append(artifacts)
            return newest

        with tempfile.TemporaryDirectory() as tmp, contextlib.redirect_stderr(err):
            root = Path(tmp)
            _registry(root, staleness)
            with contextlib.redirect_stdout(io.StringIO()):
                code = GATE.check_scan_record(root, self.NOW, changed)
        if staleness is not None and code != 1:
            self.assertEqual(seen, [(self.RECORD,)])  # the declared record, read as declared
        return code, err.getvalue()

    def test_a_fresh_record_passes(self) -> None:
        self.assertEqual(self._gate(self.DECLARED, self.NOW - timedelta(hours=3))[0], 0)

    def test_a_stale_record_is_a_breach_with_recovery_prose(self) -> None:
        code, text = self._gate(self.DECLARED, self.NOW - timedelta(days=4))
        self.assertEqual(code, 3)
        self.assertIn("4d ago", text)
        self.assertIn("Why:", text)
        self.assertIn("gz chores run dependency-currency", text)

    def test_an_undeclared_record_is_a_config_error(self) -> None:
        self.assertEqual(self._gate({"signal": "elapsed-time", "periodDays": 1}, None)[0], 1)
        self.assertEqual(self._gate(None, None)[0], 1)


class TestTheRegistryIsTheOnlyDeclaration(unittest.TestCase):
    NOW = datetime(2026, 11, 25, 12, tzinfo=UTC)

    def _exit(self, registry_text: str | None) -> int:
        with tempfile.TemporaryDirectory() as tmp, contextlib.redirect_stderr(io.StringIO()):
            root = Path(tmp)
            if registry_text is not None:
                (root / ".gzkit" / "chores").mkdir(parents=True)
                (root / ".gzkit" / "chores" / "registry.json").write_text(
                    registry_text, encoding="utf-8"
                )
            return GATE.check_scan_record(root, self.NOW, lambda _a: self.NOW)

    def test_a_missing_registry_is_a_config_error(self) -> None:
        self.assertEqual(self._exit(None), 1)

    def test_a_registry_without_the_chore_is_a_config_error(self) -> None:
        self.assertEqual(self._exit(json.dumps({"chores": [{"slug": "other"}]})), 1)


class TestTheCommandLineNamesOneGate(unittest.TestCase):
    def test_no_gate_named_is_a_usage_error(self) -> None:
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as raised:
            GATE.main([])
        self.assertEqual(raised.exception.code, 2)

    def test_each_flag_runs_its_gate(self) -> None:
        with (
            mock.patch.object(GATE, "check_scan_record", return_value=11) as scan,
            mock.patch.object(GATE, "check_currency", return_value=13) as currency,
        ):
            self.assertEqual(GATE.main(["--scan-record"]), 11)
            self.assertEqual(GATE.main(["--currency"]), 13)
        self.assertEqual(scan.call_count, 1)
        self.assertEqual(currency.call_count, 1)

    def test_the_script_runs_main_when_executed(self) -> None:
        completed = subprocess.run(  # noqa: S603 — this interpreter on the chore script
            [sys.executable, str(_SCRIPT)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
            timeout=60,
        )
        self.assertEqual(completed.returncode, 2)
        self.assertIn("--scan-record", completed.stderr)


class TestTheReviewsParsingCasesAreRead(unittest.TestCase):
    """Forms the #1369 review found the first parser missed or misread."""

    def test_a_dependency_with_extras_is_read(self) -> None:
        pins = GATE.python_pins("├── httpx[http2] v0.27.0 (latest: v0.28.1)\n", PYPROJECT)
        self.assertEqual(
            [(p.name, p.current, p.latest) for p in pins], [("httpx", "0.27.0", "0.28.1")]
        )

    def test_build_constraints_and_the_build_system_floor_are_read(self) -> None:
        pins = GATE.build_pins(BUILD)
        self.assertEqual(
            [(p.surface, p.name, p.current) for p in pins],
            [("build", "uv_build", "0.13.1"), ("build", "setuptools", "84.2.1")],
        )

    def test_the_uv_binary_is_held_on_its_required_version_line(self) -> None:
        self.assertEqual(GATE.uv_binary_pin(BUILD, "0.13.9").hold_ghi, 77)
        self.assertIsNone(GATE.uv_binary_pin(PYPROJECT, "0.13.9").hold_ghi)

    def test_python_version_compares_with_the_newest_stable_download_of_its_minor(self) -> None:
        pin = GATE.python_version_pin("3.14.10\n", DOWNLOADS)
        self.assertEqual((pin.current, pin.latest), ("3.14.10", "3.14.10"))
        behind = GATE.python_version_pin("3.14.9\n", DOWNLOADS)
        self.assertEqual(behind.latest, "3.14.10")

    def test_commented_uses_and_hook_lines_are_not_pins(self) -> None:
        workflow = "      # - uses: actions/checkout@v4\n      - uses: actions/checkout@v7\n"
        self.assertEqual([p.current for p in GATE.action_pins(workflow, "w.yml")], ["v7"])
        hooks = (
            "  # - repo: https://github.com/old/hooks\n  #   rev: v1.0.0\n"
            "  - repo: https://github.com/new/hooks\n    rev: v2.0.0\n"
        )
        self.assertEqual([p.name for p in GATE.hook_pins(hooks)], ["new/hooks"])

    def test_a_frozen_sha_hook_rev_reads_its_frozen_version(self) -> None:
        sha = "0123456789abcdef0123456789abcdef01234567"
        hooks = f"  - repo: https://github.com/a/b\n    rev: {sha}  # frozen: v3.1.0\n"
        hooks += f"  - repo: https://github.com/c/d\n    rev: {sha}\n"
        self.assertEqual([p.current for p in GATE.hook_pins(hooks)], ["v3.1.0", None])

    def test_an_upstream_tag_naming_no_version_is_a_finding_not_a_crash(self) -> None:
        findings = GATE.judge([_pin(current="v6")], lambda _pin: "nightly", lambda _n: True)
        self.assertEqual(
            [f.reason for f in findings], ["upstream latest 'nightly' names no version"]
        )

    def test_build_pins_are_compared_with_pypi_once_per_package(self) -> None:
        asked: list[str] = []

        def pypi(name: str) -> str:
            asked.append(name)
            return "84.3.0"

        latest = GATE.github_latest(_FakeUpstream({}), pypi)
        pin = _pin(surface="build", name="setuptools", current="84.2.1")
        self.assertEqual(latest(pin), "84.3.0")
        latest(pin)
        self.assertEqual(asked, ["setuptools"])

    def test_an_unreachable_pypi_raises_rather_than_passing(self) -> None:
        with (
            mock.patch.object(GATE.urllib.request, "urlopen", side_effect=OSError("offline")),
            self.assertRaises(GATE.UpstreamUnavailableError),
        ):
            GATE.pypi_latest("setuptools")


class TestTheGateReadsPyPIForBuildPins(unittest.TestCase):
    def test_pypi_latest_reads_the_info_version(self) -> None:
        body = io.BytesIO(json.dumps({"info": {"version": "84.3.0"}}).encode())
        with mock.patch.object(GATE.urllib.request, "urlopen", return_value=body) as opened:
            self.assertEqual(GATE.pypi_latest("setuptools"), "84.3.0")
        self.assertIn("pypi.org/pypi/setuptools/json", opened.call_args.args[0])

    def test_the_currency_gate_judges_build_pins_and_the_uv_binary(self) -> None:
        err = io.StringIO()
        with tempfile.TemporaryDirectory() as tmp, contextlib.redirect_stderr(err):
            root = Path(tmp)
            _tree(root, behind=False)
            (root / "pyproject.toml").write_text(PYPROJECT + BUILD, encoding="utf-8")
            upstream = _upstream()
            upstream.answers["uv", "self"] = "0.13.9\n"
            upstream.answers["gh", "issue", "view", "77"] = "CLOSED\n"
            code = GATE.check_currency(root, upstream, lambda _name: "99.0.0")
        self.assertEqual(code, 3)
        text = err.getvalue()
        self.assertIn("build uv_build 0.13.1 (latest 99.0.0)", text)
        self.assertIn("build setuptools 84.2.1 (latest 99.0.0)", text)
        self.assertIn("uv uv 0.13.9 (latest 0.13.10): held by GHI #77, which is closed", text)


if __name__ == "__main__":
    unittest.main()
