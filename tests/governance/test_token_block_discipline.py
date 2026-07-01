"""Token-block discipline coverage (ADR-0.0.41).

Tests assert the binding sub-invariants of `.gzkit/rules/token-block-discipline.md`:
- Sub-Invariant 1 (abandon category enum)
- Sub-Invariant 2 (register-entry minimum-information)
- Sub-Invariant 3 (reaping register-entry rule)
- Sub-Invariant 4 (TTL canon and reaping discipline)
- Sub-Invariant 5 (release fail-closed precondition)

Authored progressively across OBPI-0.0.41-02, -03, -04 per parent ADR § Evidence.
"""

from __future__ import annotations

import json
import re
import tempfile
import unittest
from datetime import UTC, datetime, timedelta
from io import StringIO
from pathlib import Path
from unittest.mock import patch

from rich.console import Console

from gzkit.commands.obpi_lock import obpi_lock_release_cmd
from gzkit.handoff_validation import (
    ABANDON_CATEGORIES,
    AbandonSpec,
    InvalidAbandonSpec,
    find_handoff_for_release,
    parse_abandon_spec,
    write_degenerate_handoff,
)
from gzkit.lock_manager import lock_path, reap_expired_locks, write_lock
from tests.commands.common import SilencedConsoleTestCase
from tests.test_obpi_lock_cmd import _make_lock, _mock_config, _setup_project


def covers(target: str):  # noqa: D401
    """Identity decorator linking test to ADR/OBPI target for traceability."""

    def _identity(obj):  # type: ignore[no-untyped-def]
        return obj

    return _identity


class _CapturingLedger:
    """Minimal ledger double (sink with ``append``) for reap tests.

    Avoids importing the real ``gzkit.ledger.Ledger`` here: this module also
    carries OBPI-0.0.41-02 tokens, and a ``gzkit.ledger`` import would drag
    ``ledger.py`` into OBPI-0.0.41-02's brief-reconcile allowlist neighborhood.
    """

    def __init__(self) -> None:
        self.events: list = []

    def append(self, event: object) -> None:
        self.events.append(event)


_quiet_console = Console(file=StringIO())


@covers("OBPI-0.0.41-01")
class TokenBlockDisciplineCoverage(unittest.TestCase):
    """Sub-invariant coverage authored by OBPI-01."""

    def test_base_categories_parse_as_valid_specs(self) -> None:
        """Each base abandon category round-trips through the production parser.

        Converted from a rule-file existence sanity check (GHI #632): asserting a
        doc is on disk is a tautology; exercising ``parse_abandon_spec`` tests the
        behavior the OBPI actually delivers.
        """
        for category in ("network_loss", "external_blocker", "wrong_obpi_claimed", "tool_failure"):
            spec = parse_abandon_spec(f"{category}:legitimate reason")
            self.assertEqual(spec.category, category)


@covers("OBPI-0.0.41-02")
class TestAbandonCategoryEnum(unittest.TestCase):
    """REQ-06: abandon category enum is closed, grounded in the rule file."""

    @covers("REQ-0.0.41-02-06")
    def test_unregistered_category_rejected(self) -> None:
        """`parse_abandon_spec` rejects categories outside the closed enum."""
        with self.assertRaises(InvalidAbandonSpec) as ctx:
            parse_abandon_spec("fabricated_category:reason")
        msg = str(ctx.exception)
        # Error message MUST enumerate the closed set so operators can recover.
        for category in ABANDON_CATEGORIES:
            self.assertIn(category, msg)

    @covers("REQ-0.0.41-02-06")
    def test_base_categories_are_members_of_closed_enum(self) -> None:
        """The four base categories are members of the production closed set.

        Converted from a rule-file text echo (GHI #632): reading the doc and
        asserting the category strings appear is a tautology; asserting membership
        in the production ``ABANDON_CATEGORIES`` tests the code-side contract that
        actually gates ``parse_abandon_spec``.
        """
        for category in (
            "network_loss",
            "external_blocker",
            "wrong_obpi_claimed",
            "tool_failure",
        ):
            self.assertIn(
                category,
                ABANDON_CATEGORIES,
                f"Base abandon category {category!r} missing from the code enum",
            )


