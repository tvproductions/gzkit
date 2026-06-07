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
import tempfile
import unittest
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
from gzkit.lock_manager import lock_path, write_lock
from tests.test_obpi_lock_cmd import _make_lock, _mock_config, _setup_project


def covers(target: str):  # noqa: D401
    """Identity decorator linking test to ADR/OBPI target for traceability."""

    def _identity(obj):  # type: ignore[no-untyped-def]
        return obj

    return _identity


_quiet_console = Console(file=StringIO())


@covers("OBPI-0.0.41-01")
class TokenBlockDisciplineCoverage(unittest.TestCase):
    """Sub-invariant coverage authored by OBPI-01."""

    def test_token_block_rule_file_present(self) -> None:
        """Sanity: the canonical rule file authored by OBPI-01 is on disk."""
        repo_root = Path(__file__).resolve().parents[2]
        rule_path = repo_root / ".gzkit" / "rules" / "token-block-discipline.md"
        self.assertTrue(rule_path.is_file(), f"Missing rule file: {rule_path}")


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
    def test_base_enum_matches_rule_file(self) -> None:
        """Code-side enum MUST mirror the rule's Sub-Invariant 1 closed set."""
        repo_root = Path(__file__).resolve().parents[2]
        rule_path = repo_root / ".gzkit" / "rules" / "token-block-discipline.md"
        rule_text = rule_path.read_text(encoding="utf-8")
        for category in (
            "network_loss",
            "external_blocker",
            "wrong_obpi_claimed",
            "tool_failure",
        ):
            self.assertIn(
                category,
                rule_text,
                f"Base abandon category {category!r} missing from rule file",
            )


@covers("OBPI-0.0.41-02")
class TestDegenerateHandoffWriter(unittest.TestCase):
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


@covers("OBPI-0.0.41-02")
class TestWarningOnNoHandoff(unittest.TestCase):
    """REQ-07: release without --abandon and no handoff warns (OBPI-02 staging)."""

    @covers("REQ-0.0.41-02-07")
    def test_release_without_handoff_warns_but_succeeds(self) -> None:
        """Warning to stderr; release exits 0; warning names the OBPI-03 flip."""
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
                with patch("sys.stderr", captured):
                    obpi_lock_release_cmd(
                        obpi_id="OBPI-0.0.41-02",
                        as_json=False,
                        agent="claude-code",
                    )

                stderr = captured.getvalue()
                self.assertIn("WARNING", stderr)
                self.assertIn("register entry", stderr)
                self.assertIn("gz-session-handoff", stderr)
                self.assertIn("OBPI-0.0.41-03", stderr)
                self.assertIn("fail-closed", stderr)

                # Lock removed (release succeeded, exit 0)
                self.assertFalse(lock_path(root, "OBPI-0.0.41-02").exists())


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
