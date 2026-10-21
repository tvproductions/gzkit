"""Unit tests for the MX shared checkpoint (OBPI-0.0.74-02).

The checkpoint is the single place code reads the marker and resolves guard
severity under MX mode.

REQ-0.0.74-02-01 and REQ-0.0.74-02-02 are BEHAVIOR REQs proven by the
``@covers``-decorated methods below. REQ-0.0.74-02-03 is a [structural-fence]
REQ — its proof channel is the parent ADR § Boundary Invariants #2 (checkpoint
is the single severity authority) per ADR-0.0.59, not a ``@covers`` test;
``TestValidateCmdWiring`` backs it behaviorally but is intentionally not
decorated as the fence's proof.
"""

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from gzkit.mx import marker
from gzkit.mx.marker import Marker
from gzkit.traceability import covers


def _mk_root(tmp: str) -> Path:
    root = Path(tmp)
    (root / ".gzkit").mkdir(parents=True, exist_ok=True)
    return root


def _write_marker(root: Path) -> None:
    marker.write(Marker(session_id="test-session"), root)


class TestInHangar(unittest.TestCase):
    """REQ-0.0.74-02-01: inside the hangar ordinary guards become advisory;
    gate5_invariants stay fail-closed regardless."""

    @covers("REQ-0.0.74-02-01")
    def test_ordinary_guard_is_advisory_in_hangar(self) -> None:
        from gzkit.mx import checkpoint

        with TemporaryDirectory() as tmp:
            root = _mk_root(tmp)
            _write_marker(root)
            self.assertTrue(checkpoint.is_advisory("gate3-docs", root))

    @covers("REQ-0.0.74-02-01")
    def test_gate5_invariant_stays_fail_closed_in_hangar(self) -> None:
        from gzkit.mx import checkpoint

        with TemporaryDirectory() as tmp:
            root = _mk_root(tmp)
            _write_marker(root)
            # gate5_invariants must never become advisory, even inside the hangar
            for invariant in checkpoint.GATE5_INVARIANTS:
                with self.subTest(invariant=invariant):
                    self.assertFalse(
                        checkpoint.is_advisory(invariant, root),
                        f"gate5_invariant '{invariant}' must stay fail-closed in the hangar",
                    )

    @covers("REQ-0.0.74-02-01")
    def test_ledger_scope_stays_fail_closed_in_hangar(self) -> None:
        from gzkit.mx import checkpoint

        with TemporaryDirectory() as tmp:
            root = _mk_root(tmp)
            _write_marker(root)
            # "ledger" is the validate_cmd scope protecting ledger integrity —
            # a gate5_invariant that must never be dropped to advisory.
            self.assertFalse(checkpoint.is_advisory("ledger", root))


class TestOutsideHangar(unittest.TestCase):
    """REQ-0.0.74-02-02: outside the hangar the checkpoint is a strict no-op —
    every guard is unchanged (not advisory), regardless of the guard name."""

    @covers("REQ-0.0.74-02-02")
    def test_ordinary_guard_not_advisory_without_marker(self) -> None:
        from gzkit.mx import checkpoint

        with TemporaryDirectory() as tmp:
            root = _mk_root(tmp)
            # No marker written — outside the hangar
            self.assertFalse(checkpoint.is_advisory("gate3-docs", root))

    @covers("REQ-0.0.74-02-02")
    def test_gate5_invariant_not_advisory_without_marker(self) -> None:
        from gzkit.mx import checkpoint

        with TemporaryDirectory() as tmp:
            root = _mk_root(tmp)
            for invariant in checkpoint.GATE5_INVARIANTS:
                with self.subTest(invariant=invariant):
                    self.assertFalse(
                        checkpoint.is_advisory(invariant, root),
                        f"'{invariant}' must not be advisory outside the hangar",
                    )

    @covers("REQ-0.0.74-02-02")
    def test_multiple_guards_strict_noop_without_marker(self) -> None:
        from gzkit.mx import checkpoint

        guards = ["surfaces", "documents", "briefs", "instructions", "taxonomy"]
        with TemporaryDirectory() as tmp:
            root = _mk_root(tmp)
            for guard in guards:
                with self.subTest(guard=guard):
                    self.assertFalse(
                        checkpoint.is_advisory(guard, root),
                        f"guard '{guard}' must not be advisory outside the hangar",
                    )


class TestValidateCmdWiring(unittest.TestCase):
    """Backs REQ-0.0.74-02-03 (structural-fence): validate_cmd's _run_scope_checks
    imports and consults the checkpoint for every scope.

    Intentionally not @covers-decorated: the fence's proof channel is the parent
    ADR § Boundary Invariants #2 per ADR-0.0.59, not a unit test.
    """

    def test_validate_cmd_imports_checkpoint(self) -> None:
        import ast
        from pathlib import Path

        source = (
            Path(__file__).parent.parent.parent / "src" / "gzkit" / "commands" / "validate_cmd.py"
        ).read_text(encoding="utf-8")
        tree = ast.parse(source)
        # The checkpoint is imported lazily inside _run_scope_checks; look for
        # any import that references 'checkpoint' in a module name.
        imports_checkpoint = False
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                # Matches both `from gzkit.mx import checkpoint` (names) and
                # `from gzkit.mx.checkpoint import ...` (module).
                if node.module and "checkpoint" in node.module:
                    imports_checkpoint = True
                    break
                if any("checkpoint" in alias.name for alias in node.names):
                    imports_checkpoint = True
                    break
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if "checkpoint" in alias.name:
                        imports_checkpoint = True
                        break
        self.assertTrue(
            imports_checkpoint,
            "validate_cmd.py must import the checkpoint module to wire the funnel",
        )


