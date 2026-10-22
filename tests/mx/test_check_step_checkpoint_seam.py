"""Unit tests for the gz check step-layer checkpoint seam (OBPI-0.0.74-20).

The seam lives in ``_apply_mx_seam`` (``src/gzkit/commands/quality.py``):
a single function called once per step in the ``check()`` loop that routes
each step's ``returncode=3`` result through ``checkpoint.resolve`` — demoting
to advisory under an active marker, preserving full strength outside.

REQ-0.0.74-20-01 and -02 are BEHAVIOR REQs proven by ``@covers``-decorated
methods.  REQ-0.0.74-20-03 is proven by ``TestFloorPin``.
REQ-0.0.74-20-04 is proven by ``TestExcludedPaths``.
REQ-0.0.74-20-05 is a [FENCE] REQ — proof channel is parent ADR
§ Boundary Invariants #2 (OBPI-02, OBPI-09, OBPI-11, OBPI-12, OBPI-20);
not proven by a ``@covers`` test.
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


def _failing_result():
    """Return a QualityResult representing a policy-breach (returncode=3)."""
    from gzkit.quality import QualityResult

    return QualityResult(
        success=False,
        command="test-step",
        stdout="violation found",
        stderr="",
        returncode=3,
    )


class TestDemoteUnderMarker(unittest.TestCase):
    """REQ-0.0.74-20-01/-02: non-floor step demotes under marker, full-strength outside."""

    @covers("REQ-0.0.74-20-01")
    def test_non_floor_step_demotes_to_advisory_under_marker(self) -> None:
        """Under an active marker a non-floor step's returncode=3 demotes to success."""
        from gzkit.commands.quality import _apply_mx_seam
        from gzkit.mx import levels

        with TemporaryDirectory() as tmp:
            root = _mk_root(tmp)
            _write_marker(root)

            result = _apply_mx_seam(_failing_result(), "test-guard", levels.ERROR, root)

            self.assertTrue(
                result.success,
                "Non-floor step must demote to advisory (success=True) under marker",
            )
            self.assertEqual(result.returncode, 0, "Demoted result must have returncode=0")

    @covers("REQ-0.0.74-20-02")
    def test_non_floor_step_stays_fatal_without_marker(self) -> None:
        """Without a marker a non-floor step's returncode=3 stays fatal (full strength)."""
        from gzkit.commands.quality import _apply_mx_seam
        from gzkit.mx import levels

        with TemporaryDirectory() as tmp:
            root = _mk_root(tmp)
            # No marker written — outside the hangar

            result = _apply_mx_seam(_failing_result(), "test-guard", levels.ERROR, root)

            self.assertFalse(
                result.success,
                "Non-floor step must stay fatal (success=False) without marker",
            )
            self.assertEqual(result.returncode, 3, "Fatal result must retain returncode=3")

    @covers("REQ-0.0.74-20-02")
    def test_success_result_passes_through_unchanged(self) -> None:
        """A passing result (returncode=0) is not modified by the seam."""
        from gzkit.commands.quality import _apply_mx_seam
        from gzkit.mx import levels
        from gzkit.quality import QualityResult

        passing = QualityResult(success=True, command="test", stdout="ok", stderr="", returncode=0)
        with TemporaryDirectory() as tmp:
            root = _mk_root(tmp)
            _write_marker(root)  # marker active — should make no difference

            result = _apply_mx_seam(passing, "test-guard", levels.ERROR, root)

            self.assertTrue(result.success)
            self.assertEqual(result.returncode, 0)


class TestFloorPin(unittest.TestCase):
    """REQ-0.0.74-20-03: gate5_invariants guard_names pin CRITICAL and never demote."""

    @covers("REQ-0.0.74-20-03")
    def test_gate5_invariant_step_stays_fatal_under_marker(self) -> None:
        """Every gate5_invariants member stays fatal (returncode=3) even under marker."""
        from gzkit.commands.quality import _apply_mx_seam
        from gzkit.mx import levels
        from gzkit.mx.invariants import GATE5_INVARIANTS

        with TemporaryDirectory() as tmp:
            root = _mk_root(tmp)
            _write_marker(root)

            for invariant in GATE5_INVARIANTS:
                with self.subTest(invariant=invariant):
                    result = _apply_mx_seam(_failing_result(), invariant, levels.ERROR, root)
                    self.assertFalse(
                        result.success,
                        f"Floor member '{invariant}' must stay fatal under marker",
                    )
                    self.assertEqual(
                        result.returncode,
                        3,
                        f"Floor member '{invariant}' must retain returncode=3 under marker",
                    )

    @covers("REQ-0.0.74-20-03")
    def test_gate5_invariant_step_stays_fatal_outside_marker(self) -> None:
        """gate5_invariants members are fatal outside the marker too (no regression)."""
        from gzkit.commands.quality import _apply_mx_seam
        from gzkit.mx import levels
        from gzkit.mx.invariants import GATE5_INVARIANTS

        with TemporaryDirectory() as tmp:
            root = _mk_root(tmp)
            # No marker

            for invariant in GATE5_INVARIANTS:
                with self.subTest(invariant=invariant):
                    result = _apply_mx_seam(_failing_result(), invariant, levels.ERROR, root)
                    self.assertFalse(result.success)
                    self.assertEqual(result.returncode, 3)