@covers("OBPI-0.0.41-02")
class TestDegenerateHandoffWriter(SilencedConsoleTestCase):
    """REQ-05: --abandon writes a degenerate handoff under .gzkit/handoffs/."""

    @covers("REQ-0.0.41-02-05")
    def test_release_abandon_writes_degenerate_handoff_and_records_path(self) -> None:
        """Degenerate handoff carries the four minimum-info fields per Sub-Invariant 2."""
        with tempfile.TemporaryDirectory() as tmp:
            root = _setup_project(tmp)
            with (
                patch("gzkit.commands.obpi_lock.get_project_root", return_value=root),
                patch(
                    "gzkit.commands.obpi_lock.ensure_initialized",
                    return_value=_mock_config(),
                ),
                patch("gzkit.commands.obpi_lock.console", _quiet_console),
            ):
                lock = _make_lock(obpi_id="OBPI-0.0.41-02", agent="claude-code")
                write_lock(root, lock)

                obpi_lock_release_cmd(
                    obpi_id="OBPI-0.0.41-02",
                    as_json=False,
                    agent="claude-code",
                    abandon="external_blocker:downstream service offline",
                )

                handoffs = list((root / ".gzkit" / "handoffs").glob("*OBPI-0.0.41-02-abandoned.md"))
                self.assertEqual(len(handoffs), 1)

                text = handoffs[0].read_text(encoding="utf-8")
                # Frontmatter
                self.assertIn("abandoned: true", text)
                self.assertIn("category: external_blocker", text)
                self.assertIn("reason: downstream service offline", text)
                # Sub-Invariant 2 minimum-info fields
                self.assertIn("last_lock_event_timestamp:", text)
                self.assertIn("last_commit_sha:", text)
                self.assertIn("branch:", text)
                self.assertIn("## Decisions Made", text)

                # Ledger event records handoff_path (flattened to top-level)
                lines = [
                    json.loads(ln)
                    for ln in (root / ".gzkit" / "ledger.jsonl")
                    .read_text(encoding="utf-8")
                    .splitlines()
                    if ln.strip()
                ]
                released = [e for e in lines if e["event"] == "obpi_lock_released"]
                self.assertGreater(len(released), 0)
                self.assertIn("handoff_path", released[-1])
                self.assertTrue(
                    released[-1]["handoff_path"].endswith("OBPI-0.0.41-02-abandoned.md")
                )

    @covers("REQ-0.0.41-02-06")
    def test_release_abandon_rejects_unregistered_category(self) -> None:
        """`--abandon <unknown>:<reason>` exits 1 BEFORE the lock is touched."""
        with tempfile.TemporaryDirectory() as tmp:
            root = _setup_project(tmp)
            with (
                patch("gzkit.commands.obpi_lock.get_project_root", return_value=root),
                patch(
                    "gzkit.commands.obpi_lock.ensure_initialized",
                    return_value=_mock_config(),
                ),
                patch("gzkit.commands.obpi_lock.console", _quiet_console),
            ):
                lock = _make_lock(obpi_id="OBPI-0.0.41-02", agent="claude-code")
                write_lock(root, lock)

                with self.assertRaises(SystemExit) as ctx:
                    obpi_lock_release_cmd(
                        obpi_id="OBPI-0.0.41-02",
                        as_json=False,
                        agent="claude-code",
                        abandon="fabricated:reason",
                    )
                self.assertEqual(ctx.exception.code, 1)
                # Lock file MUST still exist (fail-closed before mutation)
                self.assertTrue(lock_path(root, "OBPI-0.0.41-02").exists())


@covers("OBPI-0.0.41-03")
class TestFailClosedOnNoHandoff(unittest.TestCase):
    """REQ-03-01: release without --abandon and no handoff fails-closed (OBPI-03 flip)."""

    @covers("REQ-0.0.41-03-01")
    def test_release_fail_closed_without_handoff_or_abandon(self) -> None:
        """Exit 3; lock survives; stderr names gz-session-handoff and --abandon."""
        with tempfile.TemporaryDirectory() as tmp:
            root = _setup_project(tmp)
            with (
                patch("gzkit.commands.obpi_lock.get_project_root", return_value=root),
                patch(
                    "gzkit.commands.obpi_lock.ensure_initialized",
                    return_value=_mock_config(),
                ),
                patch("gzkit.commands.obpi_lock.console", _quiet_console),
            ):
                lock = _make_lock(obpi_id="OBPI-0.0.41-02", agent="claude-code")
                write_lock(root, lock)

                captured = StringIO()
                with patch("sys.stderr", captured), self.assertRaises(SystemExit) as ctx:
                    obpi_lock_release_cmd(
                        obpi_id="OBPI-0.0.41-02",
                        as_json=False,
                        agent="claude-code",
                    )

                self.assertEqual(ctx.exception.code, 3)
                stderr = captured.getvalue()
                self.assertIn("gz-session-handoff", stderr)
                self.assertIn("--abandon", stderr)

                # Lock survives — fail-closed before delete
                self.assertTrue(lock_path(root, "OBPI-0.0.41-02").exists())


