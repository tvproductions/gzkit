"""Wire tests for the OBPI-0.0.25-01 REQ-coverage gate inside ``gz obpi complete``.

The gate parses the brief's ``## Acceptance Criteria`` for REQ-IDs, locates
``@covers``-decorated tests for each, runs them scoped, and refuses
completion when any REQ has zero passing covered tests on heavy/foundation
ADRs. Lite-non-foundation completions warn and proceed.

Coverage map (formal acceptance criteria — see brief § Acceptance Criteria):

| REQ              | Test class                                                |
|------------------|-----------------------------------------------------------|
| REQ-0.0.25-01-01 | TestObpiCompleteHeavyAllReqsCovered (success path)        |
| REQ-0.0.25-01-02 | TestObpiCompleteHeavyUncoveredReq (fail-closed)           |
| REQ-0.0.25-01-03 | TestObpiCompleteFoundationLiteUncovered (foundation OR)   |
| REQ-0.0.25-01-04 | TestObpiCompleteLiteNonFoundationUncovered (warn-only)    |
| REQ-0.0.25-01-05 | TestObpiCompleteHeavyCoveredTestFails (red test fails)    |
| REQ-0.0.25-01-06 | TestObpiCompleteMultipleCoversOnePassing (any-passes)     |

Auxiliary FAIL-CLOSED REQUIREMENTs (#5 AST safety, #7 multi-cover, #9
tempfile fixtures, #11 ordering with the receipt-binding gate, #12 TDD)
are mechanism-level and underwrite the criteria above; tests in this
module use the same mock-rig pattern as
``tests/commands/test_obpi_complete.py``.
"""

from __future__ import annotations

import tempfile
import unittest
from io import StringIO
from pathlib import Path
from unittest.mock import MagicMock, patch

from rich.console import Console

from gzkit.commands.obpi_complete import obpi_complete_cmd
from gzkit.event_evidence import EventAnchor
from gzkit.traceability import covers

_BRIEF_TEMPLATE = """\
---
id: {obpi_id}
parent: {parent_adr}
item: 1
lane: {lane}
status: Draft
---

# {obpi_id}: coverage-gate fixture

## Objective

Test brief for the REQ-coverage gate.

## Acceptance Criteria

{criteria}

## Evidence

### Implementation Summary

- Files created/modified: src/gzkit/commands/obpi_complete.py
- Tests added: tests/commands/test_obpi_complete_coverage_gate.py
- Date completed: 2026-05-02
- Attestation status: Pending
- Defects noted: none

### Key Proof

uv run -m unittest tests.commands.test_obpi_complete_coverage_gate -v passes.

## Human Attestation

- Attestor: `<name>` when required, otherwise `n/a`
- Attestation: substantive attestation text or `n/a`
- Date: YYYY-MM-DD or `n/a`

---

**Brief Status:** Draft

**Date Completed:** -

**Evidence Hash:** -
"""


def _mock_config(mode: str = "heavy"):
    config = MagicMock()
    config.mode = mode
    config.paths.ledger = ".gzkit/ledger.jsonl"
    return config


def _mock_ledger(obpi_id: str, parent_adr: str, lane: str):
    ledger = MagicMock()
    ledger.canonicalize_id.return_value = obpi_id
    graph = {
        obpi_id: {"type": "obpi", "parent": parent_adr, "ledger_completed": False},
        parent_adr: {"type": "adr", "lane": lane},
    }
    ledger.get_artifact_graph.return_value = graph
    ledger.append = MagicMock()
    return ledger


_quiet_console = Console(file=StringIO())


