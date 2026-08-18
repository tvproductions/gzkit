"""Tests for ``gz obpi brief-drift`` (OBPI-0.0.37-06).

REQ-derived behavior: the CLI wraps OBPI-05's reconciliation engine, emits
ledger events, and (under ``--apply``) writes operator-attested amendments
back into the brief. Assertions derive from the brief's Acceptance Criteria,
not from a run of the code.
"""

from __future__ import annotations

import unittest
from pathlib import Path

from gzkit.cli import main
from gzkit.commands.brief_reconcile import _append_frontmatter_list_items
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
from gzkit.traceability import covers


@covers("REQ-0.1.0-03-01")
def test_thing() -> None:
    \"\"\"Covering test importing a non-allowlisted sibling.\"\"\"
    assert BETA == 1
"""


# The structured twin of `_REPAIRABLE_BRIEF`: identical drift, but frontmatter
# declares `allowlist`/`reqs`/`verification`, so `parse_brief` returns a
# `BriefStructure` and the engine reads the allowlist from frontmatter rather
# than from the `## Allowed Paths` prose (`brief_reconcile.py` line 219). Every
# other `--apply` fixture here is legacy-shaped, which is why GHI #825 shipped.
_STRUCTURED_REPAIRABLE_BRIEF = """\
---
id: OBPI-0.1.0-04-structured
parent: ADR-0.1.0-f
item: 4
lane: Lite
status: Draft
allowlist:
- src/gzkit/alpha.py
reqs:
- REQ-0.1.0-04-01
verification:
- uv run gz lint
---

# OBPI-0.1.0-04-structured: Structured Repairable

## Allowed Paths

- `src/gzkit/alpha.py` (modify)

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: the system does the structured thing

## Acceptance Criteria

- [ ] REQ-0.1.0-04-01: the system does the structured thing

**Brief Status:** Draft
"""

_STRUCTURED_REPAIRABLE_TEST = """\
from gzkit.beta import BETA
from gzkit.traceability import covers


@covers("REQ-0.1.0-04-01")
def test_structured_thing() -> None:
    \"\"\"Covering test importing a non-allowlisted sibling.\"\"\"
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
    (tests_dir / "test_structured_repairable.py").write_text(
        _STRUCTURED_REPAIRABLE_TEST, encoding="utf-8"
    )