class TestSafeMode(unittest.TestCase):
    """Safe mode lowers every guard outside the floor to advisory, as the hangar does.

    Operator ruling 2026-10-17 (R6, "A on all five"): while a safe-mode marker is open,
    every guard outside ``GATE5_INVARIANTS`` drops to advisory and the hard-gate exit
    re-runs all at full strength. GHI #1244 built safe mode with every guard at full
    strength; that was the disposition the ruling replaced.
    """

    def test_ordinary_guard_is_advisory_under_a_safe_mode_marker(self) -> None:
        from gzkit.mx import checkpoint, disposition, levels

        with TemporaryDirectory() as tmp:
            root = _mk_root(tmp)
            marker.write(Marker(session_id="safe-session", mode="safe"), root)
            self.assertTrue(checkpoint.is_advisory("gate3-docs", root))
            self.assertEqual(
                checkpoint.resolve("gate3-docs", levels.ERROR, root),
                disposition.Route.ADVISORY,
            )
            self.assertFalse(checkpoint.blocks("gate3-docs", levels.ERROR, root))

    def test_floor_guard_stays_critical_under_a_safe_mode_marker(self) -> None:
        from gzkit.mx import checkpoint, disposition, levels
        from gzkit.mx.invariants import GATE5_INVARIANTS

        with TemporaryDirectory() as tmp:
            root = _mk_root(tmp)
            marker.write(Marker(session_id="safe-session", mode="safe"), root)
            for name in GATE5_INVARIANTS:
                self.assertFalse(checkpoint.is_advisory(name, root), name)
                self.assertEqual(
                    checkpoint.resolve(name, levels.ERROR, root),
                    disposition.route(levels.CRITICAL),
                    name,
                )

    def test_the_hangar_mode_still_demotes(self) -> None:
        from gzkit.mx import checkpoint

        with TemporaryDirectory() as tmp:
            root = _mk_root(tmp)
            marker.write(Marker(session_id="mx-session", mode="mx"), root)
            self.assertTrue(checkpoint.is_advisory("gate3-docs", root))


class TestExitingMarker(unittest.TestCase):
    """A marker held by `gz mx exit` demotes nothing (GHI #1257).

    Exit keeps the marker through its re-run, as `gz obpi complete` keeps its lock
    through its checks, and marks it ``exiting``; the re-run must still see every
    guard at full strength (REQ-0.0.74-05-01).
    """

    def test_an_exiting_marker_does_not_demote(self) -> None:
        from gzkit.mx import checkpoint, disposition, levels

        for mode in ("mx", "safe"):
            with self.subTest(mode=mode), TemporaryDirectory() as tmp:
                root = _mk_root(tmp)
                marker.write(Marker(session_id="s", mode=mode, exiting=True), root)
                self.assertFalse(checkpoint.hangar_demotes(root))
                self.assertEqual(
                    checkpoint.resolve("gate3-docs", levels.ERROR, root),
                    disposition.route(levels.ERROR),
                )

    def test_an_unreadable_marker_keeps_the_presence_reading(self) -> None:
        from gzkit.mx import checkpoint

        with TemporaryDirectory() as tmp:
            root = _mk_root(tmp)
            marker.marker_path(root).write_text("{not json", encoding="utf-8")
            self.assertTrue(checkpoint.hangar_demotes(root))


class TestValidateAnnouncesDemotion(unittest.TestCase):
    """`gz validate` announces a demoted scope's findings rather than dropping them.

    `checkpoint.demote_notice`: "Demotion is announced, never silent: advisory means
    non-grounding, not discarded" (GHI #843). `_run_scope_checks` dropped a demoted
    scope's findings with nothing said, so `gz validate --id-seam` read "All
    validations passed" over a real violation under safe mode (drydock RO-3, 2026-10-21).
    """

    def _run(self, root: Path) -> tuple[list, str]:
        import contextlib
        import io
        from unittest.mock import patch

        from gzkit.commands import validate_cmd
        from gzkit.core.validation_rules import ValidationError

        finding = ValidationError(type="t", artifact="a.py", message="the finding itself")
        stderr = io.StringIO()
        with (
            patch.object(validate_cmd, "_default_scope_runners", return_value={}),
            patch.object(
                validate_cmd, "_explicit_scope_runners", return_value={"id_seam": lambda: [finding]}
            ),
            contextlib.redirect_stderr(stderr),
        ):
            errors = validate_cmd._run_scope_checks(root, {}, {"id_seam": True}, run_all=False)
        return errors, stderr.getvalue()

    def test_a_demoted_scope_names_itself_and_its_findings_on_stderr(self) -> None:
        with TemporaryDirectory() as tmp:
            root = _mk_root(tmp)
            marker.write(Marker(session_id="safe-session", mode="safe"), root)
            errors, stderr = self._run(root)
        self.assertEqual(errors, [])
        self.assertIn("[MX advisory] guard 'id_seam'", stderr)
        self.assertIn("a.py: the finding itself", stderr)

    def test_a_grounding_scope_returns_its_findings_and_announces_nothing(self) -> None:
        with TemporaryDirectory() as tmp:
            errors, stderr = self._run(_mk_root(tmp))
        self.assertEqual([e.message for e in errors], ["the finding itself"])
        self.assertEqual(stderr, "")