class _CoverageGateWireFixture(unittest.TestCase):
    """Mock-rig for the REQ-coverage gate.

    Patches earlier gates (security, receipt-binding) and the TTY gate so the
    new gate is exercised in isolation. ``passing_test_predicate`` controls
    the scoped-run outcome — tests pass `True` to simulate green covering
    tests, `False` to simulate red, or a per-REQ dict for finer control.
    """

    def _run(
        self,
        *,
        brief_text: str,
        obpi_id: str,
        parent_adr: str,
        lane: str,
        kind: str,
        criteria_reqs: list[str],
        covers_layout: dict[str, str | None],
        passing_predicate,
    ) -> tuple[type[BaseException] | None, int | None, list[str], MagicMock]:
        """Drive ``obpi_complete_cmd`` and return outcome + ledger mock.

        ``covers_layout`` maps REQ-ID → file content (the body of a fixture
        test file under ``tests_root``) or ``None`` (no covering test).
        ``passing_predicate`` is a callable ``(qualified_name) -> bool``
        deciding whether a discovered covering test "passes" when
        ``_any_covering_test_passes`` is called.
        """
        del criteria_reqs  # consumed by the brief_text fixture

        recorded: list[str] = []
        rec_console = Console(file=StringIO(), record=True)
        original_print = rec_console.print

        def _capture(*args, **kwargs):
            recorded.append(" ".join(str(a) for a in args))
            return original_print(*args, **kwargs)

        rec_console.print = _capture  # ty: ignore[invalid-assignment]

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            obpi_file = root / "brief.md"
            obpi_file.write_text(brief_text, encoding="utf-8")

            adr_file = root / "adr.md"
            adr_file.write_text(
                f"---\nid: {parent_adr}\nlane: {lane}\nkind: {kind}\n---\n# {parent_adr}\n",
                encoding="utf-8",
            )

            # Build tests root with @covers fixtures per covers_layout.
            tests_root = root / "tests"
            tests_root.mkdir(parents=True, exist_ok=True)
            for req_id, body in covers_layout.items():
                if body is None:
                    continue
                # File name embeds the REQ to keep fixtures unambiguous.
                fname = f"test_cov_{req_id.replace('.', '_').replace('-', '_')}.py"
                (tests_root / fname).write_text(body, encoding="utf-8")

            ledger_obj = _mock_ledger(obpi_id, parent_adr, lane)

            patches = [
                patch("gzkit.commands.obpi_complete.console", rec_console),
                patch("gzkit.commands.obpi_complete.get_project_root", return_value=root),
                patch(
                    "gzkit.commands.obpi_complete.ensure_initialized",
                    return_value=_mock_config(mode=lane.lower()),
                ),
                patch(
                    "gzkit.commands.obpi_complete.resolve_obpi_file",
                    return_value=(obpi_file, obpi_id),
                ),
                patch("gzkit.commands.obpi_complete.Ledger", return_value=ledger_obj),
                patch(
                    "gzkit.commands.obpi_complete.resolve_adr_file",
                    return_value=(adr_file, parent_adr),
                ),
                patch(
                    "gzkit.commands.obpi_complete.capture_validation_anchor",
                    return_value=EventAnchor(commit="abc1234", semver="0.0.25"),
                ),
                # Bypass earlier gates so the coverage gate runs in isolation.
                patch(
                    "gzkit.commands.obpi_complete._enforce_security_review_gate",
                    MagicMock(return_value=None),
                ),
                patch(
                    "gzkit.commands.obpi_complete._enforce_attestation_receipt_gate",
                    MagicMock(return_value=None),
                ),
                patch(
                    "gzkit.commands.obpi_complete._enforce_reconcile_receipt_gate",
                    MagicMock(return_value=None),
                ),
                # Hook the scoped-run outcome predicate.
                patch(
                    "gzkit.commands.obpi_complete._any_covering_test_passes",
                    side_effect=lambda refs, project_root, **_kw: any(
                        passing_predicate(r.qualified_name) for r in refs
                    ),
                ),
                patch("gzkit.commands.obpi_complete.receipts_root", return_value=root),
            ]
            for p in patches:
                p.start()
            try:
                exc_type: type[BaseException] | None = None
                code: int | None = None
                try:
                    obpi_complete_cmd(
                        obpi=obpi_id,
                        attestor="g0",
                        attestation_text=(
                            "attest completed — receipts arb-step-unittest-" + ("0" * 32)
                        ),
                        implementation_summary="- Files: src/gzkit/governance/req_coverage.py",
                        key_proof="gz obpi complete fires the gate.",
                        as_json=False,
                        dry_run=False,
                    )
                except SystemExit as exc:
                    exc_type = SystemExit
                    code = int(exc.code) if isinstance(exc.code, int) else 1
            finally:
                for p in patches:
                    p.stop()

        return exc_type, code, recorded, ledger_obj


