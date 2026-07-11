"""Unit tests for the mx-door airlock wiring (OBPI-0.33.0-04).

The mx/ghi door (``gz mx enter`` / ``gz mx exit``) crosses the SAME airlock
membrane the pipeline door does — consuming the SHARED primitive extracted by
OBPI-02/03 (``gzkit.airlock.enter.airlock_enter`` /
``gzkit.airlock.exit.airlock_exit``), never forking a private variant.

DIAGNOSTIC-ONLY tracer (option-c reconcile, attestor g0, 2026-07-11): the
acknowledge-and-decide gate LOGS its decision; fail-closing on a NO-GO and
real-entry / brief-less-DECLARE seam accounting are the attested deferred
calibration frontier (parent ADR § Consequences), not this increment.

REQ-0.33.0-04-01..04 are BEHAVIOR REQs proven by the ``@covers`` methods below.
"""

from __future__ import annotations

import inspect
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from gzkit.commands import mx_cmd
from gzkit.mx import marker
from gzkit.traceability import covers
from tests.commands.common import SilencedConsoleTestCase


def _mk_root(tmp: str) -> Path:
    root = Path(tmp)
    (root / ".gzkit").mkdir(parents=True, exist_ok=True)
    return root


def _mk_brief(root: Path, scope: str, *, names: str | None = None) -> None:
    """Create a resolvable ADR artifact the mx airlock resolver will find.

    When ``names`` is None the artifact names no reach dependent, so an injected
    reach edge stays un-accounted (-> HOLD).  When ``names`` is set the artifact
    accounts for that dependent (-> PROCEED).
    """
    d = root / "docs" / "design" / "adr" / "pre-release" / scope
    d.mkdir(parents=True, exist_ok=True)
    body = f"# {scope}\n\n## Allowed Paths\n\n- `src/gzkit/commands/mx_cmd.py`\n\n"
    body += f"This entry accounts for {names}.\n" if names else "Names no reach dependent.\n"
    (d / f"{scope}.md").write_text(body, encoding="utf-8")


def _events(root: Path, event_type: str) -> list[dict]:
    p = root / ".gzkit" / "ledger.jsonl"
    if not p.exists():
        return []
    out: list[dict] = []
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            ev = json.loads(line)
        except ValueError:
            continue
        if ev.get("event") == event_type:
            out.append(ev)
    return out


class TestMxEnterCallsAirlockIn(SilencedConsoleTestCase):
    """REQ-0.33.0-04-01: gz mx enter reaches airlock-IN, diagnostic-only, every reason."""

    @covers("REQ-0.33.0-04-01")
    def test_enter_books_airlock_in_regardless_of_reason(self) -> None:
        # BI-2: the gate fires on EVERY entry; the reason selects weight, never whether.
        for reason in ("repair drifted allowlist", "reconcile a stale marker"):
            with TemporaryDirectory() as tmp:
                root = _mk_root(tmp)
                _mk_brief(root, "ADR-TESTMX")
                mx_cmd.mx_enter_cmd(
                    reason=reason,
                    attestor="g0",
                    inspection_scope=["ADR-TESTMX"],
                    project_root=root,
                )
                self.assertEqual(
                    len(_events(root, "airlock_in")),
                    1,
                    f"airlock-IN must be booked to L2 on enter for reason={reason!r}",
                )

    @covers("REQ-0.33.0-04-01")
    def test_airlock_in_fires_before_the_hangar_marker_write(self) -> None:
        src = inspect.getsource(mx_cmd.mx_enter_cmd)
        in_idx = src.find("_run_mx_airlock_in_diagnostic")
        marker_idx = src.find("marker.write")
        self.assertNotEqual(in_idx, -1, "mx_enter_cmd reaches the airlock-IN seam")
        self.assertNotEqual(marker_idx, -1, "mx_enter_cmd writes the hangar marker")
        self.assertLess(in_idx, marker_idx, "airlock-IN fires BEFORE the hangar marker write")

    @covers("REQ-0.33.0-04-01")
    def test_no_go_is_diagnostic_only_marker_still_written(self) -> None:
        with TemporaryDirectory() as tmp:
            root = _mk_root(tmp)
            _mk_brief(root, "ADR-TESTMX")  # names no dependent -> DEP-HIDDEN stays un-accounted
            with patch.object(mx_cmd.console, "print") as pr:
                mx_cmd.mx_enter_cmd(
                    reason="repair",
                    attestor="g0",
                    inspection_scope=["ADR-TESTMX"],
                    project_root=root,
                    _airlock_reach=lambda _node: ["DEP-HIDDEN"],
                )
            self.assertTrue(
                marker.is_active(root),
                "a NO-GO is diagnostic-only — it never blocks the hangar marker write",
            )
            printed = " ".join(str(c.args[0]) for c in pr.call_args_list if c.args)
            self.assertIn(
                "DEP-HIDDEN",
                printed,
                "the NO-GO is surfaced as a diagnostic refusal naming the un-accounted seam",
            )