class TestBriefReconcileCommand(unittest.TestCase):
    """gz obpi brief-drift CLI contract (OBPI-0.0.37-06)."""

    def _events(self, name: str) -> list:
        return Ledger(Path(".gzkit/ledger.jsonl")).query(event_type=name)

    def _adrs_dir(self) -> Path:
        return Path(GzkitConfig.load(Path(".gzkit.json")).paths.adrs) / "obpis"

    @covers("REQ-0.0.37-06-06")
    def test_verb_registered_help(self) -> None:
        """REQ-06: `gz obpi brief-drift --help` resolves (verb registered)."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            result = runner.invoke(main, ["obpi", "brief-drift", "--help"])
            self.assertEqual(result.exit_code, 0)
            self.assertIn("reconcile", result.output.lower())

    @covers("REQ-0.0.37-06-01")
    def test_no_drift_exits_zero_and_emits_brief_reconciled(self) -> None:
        """REQ-01: clean brief -> exit 0, brief_reconciled event (has_drift False)."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            _write_brief(self._adrs_dir() / "OBPI-0.1.0-01-clean.md", _CLEAN_BRIEF)
            result = runner.invoke(main, ["obpi", "brief-drift", "OBPI-0.1.0-01-clean"])
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
            result = runner.invoke(main, ["obpi", "brief-drift", "OBPI-0.1.0-02-drift"])
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
            result = runner.invoke(main, ["obpi", "brief-drift", "OBPI-0.1.0-02-drift", "--apply"])
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
                    "obpi",
                    "brief-drift",
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
                    "obpi",
                    "brief-drift",
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
                    "obpi",
                    "brief-drift",
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
                ["obpi", "brief-drift", "OBPI-0.1.0-02-drift", "--apply", "--attestor", "g0"],
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
            result = runner.invoke(main, ["obpi", "brief-drift", "OBPI-0.1.0-02-drift"])
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
            result = runner.invoke(main, ["obpi", "brief-drift", "OBPI-0.1.0-01-clean"])
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
            result = runner.invoke(main, ["obpi", "brief-drift", "OBPI-9.9.9-99-missing"])
            self.assertNotEqual(result.exit_code, 0)
            self.assertIn("not found", result.output.lower())

    @covers("REQ-0.0.37-06-08")
    def test_manpage_has_required_sections(self) -> None:
        """REQ-08: the command manpage exists with the contract sections."""
        project_root = Path(__file__).resolve().parent.parent.parent
        manpage = project_root / "docs" / "user" / "manpages" / "obpi-brief-drift.md"
        self.assertTrue(manpage.is_file(), f"missing manpage: {manpage}")
        text = manpage.read_text(encoding="utf-8")
        for section in ("NAME", "SYNOPSIS", "DESCRIPTION", "OPTIONS", "EXAMPLES"):
            self.assertIn(f"## {section}", text, f"manpage missing required section: {section}")

    @covers("REQ-0.0.37-06-04")
    def test_apply_amends_the_frontmatter_allowlist_for_a_structured_brief(self) -> None:
        """REQ-04: --apply repairs the surface the engine reads, not a prose twin.

        For a `BriefStructure` brief the engine reads `parsed.allowlist` from
        frontmatter (`brief_reconcile.py` line 219); the `## Allowed Paths`
        section is an unread restatement. An amendment written only to the prose
        leaves the drift exactly as reported, so `--apply` announces success and
        the re-measurement is byte-identical to the pre-write one (GHI #825).
        """
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            _seed_repairable_project()
            brief_path = self._adrs_dir() / "OBPI-0.1.0-04-structured.md"
            _write_brief(brief_path, _STRUCTURED_REPAIRABLE_BRIEF)
            result = runner.invoke(
                main,
                [
                    "obpi",
                    "brief-drift",
                    "OBPI-0.1.0-04-structured",
                    "--apply",
                    "--attestor",
                    "g0",
                ],
            )
            written = brief_path.read_text(encoding="utf-8")
            frontmatter = written.split("\n---\n", 1)[0]
            self.assertIn(
                "src/gzkit/beta.py",
                frontmatter,
                "amendment did not reach the frontmatter allowlist the engine reads",
            )
            # The binding assertion: the drift the verb reported is actually gone.
            applied = [e for e in self._events("brief_reconciled") if e.extra.get("applied")]
            self.assertEqual(len(applied), 1)
            self.assertFalse(
                applied[0].extra["has_drift"],
                "--apply reported drift it did not clear",
            )
            self.assertEqual(result.exit_code, 0)


class TestFrontmatterListAppend(unittest.TestCase):
    """The allowlist writer joins the block it lands in (GHI #825)."""

    @covers("REQ-0.0.37-06-04")
    def test_inserted_items_match_the_existing_block_indentation(self) -> None:
        """An indented YAML list stays indented; a column-0 insert would break it.

        The inserted line must sit at the indentation of the block it joins, not
        at a fixed column — YAML rejects a list whose items disagree on depth, so
        a mismatched insert turns a repaired brief into an unparseable one.
        """
        text = "---\nallowlist:\n  - src/a.py\n  - src/b.py\nstatus: Draft\n---\n\nbody\n"
        out = _append_frontmatter_list_items(text, "allowlist", ["src/c.py"])
        self.assertIn("  - src/c.py", out)
        self.assertNotIn("\n- src/c.py", out)
        # Appended at the end of the block, not spliced into the middle of it.
        self.assertLess(out.index("  - src/b.py"), out.index("  - src/c.py"))
        self.assertLess(out.index("  - src/c.py"), out.index("status: Draft"))

    @covers("REQ-0.0.37-06-04")
    def test_flow_style_list_is_left_untouched(self) -> None:
        """A flow-style list is not rewritten — reporting drift beats writing garbage.

        `key: [a, b]` has no block to append to. Returning the text unchanged
        leaves the drift reported and fails closed at exit 3; a naive insert
        would emit a malformed brief that no longer parses at all.
        """
        text = "---\nallowlist: [src/a.py]\nstatus: Draft\n---\n\nbody\n"
        self.assertEqual(_append_frontmatter_list_items(text, "allowlist", ["src/c.py"]), text)

    @covers("REQ-0.0.37-06-04")
    def test_absent_key_is_left_untouched(self) -> None:
        """A brief with no `allowlist:` key is returned unchanged, never invented."""
        text = "---\nstatus: Draft\n---\n\nbody\n"
        self.assertEqual(_append_frontmatter_list_items(text, "allowlist", ["src/c.py"]), text)


if __name__ == "__main__":
    unittest.main()