def _covering_body(req_id: str) -> str:
    """Render a fixture test file body decorating ``test_x`` with ``@covers(req_id)``."""
    return (
        "import unittest\n\n"
        "def covers(req_id):\n"
        "    def deco(fn):\n"
        "        return fn\n"
        "    return deco\n\n"
        "class FixtureTests(unittest.TestCase):\n"
        f'    @covers("{req_id}")\n'
        "    def test_x(self):\n"
        "        pass\n"
    )


def _multi_covering_body(req_id: str) -> str:
    """Render a fixture file with two ``@covers(req_id)`` test methods."""
    return (
        "import unittest\n\n"
        "def covers(req_id):\n"
        "    def deco(fn):\n"
        "        return fn\n"
        "    return deco\n\n"
        "class FixtureTests(unittest.TestCase):\n"
        f'    @covers("{req_id}")\n'
        "    def test_alpha(self):\n"
        "        pass\n\n"
        f'    @covers("{req_id}")\n'
        "    def test_beta(self):\n"
        "        pass\n"
    )


# ---------------------------------------------------------------------------
# REQ-0.0.25-01-01 — heavy/foundation, all REQs covered → completion proceeds
# ---------------------------------------------------------------------------


class TestObpiCompleteHeavyAllReqsCovered(_CoverageGateWireFixture):
    """REQ-0.0.25-01-01 — every REQ has a passing covered test → exit 0."""

    @covers("REQ-0.0.25-01-01")
    def test_heavy_all_covered_passes(self) -> None:
        criteria = "\n".join(
            [
                "- [ ] REQ-9.9.9-99-01: First.",
                "- [ ] REQ-9.9.9-99-02: Second.",
            ]
        )
        brief = _BRIEF_TEMPLATE.format(
            obpi_id="OBPI-9.9.9-99-fixture",
            parent_adr="ADR-9.9.9-fixture",
            lane="Heavy",
            criteria=criteria,
        )
        exc, code, _output, _ledger = self._run(
            brief_text=brief,
            obpi_id="OBPI-9.9.9-99-fixture",
            parent_adr="ADR-9.9.9-fixture",
            lane="Heavy",
            kind="foundation",
            criteria_reqs=["REQ-9.9.9-99-01", "REQ-9.9.9-99-02"],
            covers_layout={
                "REQ-9.9.9-99-01": _covering_body("REQ-9.9.9-99-01"),
                "REQ-9.9.9-99-02": _covering_body("REQ-9.9.9-99-02"),
            },
            passing_predicate=lambda _qn: True,
        )
        # No SystemExit raised by the coverage gate → completion path proceeded.
        # (Subsequent ledger writes/file mutation may happen; we assert only
        # that the gate did not block.)
        self.assertIsNone(exc)
        self.assertIsNone(code)


# ---------------------------------------------------------------------------
# REQ-0.0.25-01-02 — heavy with one uncovered REQ → exit 3 + structured message
# ---------------------------------------------------------------------------


class TestObpiCompleteHeavyUncoveredReq(_CoverageGateWireFixture):
    """REQ-0.0.25-01-02 — heavy lane with uncovered REQ exits 3."""

    @covers("REQ-0.0.25-01-02")
    def test_heavy_uncovered_exits_3_with_message(self) -> None:
        criteria = "\n".join(
            [
                "- [ ] REQ-9.9.9-99-01: Covered.",
                "- [ ] REQ-9.9.9-99-02: Uncovered.",
            ]
        )
        brief = _BRIEF_TEMPLATE.format(
            obpi_id="OBPI-9.9.9-99-fixture",
            parent_adr="ADR-9.9.9-fixture",
            lane="Heavy",
            criteria=criteria,
        )
        exc, code, output, ledger = self._run(
            brief_text=brief,
            obpi_id="OBPI-9.9.9-99-fixture",
            parent_adr="ADR-9.9.9-fixture",
            lane="Heavy",
            kind="foundation",
            criteria_reqs=["REQ-9.9.9-99-01", "REQ-9.9.9-99-02"],
            covers_layout={
                "REQ-9.9.9-99-01": _covering_body("REQ-9.9.9-99-01"),
                "REQ-9.9.9-99-02": None,
            },
            passing_predicate=lambda _qn: True,
        )
        self.assertIs(exc, SystemExit)
        self.assertEqual(code, 3)
        joined = " ".join(output)
        self.assertIn("REQ-9.9.9-99-02", joined)
        # No completion event written.
        ledger.append.assert_not_called()


