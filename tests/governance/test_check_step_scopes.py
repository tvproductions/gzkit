"""`gz check` scope membership is declared in config, not hard-coded (GHI #950).

The roster of steps a scope drops lived as a module-level frozenset, which made
"what does the push gate actually run" a code question. These tests pin the
properties that make the declaration trustworthy: it is READ rather than
restated, its polarity is conservative (unknown scope drops nothing), a scope
narrower than the per-change gate can never record the fingerprint that gate
reuses, and the default scope is the per-change gate — `Behave` is heavy-lane
and CI scope, reached only through `--full` (GHI #1088). Since GHI #1191 the
per-change gate also drops the whole unit tier and runs the tests the change
touches in its place. Since GHI #1192 the declaration ships inside the gzkit
package, so a project that installs gzkit gets the same gate gzkit runs.
"""

import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import gzkit
from gzkit.commands.quality import (
    _build_check_steps,
    _check_step_scopes_file,
    _load_check_step_scopes,
    _scope_records_verified,
    _scope_skips,
    _select_check_steps,
)
from gzkit.traceability import covers
from tests.commands.common import subcommand_parser

_CONFIG = _check_step_scopes_file()


class TestScopeDeclarationIsRead(unittest.TestCase):
    """The runner reads the declaration; it does not restate it."""

    @covers("REQ-0.0.68-01-01")
    def test_the_change_scope_drops_exactly_what_the_config_declares(self) -> None:
        scopes = json.loads(_CONFIG.read_text(encoding="utf-8"))["scopes"]
        declared = set(scopes["change"]["skips"])
        self.assertEqual(
            _scope_skips("change"),
            declared,
            "the runner must read the declaration, not carry a second copy of it",
        )

    @covers("REQ-0.0.68-01-01")
    def test_the_change_sweep_is_the_full_one_minus_exactly_the_declared_skips(self) -> None:
        """The change this config exists to make, asserted on the step list itself.

        The count is derived from the declaration rather than written here: a
        hard-coded difference would have to be edited every time a scope entry
        changes, which is the second copy this file exists to remove.
        """
        full = [name for name, _ in _select_check_steps("full")]
        change = [name for name, _ in _select_check_steps("change")]
        declared = _scope_skips("change")

        self.assertEqual(
            set(full) - set(change), set(declared), "change drops exactly the declared steps"
        )
        self.assertEqual(
            set(change) - set(full),
            {"Test (changed)"},
            "the only step the gate adds is the changed-test run that stands in for Test",
        )
        for step in declared:
            self.assertIn(step, full, f"{step} must still run in the full sweep")
        self.assertIn("Lint", change)
        self.assertIn("Typecheck", change)
        self.assertIn("Smoke tier", change)


class TestScopePolarityIsConservative(unittest.TestCase):
    """An unreadable or unknown scope runs MORE, never less."""

    @covers("REQ-0.0.68-01-01")
    def test_an_undeclared_scope_drops_nothing(self) -> None:
        """Absence of policy must not be read as permission to skip.

        The inverse polarity — unknown scope means "skip everything not listed" —
        would turn a typo in a scope name into a silently empty gate.
        """
        self.assertEqual(_scope_skips("no-such-scope"), frozenset())
        self.assertEqual(
            len(_select_check_steps("full")),
            len(_build_check_steps()),
            "the full scope drops nothing",
        )