@covers("OBPI-0.0.41-03")
class TestReapFailsClosed(unittest.TestCase):
    """REQ-03-04: reaping is fail-closed when the register-entry write fails."""

    @covers("REQ-0.0.41-03-04")
    def test_reap_fails_closed_when_handoff_write_fails(self) -> None:
        """Handoff write OSError → lock survives, no event, not in reaped list."""
        with tempfile.TemporaryDirectory() as tmp:
            root = _setup_project(tmp)
            old_time = (datetime.now(UTC) - timedelta(minutes=200)).isoformat()
            write_lock(
                root,
                _make_lock(obpi_id="OBPI-0.0.41-03", claimed_at=old_time, ttl_minutes=120),
            )

            ledger = _CapturingLedger()

            with patch(
                "gzkit.lock_manager._write_reaping_handoff",
                side_effect=OSError("simulated handoff write failure"),
            ):
                reaped = reap_expired_locks(root, ledger=ledger, reaper_agent="reaper-b")

            # Ordering invariant: no handoff → no delete, no event, not reaped.
            self.assertEqual(reaped, [])
            self.assertTrue(lock_path(root, "OBPI-0.0.41-03").exists())
            self.assertEqual(
                [e for e in ledger.events if e.event == "obpi_lock_released"],
                [],
            )


@covers("OBPI-0.0.41-03")
class TestNoAdrPackageHandoffWrites(unittest.TestCase):
    """REQ-03-05: every handoff-dir write under src/ is rooted at .gzkit/handoffs/."""

    @covers("REQ-0.0.41-03-05")
    def test_no_adr_package_handoff_writes(self) -> None:
        """Static fence: no code path constructs a handoffs dir outside .gzkit."""
        repo_root = Path(__file__).resolve().parents[2]
        src = repo_root / "src" / "gzkit"
        # Matches a Path join onto a "handoffs" segment, e.g. `pkg / "handoffs"`.
        join_handoffs = re.compile(r"""/\s*["']handoffs["']""")
        offenders: list[str] = []
        for py in src.rglob("*.py"):
            for lineno, line in enumerate(py.read_text(encoding="utf-8").splitlines(), start=1):
                if join_handoffs.search(line) and ".gzkit" not in line:
                    offenders.append(f"{py.relative_to(repo_root)}:{lineno}: {line.strip()}")
        self.assertEqual(
            offenders,
            [],
            "handoff-dir writes MUST target .gzkit/handoffs/, never an ADR "
            "package: " + "; ".join(offenders),
        )


@covers("OBPI-0.0.41-02")
class TestFindHandoffForRelease(unittest.TestCase):
    """Companion: find_handoff_for_release helper used by release path."""

    def test_returns_none_when_no_handoffs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            result = find_handoff_for_release(root, obpi_id="OBPI-0.0.41-02")
            self.assertIsNone(result)

    def test_returns_none_for_abandoned_handoff(self) -> None:
        """Abandoned handoffs don't satisfy the normal-release pairing."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            spec = AbandonSpec(category="network_loss", reason="example")
            written = write_degenerate_handoff(
                root,
                obpi_id="OBPI-0.0.41-02",
                adr_id="ADR-0.0.41",
                agent="claude-code",
                spec=spec,
                last_claim_timestamp="2026-06-07T10:00:00Z",
                commit_sha="abc1234",
                branch="main",
            )
            self.assertTrue(written.exists())
            # Abandoned handoffs don't count as register-entry pairing for
            # normal release (they pair only with --abandon code path).
            result = find_handoff_for_release(root, obpi_id="OBPI-0.0.41-02")
            self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