# ---------------------------------------------------------------------------
# REQ-0.0.25-01-03 — foundation kind on lite lane still fails closed
# ---------------------------------------------------------------------------


class TestObpiCompleteFoundationLiteUncovered(_CoverageGateWireFixture):
    """REQ-0.0.25-01-03 — foundation kind overrides lite lane."""

    @covers("REQ-0.0.25-01-03")
    def test_foundation_lite_uncovered_exits_3(self) -> None:
        criteria = "- [ ] REQ-9.9.9-99-01: Uncovered."
        brief = _BRIEF_TEMPLATE.format(
            obpi_id="OBPI-9.9.9-99-fixture",
            parent_adr="ADR-9.9.9-fixture",
            lane="Lite",
            criteria=criteria,
        )
        exc, code, _output, _ledger = self._run(
            brief_text=brief,
            obpi_id="OBPI-9.9.9-99-fixture",
            parent_adr="ADR-9.9.9-fixture",
            lane="Lite",
            kind="foundation",
            criteria_reqs=["REQ-9.9.9-99-01"],
            covers_layout={"REQ-9.9.9-99-01": None},
            passing_predicate=lambda _qn: True,
        )
        self.assertIs(exc, SystemExit)
        self.assertEqual(code, 3)


# ---------------------------------------------------------------------------
# REQ-0.0.25-01-04 — lite-non-foundation uncovered logs warning, proceeds
# ---------------------------------------------------------------------------


class TestObpiCompleteLiteNonFoundationUncovered(_CoverageGateWireFixture):
    """REQ-0.0.25-01-04 — lite-non-foundation uncovered REQ warns, proceeds."""

    @covers("REQ-0.0.25-01-04")
    def test_lite_non_foundation_uncovered_warns_only(self) -> None:
        criteria = "- [ ] REQ-9.9.9-99-01: Uncovered."
        brief = _BRIEF_TEMPLATE.format(
            obpi_id="OBPI-9.9.9-99-fixture",
            parent_adr="ADR-9.9.9-fixture",
            lane="Lite",
            criteria=criteria,
        )
        exc, code, output, _ledger = self._run(
            brief_text=brief,
            obpi_id="OBPI-9.9.9-99-fixture",
            parent_adr="ADR-9.9.9-fixture",
            lane="Lite",
            kind="feature",
            criteria_reqs=["REQ-9.9.9-99-01"],
            covers_layout={"REQ-9.9.9-99-01": None},
            passing_predicate=lambda _qn: True,
        )
        # Lite-non-foundation: gate must not exit. Completion may proceed
        # past the gate; we assert the gate did not block + warning surfaced.
        self.assertIsNone(exc)
        joined = " ".join(output)
        self.assertIn("REQ-9.9.9-99-01", joined)
        self.assertIn("Warning", joined)


# ---------------------------------------------------------------------------
# REQ-0.0.25-01-05 — heavy with covering test that fails → exit 3
# ---------------------------------------------------------------------------


class TestObpiCompleteHeavyCoveredTestFails(_CoverageGateWireFixture):
    """REQ-0.0.25-01-05 — covering test that fails causes gate to fail closed."""

    @covers("REQ-0.0.25-01-05")
    def test_heavy_covered_test_failing_exits_3(self) -> None:
        criteria = "- [ ] REQ-9.9.9-99-01: Covered but red."
        brief = _BRIEF_TEMPLATE.format(
            obpi_id="OBPI-9.9.9-99-fixture",
            parent_adr="ADR-9.9.9-fixture",
            lane="Heavy",
            criteria=criteria,
        )
        exc, code, output, ledger = self._run(
            brief_text=brief,
            obpi_id="OBPI-9.9.9-99-fixture",
            parent_adr="ADR-9.9.9-fixture",
            lane="Heavy",
            kind="foundation",
            criteria_reqs=["REQ-9.9.9-99-01"],
            covers_layout={"REQ-9.9.9-99-01": _covering_body("REQ-9.9.9-99-01")},
            passing_predicate=lambda _qn: False,
        )
        self.assertIs(exc, SystemExit)
        self.assertEqual(code, 3)
        joined = " ".join(output)
        self.assertIn("failing-cover", joined)
        ledger.append.assert_not_called()