class TestOnlyScopesCoveringTheGateRecord(unittest.TestCase):
    """A scope narrower than the per-change gate must never satisfy its reuse cache.

    The pre-push gate runs the `change` scope, so a fingerprint may stand in for it
    only when the run that minted it dropped nothing the gate would have run. A
    scope whose skips exceed the gate's is a partial verification, and a partial
    verification that can satisfy a gate is the presence-check failure
    `AGENTS.md` names.
    """

    def test_every_recording_scope_covers_the_per_change_gate(self) -> None:
        gate_skips = _scope_skips("change")
        for name in _load_check_step_scopes():
            with self.subTest(scope=name):
                if _scope_records_verified(name):
                    self.assertLessEqual(
                        _scope_skips(name),
                        gate_skips,
                        f"scope {name!r} records a fingerprint yet drops "
                        f"{_scope_skips(name) - gate_skips}, which the per-change gate runs",
                    )

    def test_a_scope_declared_not_to_record_does_not(self) -> None:
        narrow = {"narrow": {"skips": ["Lint"], "records_verified": False}}
        with mock.patch("gzkit.commands.quality._load_check_step_scopes", return_value=narrow):
            self.assertFalse(_scope_records_verified("narrow"))

    def test_the_change_and_full_scopes_record(self) -> None:
        self.assertTrue(_scope_records_verified("change"))
        self.assertTrue(_scope_records_verified("full"))

    def test_an_unreadable_declaration_drops_nothing_and_still_records(self) -> None:
        """A declaration that cannot be read runs MORE, never less.

        A scope that drops nothing ran the full sweep, so it may record. It also
        keeps the whole unit tier: the changed-test run stands in only where
        `Test` is declared dropped.
        """
        with mock.patch("gzkit.commands.quality._load_check_step_scopes", return_value={}):
            self.assertEqual(_scope_skips("change"), frozenset())
            self.assertTrue(_scope_records_verified("change"))
            names = [name for name, _ in _select_check_steps("change")]
            self.assertIn("Test", names)
            self.assertNotIn("Test (changed)", names)

    def test_a_malformed_declaration_reads_as_no_declaration(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            broken = Path(tmp) / "check_step_scopes.json"
            broken.write_text("{ not json", encoding="utf-8")
            with mock.patch("gzkit.commands.quality._check_step_scopes_file", return_value=broken):
                self.assertEqual(_load_check_step_scopes(), {})


class TestEveryProjectGetsThePerChangeGate(unittest.TestCase):
    """The gate a project runs does not depend on files only gzkit's repository has.

    Operator ruling 2026-10-11 (GHI #1192), verbatim: "adopters get the light
    gate too". The declaration was read from the invoking project's `data/`,
    which no installed project has, so everywhere but here plain `gz check`
    ran the full sweep and `--full` changed nothing.
    """

    def _steps_in_a_project_without_gzkit_data(self, scope: str) -> list[str]:
        with (
            tempfile.TemporaryDirectory() as tmp,
            mock.patch("gzkit.commands.quality.get_project_root", return_value=Path(tmp)),
        ):
            return [name for name, _ in _select_check_steps(scope)]

    def test_a_project_with_no_data_directory_runs_the_per_change_gate(self) -> None:
        change = self._steps_in_a_project_without_gzkit_data("change")
        for heavy in ("Test", "Behave", "Docs build", "Preflight", "Guard canary sweep"):
            self.assertNotIn(heavy, change)
        self.assertIn("Test (changed)", change)
        self.assertIn("Lint", change)
        self.assertIn("Smoke tier", change)

    def test_full_is_a_larger_sweep_in_a_project_with_no_data_directory(self) -> None:
        change = self._steps_in_a_project_without_gzkit_data("change")
        full = self._steps_in_a_project_without_gzkit_data("full")
        self.assertGreater(len(full), len(change))
        self.assertIn("Test", full)
        self.assertIn("Behave", full)

    def test_that_project_selects_the_steps_this_repository_selects(self) -> None:
        for scope in ("change", "full"):
            with self.subTest(scope=scope):
                self.assertEqual(
                    self._steps_in_a_project_without_gzkit_data(scope),
                    [name for name, _ in _select_check_steps(scope)],
                )

    def test_the_declaration_is_a_file_of_the_installed_package(self) -> None:
        package_dir = Path(gzkit.__file__).resolve().parent
        self.assertEqual(_check_step_scopes_file().resolve().parent, package_dir)
        self.assertTrue(_check_step_scopes_file().is_file())


class TestTheDefaultIsThePerChangeGate(unittest.TestCase):
    """Plain `gz check` is the per-change gate; the full tier needs `--full`.

    `Behave` left the gate under GHI #1088. The whole unit tier left it under
    GHI #1191 (operator ruling 2026-10-11): the gate runs the tests the change
    touches, and `--full` runs the tier in CI, at release and as a chore.
    """

    def test_the_change_scope_drops_behave_and_the_whole_unit_tier(self) -> None:
        change = [name for name, _ in _select_check_steps("change")]
        self.assertNotIn("Behave", change)
        self.assertNotIn("Test", change)
        self.assertIn("Test (changed)", change)

    def test_the_full_scope_runs_behave_and_the_whole_unit_tier(self) -> None:
        full = [name for name, _ in _select_check_steps("full")]
        self.assertIn("Behave", full)
        self.assertIn("Test", full)
        self.assertNotIn("Test (changed)", full)

    def test_plain_gz_check_selects_the_change_scope(self) -> None:
        from gzkit.cli.main import _build_parser  # noqa: PLC0415

        args = _build_parser().parse_args(["check"])
        self.assertFalse(args.full)

    def test_full_flag_selects_the_full_scope(self) -> None:
        from gzkit.cli.main import _build_parser  # noqa: PLC0415

        self.assertTrue(_build_parser().parse_args(["check", "--full"]).full)

    def test_the_parsed_command_hands_its_scope_to_the_check_handler(self) -> None:
        """Parsing a flag is not running it: the dispatch must reach the handler."""
        from gzkit.cli.main import _build_parser  # noqa: PLC0415

        for argv, full in ((["check"], False), (["check", "--full"], True)):
            with self.subTest(argv=argv):
                args = _build_parser().parse_args(argv)
                handler = mock.MagicMock()
                with mock.patch("gzkit.cli.parser_maintenance._lazy", return_value=handler):
                    args.func(args)
                handler.assert_called_once_with(
                    as_json=False, reuse_verified=False, full=full, cross_platform=False
                )

    def test_the_retired_fast_flag_is_a_usage_error(self) -> None:
        from gzkit.cli.main import _build_parser  # noqa: PLC0415

        with self.assertRaises(SystemExit) as raised:
            _build_parser().parse_args(["check", "--fast"])
        self.assertEqual(raised.exception.code, 2)


class TestTheCrossPlatformScope(unittest.TestCase):
    """The second CI platform runs what can fail differently there, and no more (GHI #1253).

    Windows is in the CI matrix for one failure class (`.github/workflows/ci.yml`,
    the comment above `strategy:`): compared paths (#383), console encoding (#275),
    subprocess decoding (#582), line endings (#681), and a typecheck exclude glob
    that never matched (#788). Every step that reads paths, spawns a subprocess,
    decodes output or compares bytes stays. A step whose verdict cannot depend on
    the platform is dropped there; Linux still runs it in the same CI run.
    """

    _PLATFORM_SENSITIVE = (
        "Test",
        "Behave",
        "Typecheck",
        "Lint",
        "Line endings",
        "Surface fidelity",
        "Smoke tier",
        "Docs build",
        "Validate default scopes",
    )

    def test_it_keeps_every_step_the_platform_failure_class_reaches(self) -> None:
        steps = [name for name, _ in _select_check_steps("cross-platform")]
        for step in self._PLATFORM_SENSITIVE:
            with self.subTest(step=step):
                self.assertIn(step, steps)

    def test_it_runs_the_whole_unit_tier_not_the_changed_tests(self) -> None:
        steps = [name for name, _ in _select_check_steps("cross-platform")]
        self.assertIn("Test", steps)
        self.assertNotIn("Test (changed)", steps)

    def test_it_is_the_full_sweep_minus_exactly_the_declared_skips(self) -> None:
        full = {name for name, _ in _select_check_steps("full")}
        cross = {name for name, _ in _select_check_steps("cross-platform")}
        declared = _scope_skips("cross-platform")
        self.assertTrue(declared, "the scope must be declared, or it silently runs everything")
        self.assertEqual(full - cross, set(declared))
        self.assertEqual(cross - full, set())

    def test_it_drops_the_guard_canary_sweep(self) -> None:
        """The sweep grades test strength; it sits last on the Windows critical path."""
        steps = [name for name, _ in _select_check_steps("cross-platform")]
        self.assertNotIn("Guard canary sweep", steps)

    def test_it_never_records_the_verified_fingerprint(self) -> None:
        self.assertFalse(_scope_records_verified("cross-platform"))

    def test_a_change_pass_does_not_satisfy_a_cross_platform_reuse(self) -> None:
        """A per-change pass never ran the unit tier, so it cannot stand in for it."""
        from gzkit.commands.quality import _report_reuse_skip  # noqa: PLC0415

        with (
            tempfile.TemporaryDirectory() as tmp,
            mock.patch("gzkit.check_fingerprint.already_verified", return_value=None) as seen,
        ):
            self.assertFalse(_report_reuse_skip(Path(tmp), scope="cross-platform", as_json=True))
        self.assertEqual(seen.call_args.kwargs["accept"], frozenset({"full"}))

    def test_the_flag_hands_the_cross_platform_scope_to_the_handler(self) -> None:
        from gzkit.cli.main import _build_parser  # noqa: PLC0415

        args = _build_parser().parse_args(["check", "--cross-platform"])
        handler = mock.MagicMock()
        with mock.patch("gzkit.cli.parser_maintenance._lazy", return_value=handler):
            args.func(args)
        handler.assert_called_once_with(
            as_json=False, reuse_verified=False, full=False, cross_platform=True
        )

    def test_every_scope_flag_has_a_help_example_that_parses(self) -> None:
        """`gz check --help` shows an operator how to reach each scope, and each example runs."""
        import shlex  # noqa: PLC0415

        from gzkit.cli.main import _build_parser  # noqa: PLC0415

        parser = _build_parser()
        check = subcommand_parser(parser, "check")
        examples = [
            line.strip()
            for line in (check.epilog or "").split("Exit codes")[0].splitlines()
            if line.strip().startswith("gz check")
        ]
        for example in examples:
            with self.subTest(example=example):
                parser.parse_args(shlex.split(example)[1:])
        for flag in ("--full", "--cross-platform"):
            with self.subTest(flag=flag):
                self.assertTrue(
                    any(flag in shlex.split(example) for example in examples),
                    f"no `gz check --help` example reaches the {flag} scope",
                )

    def test_full_and_cross_platform_together_are_a_usage_error(self) -> None:
        from gzkit.cli.main import _build_parser  # noqa: PLC0415

        with self.assertRaises(SystemExit) as raised:
            _build_parser().parse_args(["check", "--full", "--cross-platform"])
        self.assertEqual(raised.exception.code, 2)

    def test_the_check_handler_runs_the_cross_platform_steps(self) -> None:
        from gzkit.commands import quality  # noqa: PLC0415

        with (
            mock.patch.object(quality, "_select_check_steps", side_effect=RuntimeError) as sel,
            mock.patch.object(quality, "get_project_root", return_value=Path(".")),
            self.assertRaises(RuntimeError),
        ):
            quality.check(cross_platform=True)
        sel.assert_called_once_with("cross-platform")


if __name__ == "__main__":
    unittest.main()