class TestEnforcementFloorPin(unittest.TestCase):
    """GHI #651: the enforcement-floor (§5 meta-validator) gz check step must pin
    CRITICAL and never demote to advisory inside the hangar — a FACADE must ground
    under an active marker, not silently pass (ADR-0.0.74 BI#3 / §5)."""

    def test_enforcement_floor_step_pinned_critical(self) -> None:
        """The 'Enforcement floor' step is registered at CRITICAL, not the
        ERROR fallback that demotes under a marker."""
        from gzkit.commands.quality import _STEP_GUARD_META
        from gzkit.mx import levels

        guard_name, emitted_level = _STEP_GUARD_META["Enforcement floor"]
        self.assertEqual(guard_name, "enforcement-floor")
        self.assertEqual(emitted_level, levels.CRITICAL)

    def test_enforcement_floor_facade_grounds_under_marker(self) -> None:
        """A failing enforcement-floor step (FACADE, returncode=3) stays fatal
        inside the hangar — resolved exactly as check() would resolve it."""
        from gzkit.commands.quality import _STEP_GUARD_META, _apply_mx_seam
        from gzkit.mx import levels

        with TemporaryDirectory() as tmp:
            root = _mk_root(tmp)
            _write_marker(root)

            guard_name, emitted_level = _STEP_GUARD_META.get(
                "Enforcement floor", ("enforcement-floor", levels.ERROR)
            )
            result = _apply_mx_seam(_failing_result(), guard_name, emitted_level, root)

        self.assertFalse(
            result.success,
            "A FACADE must ground under an active marker, not demote to advisory",
        )
        self.assertEqual(result.returncode, 3, "Pinned floor step must retain returncode=3")


class TestExcludedPaths(unittest.TestCase):
    """REQ-0.0.74-20-04: excluded policy paths are not routed through the seam."""

    @covers("REQ-0.0.74-20-04")
    def test_excluded_guard_names_absent_from_step_guard_meta(self) -> None:
        """_STEP_GUARD_META contains no guard_name matching the excluded policy paths."""
        from gzkit.commands.quality import _STEP_GUARD_META

        guard_names = set(_STEP_GUARD_META.values())
        # Each value is (guard_name, emitted_level); extract guard_names
        step_guard_names = {gn for gn, _ in guard_names}

        # The sensitivity security-floor handler and attestation lane/kind handler
        # must NOT appear in the step guard metadata — they self-decide and bypass
        # the seam entirely.
        for excluded in ("sensitivity", "attestation-lane-kind"):
            self.assertNotIn(
                excluded,
                step_guard_names,
                f"Excluded policy path '{excluded}' must not be in _STEP_GUARD_META",
            )

    @covers("REQ-0.0.74-20-04")
    def test_sensitivity_guard_name_not_in_build_check_steps(self) -> None:
        """_build_check_steps() step names do not include a sensitivity-mapped step."""
        from gzkit.commands.quality import _STEP_GUARD_META, _build_check_steps

        steps = _build_check_steps()
        step_display_names = {name for name, _ in steps}

        # Resolve guard_names for all current steps
        step_guard_names = {
            _STEP_GUARD_META.get(name, (name.lower().replace(" ", "-"), None))[0]
            for name in step_display_names
        }

        # The sensitivity handler must not appear as a guard routed through the seam.
        self.assertNotIn(
            "sensitivity",
            step_guard_names,
            "The --sensitivity handler must not be wired through the checkpoint seam",
        )