# ---------------------------------------------------------------------------
# REQ-0.0.25-01-06 — multiple @covers on same REQ; one passing satisfies
# ---------------------------------------------------------------------------


class TestObpiCompleteMultipleCoversOnePassing(_CoverageGateWireFixture):
    """REQ-0.0.25-01-06 — when multiple covering tests exist, one pass satisfies."""

    @covers("REQ-0.0.25-01-06")
    def test_multiple_covers_one_passes_satisfies(self) -> None:
        criteria = "- [ ] REQ-9.9.9-99-01: covered by two tests."
        brief = _BRIEF_TEMPLATE.format(
            obpi_id="OBPI-9.9.9-99-fixture",
            parent_adr="ADR-9.9.9-fixture",
            lane="Heavy",
            criteria=criteria,
        )
        # One test passes (test_alpha) and one fails (test_beta) — gate
        # must accept the REQ as satisfied.
        exc, code, _output, _ledger = self._run(
            brief_text=brief,
            obpi_id="OBPI-9.9.9-99-fixture",
            parent_adr="ADR-9.9.9-fixture",
            lane="Heavy",
            kind="foundation",
            criteria_reqs=["REQ-9.9.9-99-01"],
            covers_layout={"REQ-9.9.9-99-01": _multi_covering_body("REQ-9.9.9-99-01")},
            passing_predicate=lambda qn: qn.endswith(".test_alpha"),
        )
        self.assertIsNone(exc)
        self.assertIsNone(code)


# ---------------------------------------------------------------------------
# OBPI-0.0.25-02 override tests — extend the fixture rig with accept_uncovered
# ---------------------------------------------------------------------------


class _OverrideGateWireFixture(_CoverageGateWireFixture):
    """Extends ``_CoverageGateWireFixture`` with ``--accept-uncovered`` params.

    ``tty_present`` controls the mock outcome for
    ``_enforce_uncovered_acceptance_confirmation``:
    - True → returns ``"human"``
    - False → raises ``GzCliError("headless — no TTY")``
    """

    def _run_override(
        self,
        *,
        brief_text: str,
        obpi_id: str,
        parent_adr: str,
        lane: str,
        kind: str,
        criteria_reqs: list[str],
        covers_layout: dict[str, str | None],
        passing_predicate,
        accept_uncovered: list[str] | None = None,
        accept_uncovered_reason: list[str] | None = None,
        tty_present: bool = True,
    ) -> tuple[type[BaseException] | None, int | None, list[str], MagicMock]:
        from gzkit.commands.common import GzCliError

        recorded: list[str] = []
        rec_console = Console(file=StringIO(), record=True)
        original_print = rec_console.print

        def _capture(*args, **kwargs):
            recorded.append(" ".join(str(a) for a in args))
            return original_print(*args, **kwargs)

        rec_console.print = _capture  # ty: ignore[invalid-assignment]

        def _mock_enforce_uncovered(*args, **kwargs):
            if tty_present:
                return "human"
            raise GzCliError("headless — no TTY and no pipeline marker")

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            obpi_file = root / "brief.md"
            obpi_file.write_text(brief_text, encoding="utf-8")

            adr_file = root / "adr.md"
            adr_file.write_text(
                f"---\nid: {parent_adr}\nlane: {lane}\nkind: {kind}\n---\n# {parent_adr}\n",
                encoding="utf-8",
            )

            tests_root = root / "tests"
            tests_root.mkdir(parents=True, exist_ok=True)
            for req_id, body in covers_layout.items():
                if body is None:
                    continue
                fname = f"test_cov_{req_id.replace('.', '_').replace('-', '_')}.py"
                (tests_root / fname).write_text(body, encoding="utf-8")

            ledger_obj = _mock_ledger(obpi_id, parent_adr, lane)

            patches = [
                patch("gzkit.commands.obpi_complete.console", rec_console),
                patch("gzkit.commands.obpi_complete.get_project_root", return_value=root),
                patch(
                    "gzkit.commands.obpi_complete.ensure_initialized",
                    return_value=_mock_config(mode=lane.lower()),
                ),
                patch(
                    "gzkit.commands.obpi_complete.resolve_obpi_file",
                    return_value=(obpi_file, obpi_id),
                ),
                patch("gzkit.commands.obpi_complete.Ledger", return_value=ledger_obj),
                patch(
                    "gzkit.commands.obpi_complete.resolve_adr_file",
                    return_value=(adr_file, parent_adr),
                ),
                patch(
                    "gzkit.commands.obpi_complete.capture_validation_anchor",
                    return_value=EventAnchor(commit="abc1234", semver="0.0.25"),
                ),
                patch(
                    "gzkit.commands.obpi_complete._enforce_security_review_gate",
                    MagicMock(return_value=None),
                ),
                patch(
                    "gzkit.commands.obpi_complete._enforce_attestation_receipt_gate",
                    MagicMock(return_value=None),
                ),
                patch(
                    "gzkit.commands.obpi_complete._enforce_reconcile_receipt_gate",
                    MagicMock(return_value=None),
                ),
                patch(
                    "gzkit.commands.obpi_complete._enforce_uncovered_acceptance_confirmation",
                    side_effect=_mock_enforce_uncovered,
                ),
                patch(
                    "gzkit.commands.obpi_complete._any_covering_test_passes",
                    side_effect=lambda refs, project_root, **_kw: any(
                        passing_predicate(r.qualified_name) for r in refs
                    ),
                ),
                patch("gzkit.commands.obpi_complete.receipts_root", return_value=root),
            ]
            for p in patches:
                p.start()
            try:
                exc_type: type[BaseException] | None = None
                code: int | None = None
                try:
                    obpi_complete_cmd(
                        obpi=obpi_id,
                        attestor="g0",
                        attestation_text=(
                            "attest completed — receipts arb-step-unittest-" + ("0" * 32)
                        ),
                        implementation_summary="- Files: src/gzkit/governance/req_coverage.py",
                        key_proof="gz obpi complete fires the gate.",
                        as_json=False,
                        dry_run=False,
                        accept_uncovered=accept_uncovered,
                        accept_uncovered_reason=accept_uncovered_reason,
                    )
                except SystemExit as exc:
                    exc_type = SystemExit
                    code = int(exc.code) if isinstance(exc.code, int) else 1
            finally:
                for p in patches:
                    p.stop()

        return exc_type, code, recorded, ledger_obj


