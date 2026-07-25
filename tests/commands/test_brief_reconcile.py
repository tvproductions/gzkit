"""Tests for ``gz brief reconcile`` (OBPI-0.0.37-06).

REQ-derived behavior: the CLI wraps OBPI-05's reconciliation engine, emits
ledger events, and (under ``--apply``) writes operator-attested amendments
back into the brief. Assertions derive from the brief's Acceptance Criteria,
not from a run of the code.
"""

from __future__ import annotations

import unittest
from pathlib import Path

from gzkit.cli import main
from gzkit.config import GzkitConfig
from gzkit.ledger import Ledger
from gzkit.traceability import covers
from tests.commands.common import CliRunner, _quick_init


def _write_brief(path: Path, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")


_CLEAN_BRIEF = """\
---
id: OBPI-0.1.0-01-clean
parent: ADR-0.1.0-f
item: 1
lane: Lite
status: Draft
---

# OBPI-0.1.0-01-clean: Clean

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: the system does the clean thing

## Acceptance Criteria

- [ ] REQ-0.1.0-01-01: the system does the clean thing

**Brief Status:** Draft
"""

# Drift via an allowlist path that cannot exist on disk + an unknown gz verb.
# `Active`, not `Draft`: both of those dimensions are DELIVERABLE dimensions, and
# a Draft brief deliberately does not gate on its own deliverables (GHI #615).
# Keeping the fixture Draft would confound "does this dimension detect drift"
# with "does this lifecycle state gate on it".
_DRIFT_BRIEF = """\
---
id: OBPI-0.1.0-02-drift
parent: ADR-0.1.0-f
item: 2
lane: Lite
status: Active
---

# OBPI-0.1.0-02-drift: Drift

## Allowed Paths

- `src/gzkit/does_not_exist_zzz.py` (modify)

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: the system does the drifting thing

## Acceptance Criteria

- [ ] REQ-0.1.0-02-01: the system does the drifting thing

## Verification

```bash
gz totally-not-a-real-verb-xyz
```

**Brief Status:** Draft
"""

# Drift that `--apply` can actually repair: `src/gzkit/beta.py` is imported by
# the REQ's covering test but absent from the allowlist, so it lands in
# `allowlist_delta.missing_in_brief` — the one dimension `_compute_amendments`
# writes back. After the amendment the brief declares it, so a re-measurement
# reports no drift (GHI #677).
_REPAIRABLE_BRIEF = """\
---
id: OBPI-0.1.0-03-repairable
parent: ADR-0.1.0-f
item: 3
lane: Lite
status: Draft
---

# OBPI-0.1.0-03-repairable: Repairable

## Allowed Paths

- `src/gzkit/alpha.py` (modify)

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: the system does the repairable thing

## Acceptance Criteria

- [ ] REQ-0.1.0-03-01: the system does the repairable thing

**Brief Status:** Draft
"""

_REPAIRABLE_TEST = """\
from gzkit.beta import BETA


def test_thing() -> None:
    \"\"\"REQ-0.1.0-03-01: covering test importing a non-allowlisted sibling.\"\"\"
    assert BETA == 1
"""


def _seed_repairable_project() -> None:
    """Lay down the src/ siblings and covering test the repairable brief needs."""
    src = Path("src") / "gzkit"
    src.mkdir(parents=True, exist_ok=True)
    (src / "alpha.py").write_text("ALPHA = 1\n", encoding="utf-8")
    (src / "beta.py").write_text("BETA = 1\n", encoding="utf-8")
    tests_dir = Path("tests")
    tests_dir.mkdir(parents=True, exist_ok=True)
    (tests_dir / "test_repairable.py").write_text(_REPAIRABLE_TEST, encoding="utf-8")


class TestBriefReconcileCommand(unittest.TestCase):
    """gz brief reconcile CLI contract (OBPI-0.0.37-06)."""

    def _events(self, name: str) -> list:
        return Ledger(Path(".gzkit/ledger.jsonl")).query(event_type=name)

    def _adrs_dir(self) -> Path:
        return Path(GzkitConfig.load(Path(".gzkit.json")).paths.adrs) / "obpis"

    @covers("REQ-0.0.37-06-06")
    def test_verb_registered_help(self) -> None:
        """REQ-06: `gz brief reconcile --help` resolves (verb registered)."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            result = runner.invoke(main, ["brief", "reconcile", "--help"])
            self.assertEqual(result.exit_code, 0)
            self.assertIn("reconcile", result.output.lower())

    @covers("REQ-0.0.37-06-01")
    def test_no_drift_exits_zero_and_emits_brief_reconciled(self) -> None:
        """REQ-01: clean brief -> exit 0, brief_reconciled event (has_drift False)."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            _write_brief(self._adrs_dir() / "OBPI-0.1.0-01-clean.md", _CLEAN_BRIEF)
            result = runner.invoke(main, ["brief", "reconcile", "OBPI-0.1.0-01-clean"])
            self.assertEqual(result.exit_code, 0)
            events = self._events("brief_reconciled")
            self.assertEqual(len(events), 1)
            self.assertEqual(events[0].extra["brief_id"], "OBPI-0.1.0-01-clean")
            self.assertFalse(events[0].extra["has_drift"])
            self.assertEqual(self._events("brief_reconcile_drift_detected"), [])

    @covers("REQ-0.0.37-06-02")
    def test_drift_exits_three_and_emits_both_events(self) -> None:
        """REQ-01/02: drift brief -> exit 3, brief_reconciled + drift_detected events."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            _write_brief(self._adrs_dir() / "OBPI-0.1.0-02-drift.md", _DRIFT_BRIEF)
            result = runner.invoke(main, ["brief", "reconcile", "OBPI-0.1.0-02-drift"])
            self.assertEqual(result.exit_code, 3)
            reconciled = self._events("brief_reconciled")
            self.assertEqual(len(reconciled), 1)
            self.assertTrue(reconciled[0].extra["has_drift"])
            drift = self._events("brief_reconcile_drift_detected")
            self.assertEqual(len(drift), 1)
            self.assertIn(
                "src/gzkit/does_not_exist_zzz.py",
                drift[0].extra["allowlist_missing_on_disk"],
            )

    @covers("REQ-0.0.37-06-03")
    def test_apply_without_attestor_errors(self) -> None:
        """REQ-03: --apply without --attestor exits non-zero with guidance, emits nothing."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            _write_brief(self._adrs_dir() / "OBPI-0.1.0-02-drift.md", _DRIFT_BRIEF)
            result = runner.invoke(main, ["brief", "reconcile", "OBPI-0.1.0-02-drift", "--apply"])
            self.assertNotEqual(result.exit_code, 0)
            self.assertIn("--apply requires --attestor", result.output)
            self.assertEqual(self._events("brief_reconciled"), [])

    @covers("REQ-0.0.37-06-04")
    def test_apply_with_attestor_writes_amendment_and_records_applied(self) -> None:
        """REQ-04: --apply --attestor writes amendment + brief_reconciled applied:true."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            brief_path = self._adrs_dir() / "OBPI-0.1.0-02-drift.md"
            _write_brief(brief_path, _DRIFT_BRIEF)
            result = runner.invoke(
                main,
                [
                    "brief",
                    "reconcile",
                    "OBPI-0.1.0-02-drift",
                    "--apply",
                    "--attestor",
                    "g0",
                ],
            )
            # REQ-01 ("3 on drift") binds under --apply too: the verb drift this
            # fixture carries is recorded as a tracked defect, never repaired, so
            # drift survives the amendment and the run still fails closed (#677).
            self.assertEqual(result.exit_code, 3)
            written = brief_path.read_text(encoding="utf-8")
            self.assertIn("## Tracked Defects", written)
            self.assertIn("totally-not-a-real-verb-xyz", written)
            applied = [e for e in self._events("brief_reconciled") if e.extra.get("applied")]
            self.assertEqual(len(applied), 1)
            self.assertEqual(applied[0].extra["attestor"], "g0")

    @covers("REQ-0.0.37-06-05")
    def test_apply_dry_run_does_not_write_or_record_applied(self) -> None:
        """REQ-05: --apply --dry-run previews without writing the brief or applying."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            brief_path = self._adrs_dir() / "OBPI-0.1.0-02-drift.md"
            _write_brief(brief_path, _DRIFT_BRIEF)
            before = brief_path.read_text(encoding="utf-8")
            result = runner.invoke(
                main,
                [
                    "brief",
                    "reconcile",
                    "OBPI-0.1.0-02-drift",
                    "--apply",
                    "--attestor",
                    "g0",
                    "--dry-run",
                ],
            )
            self.assertEqual(brief_path.read_text(encoding="utf-8"), before)
            applied = [e for e in self._events("brief_reconciled") if e.extra.get("applied")]
            self.assertEqual(applied, [])
            self.assertIn("dry", result.output.lower())

    @covers("REQ-0.0.37-06-04")
    def test_apply_receipt_describes_the_amended_brief_not_the_pre_write_state(self) -> None:
        """REQ-04: the applied receipt is measured after the amendment, not before.

        A repair verb that emits a receipt computed before its own mutation
        certifies the pre-mutation world — the Stage-1 gate then blocks on drift
        the amendment already cleared (GHI #677).
        """
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            _seed_repairable_project()
            brief_path = self._adrs_dir() / "OBPI-0.1.0-03-repairable.md"
            _write_brief(brief_path, _REPAIRABLE_BRIEF)
            result = runner.invoke(
                main,
                [
                    "brief",
                    "reconcile",
                    "OBPI-0.1.0-03-repairable",
                    "--apply",
                    "--attestor",
                    "g0",
                ],
            )
            # The amendment declared the sibling, so the re-measured brief is clean.
            self.assertIn("src/gzkit/beta.py", brief_path.read_text(encoding="utf-8"))
            applied = [e for e in self._events("brief_reconciled") if e.extra.get("applied")]
            self.assertEqual(len(applied), 1)
            self.assertFalse(
                applied[0].extra["has_drift"],
                "receipt still reports the pre-amendment world",
            )
            self.assertEqual(result.exit_code, 0)

    @covers("REQ-0.0.37-06-01")
    def test_apply_with_residual_drift_still_exits_three(self) -> None:
        """REQ-01: exit 3 on drift is unconditional — --apply does not suppress it.

        `--apply` repairs only the allowlist dimension; unresolved verbs survive
        as tracked defects. A green exit over a drifted receipt tells the operator
        the gate is open when it is not (GHI #677).
        """
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            brief_path = self._adrs_dir() / "OBPI-0.1.0-02-drift.md"
            _write_brief(brief_path, _DRIFT_BRIEF)
            result = runner.invoke(
                main,
                ["brief", "reconcile", "OBPI-0.1.0-02-drift", "--apply", "--attestor", "g0"],
            )
            self.assertEqual(result.exit_code, 3)
            applied = [e for e in self._events("brief_reconciled") if e.extra.get("applied")]
            self.assertEqual(len(applied), 1)
            self.assertTrue(applied[0].extra["has_drift"])

    @covers("REQ-0.0.37-06-01")
    def test_terminal_brief_verdict_is_not_rendered_as_clean(self) -> None:
        """A sealed brief carrying deltas must not report the word `clean`.

        `has_drift` is false for a terminal brief because it cannot gate, not
        because nothing moved. Rendering that as `clean` alongside a non-zero
        delta count states the opposite of the delta line directly above it —
        the operator has to read the manpage to resolve their own CLI output
        (GHI #707 coupled-surface follow-up).
        """
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            brief_path = self._adrs_dir() / "OBPI-0.1.0-02-drift.md"
            _write_brief(brief_path, _DRIFT_BRIEF.replace("status: Active", "status: Completed"))
            result = runner.invoke(main, ["brief", "reconcile", "OBPI-0.1.0-02-drift"])
            self.assertEqual(result.exit_code, 0)
            self.assertNotIn("clean", result.output)
            self.assertIn("sealed", result.output.lower())

    @covers("REQ-0.0.37-06-01")
    def test_live_clean_brief_still_reports_clean(self) -> None:
        """Negative control: the ordinary no-drift verdict is unchanged."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            _write_brief(self._adrs_dir() / "OBPI-0.1.0-01-clean.md", _CLEAN_BRIEF)
            result = runner.invoke(main, ["brief", "reconcile", "OBPI-0.1.0-01-clean"])
            self.assertEqual(result.exit_code, 0)
            self.assertIn("clean", result.output)

    @covers("REQ-0.0.37-06-07")
    def test_new_event_types_are_registered_and_parse(self) -> None:
        """REQ-07: both event types are registered (typed union + factory round-trip)."""
        from gzkit.events import parse_typed_event
        from gzkit.ledger_events import (
            brief_reconcile_drift_detected_event,
            brief_reconciled_event,
        )

        reconciled = brief_reconciled_event(
            brief_id="OBPI-0.1.0-01",
            has_drift=True,
            allowlist_delta_count=1,
            discovery_delta_count=0,
            verification_delta_count=0,
            req_count_delta=0,
            citation_delta_count=0,
        )
        drift = brief_reconcile_drift_detected_event(
            brief_id="OBPI-0.1.0-01",
            allowlist_missing_in_brief=[],
            allowlist_missing_on_disk=["src/x.py"],
            discovery_unresolved_paths=[],
            verification_unresolved_verbs=[],
            declared_reqs=1,
            acceptance_criteria_count=1,
            req_count_delta=0,
            citation_stale=[],
        )
        # The discriminated union accepts both (registration complete, not just on disk).
        parsed_reconciled = parse_typed_event(
            {
                "event": reconciled.event,
                "id": reconciled.id,
                "ts": reconciled.ts,
                **reconciled.extra,
            }
        )
        parsed_drift = parse_typed_event(
            {"event": drift.event, "id": drift.id, "ts": drift.ts, **drift.extra}
        )
        self.assertEqual(parsed_reconciled.event, "brief_reconciled")
        self.assertEqual(parsed_drift.event, "brief_reconcile_drift_detected")

    def test_brief_not_found_errors(self) -> None:
        """Unknown OBPI id exits non-zero with a not-found message."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            result = runner.invoke(main, ["brief", "reconcile", "OBPI-9.9.9-99-missing"])
            self.assertNotEqual(result.exit_code, 0)
            self.assertIn("not found", result.output.lower())

    @covers("REQ-0.0.37-06-08")
    def test_manpage_has_required_sections(self) -> None:
        """REQ-08: the command manpage exists with the contract sections."""
        project_root = Path(__file__).resolve().parent.parent.parent
        manpage = project_root / "docs" / "user" / "manpages" / "brief-reconcile.md"
        self.assertTrue(manpage.is_file(), f"missing manpage: {manpage}")
        text = manpage.read_text(encoding="utf-8")
        for section in ("NAME", "SYNOPSIS", "DESCRIPTION", "OPTIONS", "EXAMPLES"):
            self.assertIn(f"## {section}", text, f"manpage missing required section: {section}")


if __name__ == "__main__":
    unittest.main()