class TestDemotionIsAnnounced(unittest.TestCase):
    """A demoted step is announced with its findings, never shown as a bare pass (GHI #843).

    Under the hangar the Config registry step read green over a real seam bypass
    that `gz validate --config-registry` reported with exit 3: the seam turned the
    breach into a pass and nothing rendered the step's output.
    """

    def _demoted(self):
        from gzkit.commands.quality import _apply_mx_seam
        from gzkit.mx import levels

        with TemporaryDirectory() as tmp:
            root = _mk_root(tmp)
            _write_marker(root)
            return _apply_mx_seam(_failing_result(), "test-guard", levels.ERROR, root)

    def test_a_demoted_result_names_its_guard_and_keeps_its_findings(self) -> None:
        result = self._demoted()
        self.assertEqual(result.demoted_guard, "test-guard")
        self.assertEqual(result.stdout, "violation found")

    def test_a_full_strength_or_passing_result_is_not_marked_demoted(self) -> None:
        from gzkit.commands.quality import _apply_mx_seam
        from gzkit.mx import levels
        from gzkit.quality import QualityResult

        passing = QualityResult(success=True, command="t", stdout="", stderr="", returncode=0)
        with TemporaryDirectory() as tmp:
            root = _mk_root(tmp)
            fatal = _apply_mx_seam(_failing_result(), "test-guard", levels.ERROR, root)
            _write_marker(root)
            passed = _apply_mx_seam(passing, "test-guard", levels.ERROR, root)
        self.assertIsNone(fatal.demoted_guard)
        self.assertIsNone(passed.demoted_guard)

    def test_the_check_report_announces_the_demotion_and_its_findings(self) -> None:
        import io
        from contextlib import redirect_stdout

        from gzkit.commands.quality import _render_demoted_steps
        from gzkit.mx.checkpoint import demote_notice
        from gzkit.quality import QualityResult

        quiet = QualityResult(success=True, command="t", stdout="ok", stderr="", returncode=0)
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            _render_demoted_steps([("Config registry", self._demoted()), ("Lint", quiet)])
        output = " ".join(buffer.getvalue().split())
        self.assertIn(" ".join(demote_notice("test-guard").split()), output)
        self.assertIn("violation found", output)
        self.assertIn("Config registry", output)
        self.assertNotIn("Lint", output)

    def test_nothing_is_rendered_when_no_step_was_demoted(self) -> None:
        import io
        from contextlib import redirect_stdout

        from gzkit.commands.quality import _render_demoted_steps
        from gzkit.quality import QualityResult

        quiet = QualityResult(success=True, command="t", stdout="ok", stderr="", returncode=0)
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            _render_demoted_steps([("Lint", quiet)])
        self.assertEqual(buffer.getvalue(), "")


class TestCheckReportsDemotion(unittest.TestCase):
    """`gz check` itself announces a step the hangar demoted, in both output forms."""

    def _run_check(self, *, as_json: bool) -> tuple[list[str], str]:
        import io
        from contextlib import redirect_stdout
        from types import SimpleNamespace
        from unittest.mock import patch

        from gzkit.commands import quality

        printed: list[str] = []
        stdout = io.StringIO()
        steps = [("Config registry", lambda _root: _failing_result())]
        with TemporaryDirectory() as tmp:
            root = _mk_root(tmp)
            _write_marker(root)
            with (
                redirect_stdout(stdout),
                patch.object(
                    quality,
                    "console",
                    SimpleNamespace(print=lambda *args, **_kw: printed.append(str(args[0]))),
                ),
                patch.object(quality, "get_project_root", return_value=root),
                patch.object(quality, "_build_check_steps", return_value=steps),
                patch(
                    "gzkit.quality.run_drift_advisory",
                    return_value=SimpleNamespace(has_drift=False, to_dict=dict),
                ),
                patch("gzkit.flags.registry.load_registry", side_effect=RuntimeError("skip")),
            ):
                quality.check(as_json=as_json)
        return printed, stdout.getvalue()

    def test_the_human_report_carries_the_notice_and_the_finding(self) -> None:
        from gzkit.mx.checkpoint import demote_notice

        printed, _ = self._run_check(as_json=False)
        report = "\n".join(printed)
        self.assertIn(demote_notice("config-registry"), report)
        self.assertIn("violation found", report)

    def test_the_json_report_names_the_demoted_step_and_its_guard(self) -> None:
        import json

        _, stdout = self._run_check(as_json=True)
        payload = json.loads(stdout)
        self.assertTrue(payload["success"])
        self.assertEqual(payload.get("demoted"), {"Config registry": "config-registry"})