# ---------------------------------------------------------------------------
# REQ-0.0.25-02-01 — heavy lane, TTY present, single REQ waived → no exit
# ---------------------------------------------------------------------------


class TestObpiCompleteHeavyOverrideSingleReqAccepted(_OverrideGateWireFixture):
    """REQ-0.0.25-02-01 — heavy-lane single REQ waived with TTY → completion proceeds."""

    @covers("REQ-0.0.25-02-01")
    def test_heavy_single_waiver_tty_proceeds(self) -> None:
        criteria = "- [ ] REQ-9.9.9-99-01: Uncovered but waived."
        brief = _BRIEF_TEMPLATE.format(
            obpi_id="OBPI-9.9.9-99-fixture",
            parent_adr="ADR-9.9.9-fixture",
            lane="Heavy",
            criteria=criteria,
        )
        exc, code, _output, ledger = self._run_override(
            brief_text=brief,
            obpi_id="OBPI-9.9.9-99-fixture",
            parent_adr="ADR-9.9.9-fixture",
            lane="Heavy",
            kind="foundation",
            criteria_reqs=["REQ-9.9.9-99-01"],
            covers_layout={"REQ-9.9.9-99-01": None},
            passing_predicate=lambda _qn: True,
            accept_uncovered=["REQ-9.9.9-99-01"],
            accept_uncovered_reason=["operator review confirmed; waiving for release"],
            tty_present=True,
        )
        self.assertIsNone(exc)
        self.assertIsNone(code)
        # Waiver event recorded in the ledger.
        ledger.append.assert_called()
        call_args = [c.args[0] for c in ledger.append.call_args_list]
        waiver_events = [e for e in call_args if e.event == "obpi_completion_uncovered_accept"]
        self.assertEqual(len(waiver_events), 1)
        self.assertEqual(waiver_events[0].extra["req_id"], "REQ-9.9.9-99-01")