class TestMxExitCallsAirlockOut(SilencedConsoleTestCase):
    """REQ-0.33.0-04-02: gz mx exit reaches airlock-OUT, additive to the hard gate."""

    @covers("REQ-0.33.0-04-02")
    def test_exit_books_airlock_out_when_guards_pass(self) -> None:
        with TemporaryDirectory() as tmp:
            root = _mk_root(tmp)
            _mk_brief(root, "ADR-TESTMX")
            mx_cmd.mx_enter_cmd(
                reason="repair", attestor="g0", inspection_scope=["ADR-TESTMX"], project_root=root
            )
            mx_cmd.mx_exit_cmd(attestor="g0", project_root=root, _run_guards=lambda _r: 0)
            self.assertEqual(
                len(_events(root, "airlock_out")),
                1,
                "airlock-OUT is booked to L2 at the co-equal exit membrane",
            )
            self.assertEqual(
                len(_events(root, "mx_session_closed")), 1, "the close signature is still written"
            )

    @covers("REQ-0.33.0-04-02")
    def test_airlock_out_is_additive_hard_gate_still_refuses_red(self) -> None:
        with TemporaryDirectory() as tmp:
            root = _mk_root(tmp)
            _mk_brief(root, "ADR-TESTMX")
            mx_cmd.mx_enter_cmd(
                reason="repair", attestor="g0", inspection_scope=["ADR-TESTMX"], project_root=root
            )
            with self.assertRaises(SystemExit) as ctx:
                mx_cmd.mx_exit_cmd(attestor="g0", project_root=root, _run_guards=lambda _r: 3)
            self.assertEqual(
                ctx.exception.code,
                3,
                "the existing hard guard-gate still hard-refuses on red — airlock-OUT is additive",
            )
            self.assertEqual(
                _events(root, "mx_session_closed"),
                [],
                "no close event is written when the hard gate is red",
            )
            self.assertEqual(
                _events(root, "airlock_out"),
                [],
                "airlock-OUT does not leak past the red hard gate — it is strictly "
                "additive, firing only after the guards pass (not before/around them)",
            )


class TestMxDoorConsumesSharedPrimitive(SilencedConsoleTestCase):
    """REQ-0.33.0-04-03: both seams reach the SAME shared primitive; calibration deferred."""

    @covers("REQ-0.33.0-04-03")
    def test_both_seams_reach_the_shared_pipeline_primitive(self) -> None:
        import gzkit.airlock.enter as enter_mod
        import gzkit.airlock.exit as exit_mod

        self.assertIs(mx_cmd.airlock_enter, enter_mod.airlock_enter)
        self.assertIs(mx_cmd.airlock_exit, exit_mod.airlock_exit)
        in_src = inspect.getsource(mx_cmd._run_mx_airlock_in_diagnostic)
        out_src = inspect.getsource(mx_cmd._run_mx_airlock_out_diagnostic)
        self.assertIn("airlock_enter", in_src, "the enter seam reaches airlock_enter")
        self.assertIn("airlock_exit", out_src, "the exit seam reaches airlock_exit")

    @covers("REQ-0.33.0-04-03")
    def test_mx_door_defines_no_local_ceremony_profile_branch(self) -> None:
        # The delivered primitive exposes NO ceremony-profile parameter; the mx door
        # asserts none of its own — corrective-vs-tight is the deferred frontier.
        src = inspect.getsource(mx_cmd)
        self.assertNotIn("ceremony_profile", src)
        self.assertNotIn("ceremony_weight", src)


class TestMxDoorNoPrivateFork(SilencedConsoleTestCase):
    """REQ-0.33.0-04-04: consume-only; no private airlock reimplementation (BI-3, Door drift)."""

    @covers("REQ-0.33.0-04-04")
    def test_imports_airlock_from_the_single_extracted_source(self) -> None:
        import gzkit.airlock.enter as enter_mod
        import gzkit.airlock.exit as exit_mod

        self.assertIs(
            mx_cmd.airlock_enter,
            enter_mod.airlock_enter,
            "mx door imports airlock_enter from gzkit.airlock.enter (single source)",
        )
        self.assertIs(
            mx_cmd.airlock_exit,
            exit_mod.airlock_exit,
            "mx door imports airlock_exit from gzkit.airlock.exit (single source)",
        )

    @covers("REQ-0.33.0-04-04")
    def test_mx_door_declares_no_local_airlock_reimplementation(self) -> None:
        src = inspect.getsource(mx_cmd)
        self.assertNotIn("def airlock_enter", src, "no local airlock_enter fork in the mx door")
        self.assertNotIn("def airlock_exit", src, "no local airlock_exit fork in the mx door")