# ---------------------------------------------------------------------------
# REQ-0.0.25-02-02 — heavy lane, headless, no marker → exit 3
# ---------------------------------------------------------------------------


class TestObpiCompleteHeadlessHeavyOverrideRefused(_OverrideGateWireFixture):
    """REQ-0.0.25-02-02 — headless heavy override refused (no TTY, no marker)."""

    @covers("REQ-0.0.25-02-02")
    def test_headless_heavy_override_exits_3(self) -> None:
        criteria = "- [ ] REQ-9.9.9-99-01: Uncovered."
        brief = _BRIEF_TEMPLATE.format(
            obpi_id="OBPI-9.9.9-99-fixture",
            parent_adr="ADR-9.9.9-fixture",
            lane="Heavy",
            criteria=criteria,
        )
        exc, code, _output, _ledger = self._run_override(
            brief_text=brief,
            obpi_id="OBPI-9.9.9-99-fixture",
            parent_adr="ADR-9.9.9-fixture",
            lane="Heavy",
            kind="foundation",
            criteria_reqs=["REQ-9.9.9-99-01"],
            covers_layout={"REQ-9.9.9-99-01": None},
            passing_predicate=lambda _qn: True,
            accept_uncovered=["REQ-9.9.9-99-01"],
            accept_uncovered_reason=["a reason"],
            tty_present=False,
        )
        self.assertIs(exc, SystemExit)
        self.assertEqual(code, 3)


# ---------------------------------------------------------------------------
# REQ-0.0.25-02-03 — partial waiver: one of two uncovered REQs waived → exit 3
# ---------------------------------------------------------------------------


class TestObpiCompletePartialOverrideOneUnwaived(_OverrideGateWireFixture):
    """REQ-0.0.25-02-03 — partial waiver leaves one uncovered REQ → exit 3."""

    @covers("REQ-0.0.25-02-03")
    def test_partial_waiver_exits_3(self) -> None:
        criteria = "\n".join(
            [
                "- [ ] REQ-9.9.9-99-01: Waived.",
                "- [ ] REQ-9.9.9-99-02: Not waived.",
            ]
        )
        brief = _BRIEF_TEMPLATE.format(
            obpi_id="OBPI-9.9.9-99-fixture",
            parent_adr="ADR-9.9.9-fixture",
            lane="Heavy",
            criteria=criteria,
        )
        exc, code, _output, _ledger = self._run_override(
            brief_text=brief,
            obpi_id="OBPI-9.9.9-99-fixture",
            parent_adr="ADR-9.9.9-fixture",
            lane="Heavy",
            kind="foundation",
            criteria_reqs=["REQ-9.9.9-99-01", "REQ-9.9.9-99-02"],
            covers_layout={"REQ-9.9.9-99-01": None, "REQ-9.9.9-99-02": None},
            passing_predicate=lambda _qn: True,
            accept_uncovered=["REQ-9.9.9-99-01"],
            accept_uncovered_reason=["first is waived"],
            tty_present=True,
        )
        self.assertIs(exc, SystemExit)
        self.assertEqual(code, 3)


# ---------------------------------------------------------------------------
# REQ-0.0.25-02-05 — --accept-uncovered without matching reason → exit 1
# ---------------------------------------------------------------------------


class TestObpiCompleteOverrideEmptyRationaleExit1(_OverrideGateWireFixture):
    """REQ-0.0.25-02-05 — missing rationale for --accept-uncovered exits 1."""

    @covers("REQ-0.0.25-02-05")
    def test_accept_uncovered_no_reason_exits_1(self) -> None:
        criteria = "- [ ] REQ-9.9.9-99-01: Uncovered."
        brief = _BRIEF_TEMPLATE.format(
            obpi_id="OBPI-9.9.9-99-fixture",
            parent_adr="ADR-9.9.9-fixture",
            lane="Heavy",
            criteria=criteria,
        )
        exc, code, _output, _ledger = self._run_override(
            brief_text=brief,
            obpi_id="OBPI-9.9.9-99-fixture",
            parent_adr="ADR-9.9.9-fixture",
            lane="Heavy",
            kind="foundation",
            criteria_reqs=["REQ-9.9.9-99-01"],
            covers_layout={"REQ-9.9.9-99-01": None},
            passing_predicate=lambda _qn: True,
            accept_uncovered=["REQ-9.9.9-99-01"],
            accept_uncovered_reason=None,  # absent → exit 1
        )
        self.assertIs(exc, SystemExit)
        self.assertEqual(code, 1)


# ---------------------------------------------------------------------------
# Lite-lane override: no TTY confirmation required, ledger event recorded
# ---------------------------------------------------------------------------


class TestObpiCompleteLiteOverrideNoTtyRequired(_OverrideGateWireFixture):
    """Lite-lane (non-foundation) waiver: no TTY gate fired; ledger event recorded."""

    @covers("REQ-0.0.25-02-01")
    def test_lite_override_no_tty_proceeds(self) -> None:
        criteria = "- [ ] REQ-9.9.9-99-01: Uncovered but waived on lite."
        brief = _BRIEF_TEMPLATE.format(
            obpi_id="OBPI-9.9.9-99-fixture",
            parent_adr="ADR-9.9.9-fixture",
            lane="Lite",
            criteria=criteria,
        )
        exc, code, _output, ledger = self._run_override(
            brief_text=brief,
            obpi_id="OBPI-9.9.9-99-fixture",
            parent_adr="ADR-9.9.9-fixture",
            lane="Lite",
            kind="feature",
            criteria_reqs=["REQ-9.9.9-99-01"],
            covers_layout={"REQ-9.9.9-99-01": None},
            passing_predicate=lambda _qn: True,
            accept_uncovered=["REQ-9.9.9-99-01"],
            accept_uncovered_reason=["lite-lane waiver, no TTY needed"],
            tty_present=False,  # TTY gate is NOT called on lite-feature lane
        )
        self.assertIsNone(exc)
        self.assertIsNone(code)
        call_args = [c.args[0] for c in ledger.append.call_args_list]
        waiver_events = [e for e in call_args if e.event == "obpi_completion_uncovered_accept"]
        self.assertEqual(len(waiver_events), 1)
        self.assertEqual(waiver_events[0].extra["acceptance_type"], "lite-auto")


# ---------------------------------------------------------------------------
# Multi-REQ override: both uncovered REQs waived → no exit, two events
# ---------------------------------------------------------------------------


class TestObpiCompleteMultiReqOverrideAllWaived(_OverrideGateWireFixture):
    """REQ-0.0.25-02-01 (multi) — two uncovered REQs waived → no exit, two events."""

    @covers("REQ-0.0.25-02-01")
    def test_multi_req_all_waived_proceeds(self) -> None:
        criteria = "\n".join(
            [
                "- [ ] REQ-9.9.9-99-01: First uncovered.",
                "- [ ] REQ-9.9.9-99-02: Second uncovered.",
            ]
        )
        brief = _BRIEF_TEMPLATE.format(
            obpi_id="OBPI-9.9.9-99-fixture",
            parent_adr="ADR-9.9.9-fixture",
            lane="Heavy",
            criteria=criteria,
        )
        exc, code, _output, ledger = self._run_override(
            brief_text=brief,
            obpi_id="OBPI-9.9.9-99-fixture",
            parent_adr="ADR-9.9.9-fixture",
            lane="Heavy",
            kind="foundation",
            criteria_reqs=["REQ-9.9.9-99-01", "REQ-9.9.9-99-02"],
            covers_layout={"REQ-9.9.9-99-01": None, "REQ-9.9.9-99-02": None},
            passing_predicate=lambda _qn: True,
            accept_uncovered=["REQ-9.9.9-99-01", "REQ-9.9.9-99-02"],
            accept_uncovered_reason=["reason for first", "reason for second"],
            tty_present=True,
        )
        self.assertIsNone(exc)
        self.assertIsNone(code)
        call_args = [c.args[0] for c in ledger.append.call_args_list]
        waiver_events = [e for e in call_args if e.event == "obpi_completion_uncovered_accept"]
        self.assertEqual(len(waiver_events), 2)
        waived_reqs = {e.extra["req_id"] for e in waiver_events}
        self.assertIn("REQ-9.9.9-99-01", waived_reqs)
        self.assertIn("REQ-9.9.9-99-02", waived_reqs)


if __name__ == "__main__":
    unittest.main()
