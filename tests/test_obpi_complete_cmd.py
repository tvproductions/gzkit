"""Tests for gz obpi complete — atomic OBPI completion transaction."""

from __future__ import annotations

import json
import tempfile
import unittest
from io import StringIO
from pathlib import Path
from unittest.mock import MagicMock, patch

from rich.console import Console

from gzkit.commands.obpi_complete import (
    _append_audit_ledger,
    _build_attestation_audit_entry,
    _build_completed_brief,
    _has_substantive_implementation_summary,
    _has_substantive_key_proof,
    _is_placeholder,
    _read_existing_key_proof,
    _read_existing_summary,
    _replace_h3_section,
    _rollback_audit_ledger,
    _update_human_attestation,
    _validate_would_be_content,
    obpi_complete_cmd,
)
from gzkit.events import EventAnchor


def covers(target: str):  # noqa: D401
    """Identity decorator linking test to ADR/OBPI target for traceability."""

    def _identity(obj):  # type: ignore[no-untyped-def]
        return obj

    return _identity


# ---------------------------------------------------------------------------
# Shared quiet console — suppresses Rich output during command tests
# ---------------------------------------------------------------------------

_quiet_console = Console(file=StringIO())


# ---------------------------------------------------------------------------
# Minimal OBPI brief templates
# ---------------------------------------------------------------------------

_MINIMAL_BRIEF = """\
---
id: OBPI-0.0.14-02-obpi-complete-command
parent: ADR-0.0.14-deterministic-obpi-commands
item: 2
lane: Heavy
status: Draft
---

# OBPI-0.0.14-02: gz obpi complete command

## Objective

Test brief for obpi complete command.

## Allowed Paths

- `src/gzkit/commands/obpi_complete.py`
- `tests/test_obpi_complete_cmd.py`

## Requirements (FAIL-CLOSED)

1. Must validate brief exists

## Acceptance Criteria

- [ ] REQ-0.0.14-02-01: Brief must exist

## Evidence

### Implementation Summary

- Files created/modified:
- Tests added:
- Date completed:
- Attestation status:
- Defects noted:

### Key Proof

<!-- One concrete usage example, command, or before/after behavior. -->

## Human Attestation

- Attestor: `<name>` when required, otherwise `n/a`
- Attestation: substantive attestation text or `n/a`
- Date: YYYY-MM-DD or `n/a`

---

**Brief Status:** Draft

**Date Completed:** -

**Evidence Hash:** -
"""

_COMPLETED_BRIEF = _MINIMAL_BRIEF.replace("status: Draft", "status: Completed").replace(
    "**Brief Status:** Draft", "**Brief Status:** Completed"
)


# ---------------------------------------------------------------------------
# 1. Unit tests for helper functions
# ---------------------------------------------------------------------------


@covers("OBPI-0.0.14-02")
class TestIsPlaceholder(unittest.TestCase):
    """Tests for _is_placeholder detection."""

    @covers("REQ-0.0.14-02-02")
    def test_empty_is_placeholder(self):
        self.assertTrue(_is_placeholder(""))
        self.assertTrue(_is_placeholder("   "))

    @covers("REQ-0.0.14-02-02")
    def test_known_placeholders(self):
        for p in ("tbd", "TBD", "...", "-", "none", "(none)"):
            self.assertTrue(_is_placeholder(p), msg=f"Expected placeholder: {p}")

    @covers("REQ-0.0.14-02-02")
    def test_real_content_is_not_placeholder(self):
        self.assertFalse(_is_placeholder("Implemented claim/release/check/list"))

    @covers("REQ-0.0.14-02-02")
    def test_template_bullet_is_placeholder(self):
        self.assertTrue(_is_placeholder("- Files created/modified: "))


@covers("OBPI-0.0.14-02")
class TestReadExistingSummary(unittest.TestCase):
    """Tests for _read_existing_summary."""

    @covers("REQ-0.0.14-02-02")
    def test_returns_none_when_only_placeholders(self):
        self.assertIsNone(_read_existing_summary(_MINIMAL_BRIEF))

    @covers("REQ-0.0.14-02-02")
    def test_returns_content_when_substantive(self):
        brief = _MINIMAL_BRIEF.replace(
            "- Files created/modified:",
            "- Files created/modified: src/gzkit/commands/obpi_complete.py",
        )
        result = _read_existing_summary(brief)
        self.assertIsNotNone(result)
        self.assertIn("obpi_complete.py", result)


@covers("OBPI-0.0.14-02")
class TestReadExistingKeyProof(unittest.TestCase):
    """Tests for _read_existing_key_proof."""

    @covers("REQ-0.0.14-02-02")
    def test_returns_none_for_html_comment_placeholder(self):
        self.assertIsNone(_read_existing_key_proof(_MINIMAL_BRIEF))

    @covers("REQ-0.0.14-02-02")
    def test_returns_content_when_substantive(self):
        brief = _MINIMAL_BRIEF.replace(
            "<!-- One concrete usage example, command, or before/after behavior. -->",
            "gz obpi complete OBPI-0.0.14-01 --attestor jeff exits 0",
        )
        result = _read_existing_key_proof(brief)
        self.assertIsNotNone(result)


@covers("OBPI-0.0.14-02")
class TestReplaceH3Section(unittest.TestCase):
    """Tests for _replace_h3_section."""

    @covers("REQ-0.0.14-02-03")
    def test_replaces_section_body(self):
        content = "### Summary\n\nOld body\n\n### Next\n\nOther"
        result = _replace_h3_section(content, "Summary", "New body here")
        self.assertIn("New body here", result)
        self.assertNotIn("Old body", result)
        self.assertIn("### Next", result)

    @covers("REQ-0.0.14-02-03")
    def test_preserves_heading(self):
        content = "### Summary\n\nOld body\n\n### Next\n"
        result = _replace_h3_section(content, "Summary", "New body")
        self.assertIn("### Summary", result)


@covers("OBPI-0.0.14-02")
class TestUpdateHumanAttestation(unittest.TestCase):
    """Tests for _update_human_attestation."""

    @covers("REQ-0.0.14-02-08")
    def test_updates_attestor_and_text(self):
        content = (
            "## Human Attestation\n\n- Attestor: `<name>`\n- Attestation: n/a\n- Date: YYYY-MM-DD\n"
        )
        result = _update_human_attestation(content, "jeff", "Lock commands verified", "2026-04-05")
        self.assertIn("- Attestor: `jeff`", result)
        self.assertIn("- Attestation: Lock commands verified", result)
        self.assertIn("- Date: 2026-04-05", result)


@covers("OBPI-0.0.14-02")
class TestBuildCompletedBrief(unittest.TestCase):
    """Tests for _build_completed_brief."""

    @covers("REQ-0.0.14-02-04")
    def test_sets_frontmatter_status(self):
        result = _build_completed_brief(
            content=_MINIMAL_BRIEF,
            attestor="jeff",
            attestation_text="Verified",
            implementation_summary="- Files: obpi_complete.py\n- Tests: 5 added",
            key_proof="gz obpi complete exits 0",
            date_completed="2026-04-05",
        )
        self.assertIn("status: Completed", result)

    @covers("REQ-0.0.14-02-04")
    def test_sets_brief_status_line(self):
        result = _build_completed_brief(
            content=_MINIMAL_BRIEF,
            attestor="jeff",
            attestation_text="Verified",
            implementation_summary="- Files: obpi_complete.py",
            key_proof="gz obpi complete exits 0",
            date_completed="2026-04-05",
        )
        self.assertIn("**Brief Status:** Completed", result)
        self.assertIn("**Date Completed:** 2026-04-05", result)

    @covers("REQ-0.0.14-02-03")
    def test_updates_human_attestation(self):
        result = _build_completed_brief(
            content=_MINIMAL_BRIEF,
            attestor="jeff",
            attestation_text="All lock commands verified",
            implementation_summary="- Files: obpi_complete.py",
            key_proof="gz obpi complete exits 0",
            date_completed="2026-04-05",
        )
        self.assertIn("- Attestor: `jeff`", result)
        self.assertIn("- Attestation: All lock commands verified", result)


# ---------------------------------------------------------------------------
# 2. Validation tests
# ---------------------------------------------------------------------------


@covers("OBPI-0.0.14-02")
class TestValidateWouldBeContent(unittest.TestCase):
    """Tests for _validate_would_be_content."""

    def _completed_content(self) -> str:
        return _build_completed_brief(
            content=_MINIMAL_BRIEF,
            attestor="jeff",
            attestation_text="Verified",
            implementation_summary="- Files: obpi_complete.py\n- Tests: 5 added",
            key_proof="gz obpi complete exits 0",
            date_completed="2026-04-05",
        )

    @covers("REQ-0.0.14-02-02")
    def test_valid_content_passes(self):
        content = self._completed_content()
        errors = _validate_would_be_content(content, requires_human=True)
        self.assertEqual(errors, [])

    @covers("REQ-0.0.14-02-02")
    def test_template_content_fails_summary_and_proof(self):
        errors = _validate_would_be_content(_MINIMAL_BRIEF, requires_human=False)
        self.assertTrue(any("Implementation Summary" in e for e in errors))
        self.assertTrue(any("Key Proof" in e for e in errors))

    @covers("REQ-0.0.14-02-02")
    def test_human_attestation_required_but_missing(self):
        # Content with good summary and proof but no attestation
        content = _build_completed_brief(
            content=_MINIMAL_BRIEF,
            attestor="<name>",
            attestation_text="n/a",
            implementation_summary="- Files: obpi_complete.py",
            key_proof="gz obpi complete exits 0",
            date_completed="2026-04-05",
        )
        errors = _validate_would_be_content(content, requires_human=True)
        self.assertTrue(any("attestation" in e.lower() for e in errors))

    @covers("REQ-0.0.14-02-02")
    def test_human_attestation_placeholder_date_rejected(self):
        """GHI-126: placeholder date like _(pending)_ must be rejected."""
        content = _build_completed_brief(
            content=_MINIMAL_BRIEF,
            attestor="jeff",
            attestation_text="attest completed",
            implementation_summary="- Files: obpi_complete.py",
            key_proof="gz obpi complete exits 0",
            date_completed="_(pending)_",
        )
        errors = _validate_would_be_content(content, requires_human=True)
        self.assertTrue(any("attestation" in e.lower() for e in errors))

    @covers("REQ-0.0.14-02-02")
    def test_human_attestation_missing_attestation_text_rejected(self):
        """GHI-126: missing Attestation line must be rejected."""
        content = _build_completed_brief(
            content=_MINIMAL_BRIEF,
            attestor="jeff",
            attestation_text="n/a",
            implementation_summary="- Files: obpi_complete.py",
            key_proof="gz obpi complete exits 0",
            date_completed="2026-04-05",
        )
        errors = _validate_would_be_content(content, requires_human=True)
        self.assertTrue(any("attestation" in e.lower() for e in errors))


@covers("OBPI-0.0.14-02")
class TestSubstantiveChecks(unittest.TestCase):
    """Tests for _has_substantive_implementation_summary and _has_substantive_key_proof."""

    @covers("REQ-0.0.14-02-02")
    def test_placeholder_summary_not_substantive(self):
        # Template bullets like "- Files created/modified:" with no values
        # are captured as fallback bullets with text like "Files created/modified:".
        # The _is_placeholder regex catches the full-line variant but the hook
        # captures the VALUE part after "- ".  Template label-only bullets
        # have empty values in the primary regex, but fallback bullets match.
        # The primary regex (- Key: value) yields no matches for template lines
        # because they have no value after the colon.  The fallback captures
        # the label text which is NOT in _PLACEHOLDERS.
        # However, with no H3/H2 boundary issues, the section body is now
        # correctly bounded and template lines are correctly identified.
        self.assertFalse(_has_substantive_implementation_summary(_MINIMAL_BRIEF))

    @covers("REQ-0.0.14-02-02")
    def test_real_summary_is_substantive(self):
        brief = _MINIMAL_BRIEF.replace(
            "- Files created/modified:",
            "- Files created/modified: obpi_complete.py, parser_artifacts.py",
        )
        self.assertTrue(_has_substantive_implementation_summary(brief))

    @covers("REQ-0.0.14-02-02")
    def test_placeholder_key_proof_not_substantive(self):
        # HTML comment is a placeholder
        self.assertFalse(_has_substantive_key_proof(_MINIMAL_BRIEF))

    @covers("REQ-0.0.14-02-02")
    def test_real_key_proof_is_substantive(self):
        brief = _MINIMAL_BRIEF.replace(
            "<!-- One concrete usage example, command, or before/after behavior. -->",
            "gz obpi complete OBPI-0.0.14-01 --attestor jeff exits 0",
        )
        self.assertTrue(_has_substantive_key_proof(brief))


# ---------------------------------------------------------------------------
# 3. Audit ledger tests
# ---------------------------------------------------------------------------


@covers("OBPI-0.0.14-02")
class TestAuditLedger(unittest.TestCase):
    """Tests for audit ledger append and rollback."""

    @covers("REQ-0.0.14-02-05")
    def test_append_creates_entry(self):
        with tempfile.TemporaryDirectory() as tmp:
            adr_dir = Path(tmp) / "adr"
            adr_dir.mkdir()
            entry = _build_attestation_audit_entry(
                obpi_id="OBPI-0.0.14-02",
                adr_id="ADR-0.0.14",
                attestor="jeff",
                attestation_text="Verified",
                date="2026-04-05",
                requires_human=True,
            )
            _append_audit_ledger(adr_dir, entry)

            ledger_file = adr_dir / "logs" / "obpi-audit.jsonl"
            self.assertTrue(ledger_file.exists())
            lines = ledger_file.read_text(encoding="utf-8").strip().splitlines()
            self.assertEqual(len(lines), 1)
            parsed = json.loads(lines[0])
            self.assertEqual(parsed["type"], "obpi-audit")
            self.assertEqual(parsed["attestation_type"], "human")

    @covers("REQ-0.0.14-02-07")
    def test_rollback_removes_last_entry(self):
        with tempfile.TemporaryDirectory() as tmp:
            adr_dir = Path(tmp) / "adr"
            adr_dir.mkdir()
            entry1 = {"type": "obpi-audit", "obpi_id": "first"}
            entry2 = {"type": "obpi-audit", "obpi_id": "second"}
            _append_audit_ledger(adr_dir, entry1)
            _append_audit_ledger(adr_dir, entry2)

            ledger_file = adr_dir / "logs" / "obpi-audit.jsonl"
            _rollback_audit_ledger(ledger_file)

            lines = ledger_file.read_text(encoding="utf-8").strip().splitlines()
            self.assertEqual(len(lines), 1)
            self.assertEqual(json.loads(lines[0])["obpi_id"], "first")

    @covers("REQ-0.0.14-02-07")
    def test_rollback_empty_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            ledger_file = Path(tmp) / "obpi-audit.jsonl"
            ledger_file.write_text('{"test":"entry"}\n', encoding="utf-8")
            _rollback_audit_ledger(ledger_file)
            content = ledger_file.read_text(encoding="utf-8")
            self.assertEqual(content, "")


@covers("OBPI-0.0.14-02")
class TestBuildAttestationEntry(unittest.TestCase):
    """Tests for _build_attestation_audit_entry."""

    @covers("REQ-0.0.14-02-05")
    def test_human_attestation_entry(self):
        entry = _build_attestation_audit_entry(
            obpi_id="OBPI-0.0.14-02",
            adr_id="ADR-0.0.14",
            attestor="jeff",
            attestation_text="Lock commands verified",
            date="2026-04-05",
            requires_human=True,
        )
        self.assertEqual(entry["type"], "obpi-audit")
        self.assertEqual(entry["attestation_type"], "human")
        self.assertTrue(entry["evidence"]["human_attestation"])
        self.assertEqual(entry["evidence"]["attestation_text"], "Lock commands verified")
        self.assertEqual(entry["action_taken"], "attestation_recorded")

    @covers("REQ-0.0.14-02-05")
    def test_self_close_entry(self):
        entry = _build_attestation_audit_entry(
            obpi_id="OBPI-0.1.0-01",
            adr_id="ADR-0.1.0",
            attestor="agent:pipeline",
            attestation_text="Auto-completed",
            date="2026-04-05",
            requires_human=False,
        )
        self.assertEqual(entry["attestation_type"], "self-close-exception")
        self.assertFalse(entry["evidence"]["human_attestation"])


# ---------------------------------------------------------------------------
# 4. Integration-style command tests (mocked dependencies)
# ---------------------------------------------------------------------------


def _mock_config():
    """Build a mock GzkitConfig for command tests."""
    config = MagicMock()
    config.mode = "heavy"
    config.paths.ledger = ".gzkit/ledger.jsonl"
    return config


def _mock_ledger(obpi_id: str, parent_adr: str, *, completed: bool = False):
    """Build a mock Ledger instance."""
    ledger = MagicMock()
    ledger.canonicalize_id.return_value = obpi_id
    graph = {
        obpi_id: {
            "type": "obpi",
            "parent": parent_adr,
            "ledger_completed": completed,
        },
        parent_adr: {
            "type": "adr",
            "lane": "heavy",
        },
    }
    ledger.get_artifact_graph.return_value = graph
    return ledger


@covers("OBPI-0.0.14-02")
class TestObpiCompleteCmdBriefNotFound(unittest.TestCase):
    """Test that command exits 1 when brief file doesn't exist."""

    @patch("gzkit.commands.obpi_complete.console", _quiet_console)
    @patch("gzkit.commands.obpi_complete.get_project_root")
    @patch("gzkit.commands.obpi_complete.ensure_initialized")
    @patch("gzkit.commands.obpi_complete.resolve_obpi_file")
    @patch("gzkit.commands.obpi_complete.Ledger")
    @covers("REQ-0.0.14-02-01")
    def test_exits_1_for_missing_brief(self, mock_ledger_cls, mock_resolve, mock_init, mock_root):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            mock_root.return_value = root
            mock_init.return_value = _mock_config()

            obpi_file = root / "nonexistent.md"
            mock_resolve.return_value = (obpi_file, "OBPI-0.0.14-02")
            mock_ledger_cls.return_value = _mock_ledger("OBPI-0.0.14-02", "ADR-0.0.14")

            with self.assertRaises(SystemExit) as ctx:
                obpi_complete_cmd(
                    obpi="OBPI-0.0.14-02",
                    attestor="jeff",
                    attestation_text="Verified",
                    implementation_summary="- Files: test.py",
                    key_proof="exits 0",
                    as_json=False,
                    dry_run=False,
                )
            self.assertEqual(ctx.exception.code, 1)


@covers("OBPI-0.0.14-02")
class TestObpiCompleteCmdAlreadyCompleted(unittest.TestCase):
    """Test that command exits 1 when brief is already Completed."""

    @patch("gzkit.commands.obpi_complete.console", _quiet_console)
    @patch("gzkit.commands.obpi_complete.get_project_root")
    @patch("gzkit.commands.obpi_complete.ensure_initialized")
    @patch("gzkit.commands.obpi_complete.resolve_obpi_file")
    @patch("gzkit.commands.obpi_complete.Ledger")
    @covers("REQ-0.0.14-02-01")
    def test_exits_1_for_already_completed(
        self, mock_ledger_cls, mock_resolve, mock_init, mock_root
    ):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            mock_root.return_value = root
            mock_init.return_value = _mock_config()

            obpi_file = root / "brief.md"
            obpi_file.write_text(_COMPLETED_BRIEF, encoding="utf-8")
            mock_resolve.return_value = (obpi_file, "OBPI-0.0.14-02")
            mock_ledger_cls.return_value = _mock_ledger("OBPI-0.0.14-02", "ADR-0.0.14")

            with self.assertRaises(SystemExit) as ctx:
                obpi_complete_cmd(
                    obpi="OBPI-0.0.14-02",
                    attestor="jeff",
                    attestation_text="Verified",
                    implementation_summary="- Files: test.py",
                    key_proof="exits 0",
                    as_json=False,
                    dry_run=False,
                )
            self.assertEqual(ctx.exception.code, 1)


@covers("OBPI-0.0.14-02")
class TestObpiCompleteCmdDryRun(unittest.TestCase):
    """Test that --dry-run produces output without writing files."""

    @patch("gzkit.commands.obpi_complete.console", _quiet_console)
    @patch("gzkit.commands.obpi_complete.capture_validation_anchor")
    @patch("gzkit.commands.obpi_complete._requires_human_obpi_attestation")
    @patch("gzkit.commands.obpi_complete.resolve_adr_file")
    @patch("gzkit.commands.obpi_complete.get_project_root")
    @patch("gzkit.commands.obpi_complete.ensure_initialized")
    @patch("gzkit.commands.obpi_complete.resolve_obpi_file")
    @patch("gzkit.commands.obpi_complete.Ledger")
    @covers("REQ-0.0.14-02-07")
    def test_dry_run_no_writes(
        self,
        mock_ledger_cls,
        mock_resolve,
        mock_init,
        mock_root,
        mock_adr_resolve,
        mock_requires_human,
        mock_anchor,
    ):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            mock_root.return_value = root
            mock_init.return_value = _mock_config()
            mock_requires_human.return_value = False
            mock_anchor.return_value = EventAnchor(commit="abc1234", semver="0.0.14")

            obpi_file = root / "brief.md"
            obpi_file.write_text(_MINIMAL_BRIEF, encoding="utf-8")
            mock_resolve.return_value = (obpi_file, "OBPI-0.0.14-02")

            ledger = _mock_ledger("OBPI-0.0.14-02", "ADR-0.0.14")
            mock_ledger_cls.return_value = ledger
            mock_adr_resolve.return_value = (root / "adr.md", "ADR-0.0.14")

            obpi_complete_cmd(
                obpi="OBPI-0.0.14-02",
                attestor="jeff",
                attestation_text="Verified",
                implementation_summary="- Files: obpi_complete.py",
                key_proof="gz obpi complete exits 0",
                as_json=False,
                dry_run=True,
            )

            # Brief should be unchanged
            self.assertEqual(obpi_file.read_text(encoding="utf-8"), _MINIMAL_BRIEF)
            # Ledger append should not have been called
            ledger.append.assert_not_called()


@covers("OBPI-0.0.14-02")
class TestObpiCompleteCmdJsonOutput(unittest.TestCase):
    """Test that --json output is valid JSON."""

    @patch("gzkit.commands.obpi_complete.console", _quiet_console)
    @patch("gzkit.commands.obpi_complete.capture_validation_anchor")
    @patch("gzkit.commands.obpi_complete._requires_human_obpi_attestation")
    @patch("gzkit.commands.obpi_complete.resolve_adr_file")
    @patch("gzkit.commands.obpi_complete.get_project_root")
    @patch("gzkit.commands.obpi_complete.ensure_initialized")
    @patch("gzkit.commands.obpi_complete.resolve_obpi_file")
    @patch("gzkit.commands.obpi_complete.Ledger")
    @covers("REQ-0.0.14-02-09")
    def test_json_dry_run_output(
        self,
        mock_ledger_cls,
        mock_resolve,
        mock_init,
        mock_root,
        mock_adr_resolve,
        mock_requires_human,
        mock_anchor,
    ):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            mock_root.return_value = root
            mock_init.return_value = _mock_config()
            mock_requires_human.return_value = False
            mock_anchor.return_value = EventAnchor(commit="abc1234", semver="0.0.14")

            obpi_file = root / "brief.md"
            obpi_file.write_text(_MINIMAL_BRIEF, encoding="utf-8")
            mock_resolve.return_value = (obpi_file, "OBPI-0.0.14-02")

            ledger = _mock_ledger("OBPI-0.0.14-02", "ADR-0.0.14")
            mock_ledger_cls.return_value = ledger
            mock_adr_resolve.return_value = (root / "adr.md", "ADR-0.0.14")

            # Capture stdout
            import io
            import sys

            captured = io.StringIO()
            old_stdout = sys.stdout
            sys.stdout = captured

            try:
                obpi_complete_cmd(
                    obpi="OBPI-0.0.14-02",
                    attestor="jeff",
                    attestation_text="Verified",
                    implementation_summary="- Files: obpi_complete.py",
                    key_proof="gz obpi complete exits 0",
                    as_json=True,
                    dry_run=True,
                )
            finally:
                sys.stdout = old_stdout

            output = captured.getvalue().strip()
            parsed = json.loads(output)
            self.assertEqual(parsed["status"], "dry_run")
            self.assertEqual(parsed["obpi_id"], "OBPI-0.0.14-02")


@covers("OBPI-0.0.14-02")
class TestObpiCompleteCmdHappyPath(unittest.TestCase):
    """Test full happy path with mocked dependencies.

    The authenticity gate (GHI #290) is patched to a no-op here because this
    test exercises the full transaction path with human attestation required;
    the gate itself is tested in TestObpiCompleteAuthenticityGate below. The
    receipt-binding gate (ADR-0.0.24-02) is also patched to a no-op for the
    same reason — it is tested in tests/commands/test_obpi_complete.py under
    the new TestObpiCompleteHeavy* / TestObpiCompleteFoundation* classes.
    """

    @patch("gzkit.commands.obpi_complete._enforce_req_coverage_gate")
    @patch("gzkit.commands.obpi_complete._enforce_attestation_receipt_gate")
    @patch("gzkit.commands.obpi_complete.console", _quiet_console)
    @patch("gzkit.commands.obpi_complete.capture_validation_anchor")
    @patch("gzkit.commands.obpi_complete._requires_human_obpi_attestation")
    @patch("gzkit.commands.obpi_complete.resolve_adr_file")
    @patch("gzkit.commands.obpi_complete.get_project_root")
    @patch("gzkit.commands.obpi_complete.ensure_initialized")
    @patch("gzkit.commands.obpi_complete.resolve_obpi_file")
    @patch("gzkit.commands.obpi_complete.Ledger")
    @covers("REQ-0.0.14-02-04")
    @covers("REQ-0.0.14-02-05")
    @covers("REQ-0.0.14-02-06")
    def test_completes_brief_and_emits_receipt(
        self,
        mock_ledger_cls,
        mock_resolve,
        mock_init,
        mock_root,
        mock_adr_resolve,
        mock_requires_human,
        mock_anchor,
        mock_receipt_gate,
        mock_coverage_gate,
    ):
        del mock_receipt_gate  # ADR-0.0.24-02 receipt-binding gate is patched
        del mock_coverage_gate  # OBPI-0.0.25-01 coverage gate patched to no-op
        # to a no-op here; the new contract is exercised in
        # tests/commands/test_obpi_complete.py. The prior TTY 'ATTEST' gate is
        # removed: the operator's verbatim --attestation-text is the Gate-5
        # attestation, recorded as attestation_type operator-verbatim-conversational.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            mock_root.return_value = root
            mock_init.return_value = _mock_config()
            mock_requires_human.return_value = True
            mock_anchor.return_value = EventAnchor(commit="abc1234", semver="0.0.14")

            # Set up brief file inside an adr/obpis directory structure
            adr_dir = root / "adr"
            obpis_dir = adr_dir / "obpis"
            obpis_dir.mkdir(parents=True)
            obpi_file = obpis_dir / "OBPI-0.0.14-02-obpi-complete-command.md"
            obpi_file.write_text(_MINIMAL_BRIEF, encoding="utf-8")
            mock_resolve.return_value = (obpi_file, "OBPI-0.0.14-02")

            ledger = _mock_ledger("OBPI-0.0.14-02", "ADR-0.0.14")
            mock_ledger_cls.return_value = ledger
            mock_adr_resolve.return_value = (adr_dir / "ADR-0.0.14.md", "ADR-0.0.14")

            obpi_complete_cmd(
                obpi="OBPI-0.0.14-02",
                attestor="jeff",
                attestation_text="Lock commands verified",
                implementation_summary=(
                    "- Files: obpi_complete.py, parser_artifacts.py\n- Tests: 11 added"
                ),
                key_proof="gz obpi complete OBPI-0.0.14-01 exits 0",
                as_json=False,
                dry_run=False,
            )

            # Brief should be updated
            updated = obpi_file.read_text(encoding="utf-8")
            self.assertIn("status: Completed", updated)
            self.assertIn("**Brief Status:** Completed", updated)
            self.assertIn("- Attestor: `jeff`", updated)
            self.assertIn("- Attestation: Lock commands verified", updated)
            self.assertIn("obpi_complete.py, parser_artifacts.py", updated)

            # Audit ledger should have an entry
            audit_file = adr_dir / "logs" / "obpi-audit.jsonl"
            self.assertTrue(audit_file.exists())
            audit_entries = audit_file.read_text(encoding="utf-8").strip().splitlines()
            self.assertEqual(len(audit_entries), 1)
            parsed = json.loads(audit_entries[0])
            self.assertEqual(parsed["attestation_type"], "operator-verbatim-conversational")

            # Main ledger should have been appended
            ledger.append.assert_called_once()


@covers("OBPI-0.0.14-02")
class TestObpiCompleteCmdRollback(unittest.TestCase):
    """Test rollback when main ledger append fails.

    The receipt-binding gate (ADR-0.0.24-02) is patched to a no-op so the
    rollback test exercises the I/O-failure path under its original contract;
    the new gate is covered in tests/commands/test_obpi_complete.py.
    """

    @patch("gzkit.commands.obpi_complete._enforce_req_coverage_gate")
    @patch("gzkit.commands.obpi_complete._enforce_attestation_receipt_gate")
    @patch("gzkit.commands.obpi_complete.console", _quiet_console)
    @patch("gzkit.commands.obpi_complete.capture_validation_anchor")
    @patch("gzkit.commands.obpi_complete._requires_human_obpi_attestation")
    @patch("gzkit.commands.obpi_complete.resolve_adr_file")
    @patch("gzkit.commands.obpi_complete.get_project_root")
    @patch("gzkit.commands.obpi_complete.ensure_initialized")
    @patch("gzkit.commands.obpi_complete.resolve_obpi_file")
    @patch("gzkit.commands.obpi_complete.Ledger")
    @covers("REQ-0.0.14-02-07")
    def test_rollback_on_ledger_failure(
        self,
        mock_ledger_cls,
        mock_resolve,
        mock_init,
        mock_root,
        mock_adr_resolve,
        mock_requires_human,
        mock_anchor,
        mock_receipt_gate,
        mock_coverage_gate,
    ):
        del mock_receipt_gate  # see class docstring
        del mock_coverage_gate  # OBPI-0.0.25-01 coverage gate patched no-op
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            mock_root.return_value = root
            mock_init.return_value = _mock_config()
            mock_requires_human.return_value = False
            mock_anchor.return_value = EventAnchor(commit="abc1234", semver="0.0.14")

            adr_dir = root / "adr"
            obpis_dir = adr_dir / "obpis"
            obpis_dir.mkdir(parents=True)
            obpi_file = obpis_dir / "OBPI-0.0.14-02.md"
            obpi_file.write_text(_MINIMAL_BRIEF, encoding="utf-8")
            mock_resolve.return_value = (obpi_file, "OBPI-0.0.14-02")

            ledger = _mock_ledger("OBPI-0.0.14-02", "ADR-0.0.14")
            ledger.append.side_effect = OSError("Disk full")
            mock_ledger_cls.return_value = ledger
            mock_adr_resolve.return_value = (adr_dir / "ADR-0.0.14.md", "ADR-0.0.14")

            with self.assertRaises(SystemExit) as ctx:
                obpi_complete_cmd(
                    obpi="OBPI-0.0.14-02",
                    attestor="jeff",
                    attestation_text="Verified",
                    implementation_summary="- Files: obpi_complete.py",
                    key_proof="gz obpi complete exits 0",
                    as_json=False,
                    dry_run=False,
                )
            self.assertEqual(ctx.exception.code, 2)

            # Brief should be restored to original
            restored = obpi_file.read_text(encoding="utf-8")
            self.assertEqual(restored, _MINIMAL_BRIEF)

            # Audit ledger entry should be rolled back
            audit_file = adr_dir / "logs" / "obpi-audit.jsonl"
            if audit_file.exists():
                content = audit_file.read_text(encoding="utf-8").strip()
                self.assertEqual(content, "")


@covers("OBPI-0.0.14-02")
class TestObpiCompleteOperatorVerbatimAttestation(unittest.TestCase):
    """gz obpi complete records the operator's verbatim attestation.

    The prior GHI #290 TTY 'ATTEST' authenticity gate has been removed per
    the canon-owner declaration: the operator's verbatim attestation relayed
    via --attestation-text IS the Gate-5 attestation for every lane / kind /
    sensitivity. A non-empty --attestation-text completes a requires-human
    brief headlessly; an empty one exits 1 (the text is the attestation). The
    receipt-binding and REQ-coverage gates are patched to no-op here so the
    attestation behavior is exercised in isolation.
    """

    @patch("gzkit.commands.obpi_complete._enforce_req_coverage_gate")
    @patch("gzkit.commands.obpi_complete._enforce_attestation_receipt_gate")
    @patch("gzkit.commands.obpi_complete.console", _quiet_console)
    @patch("gzkit.commands.obpi_complete.capture_validation_anchor")
    @patch("gzkit.commands.obpi_complete._requires_human_obpi_attestation")
    @patch("gzkit.commands.obpi_complete.resolve_adr_file")
    @patch("gzkit.commands.obpi_complete.get_project_root")
    @patch("gzkit.commands.obpi_complete.ensure_initialized")
    @patch("gzkit.commands.obpi_complete.resolve_obpi_file")
    @patch("gzkit.commands.obpi_complete.Ledger")
    def test_headless_completion_succeeds_with_attestation_text(
        self,
        mock_ledger_cls,
        mock_resolve,
        mock_init,
        mock_root,
        mock_adr_resolve,
        mock_requires_human,
        mock_anchor,
        mock_receipt_gate,
        mock_coverage_gate,
    ):
        del mock_receipt_gate, mock_coverage_gate  # patched no-op; covered elsewhere
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            mock_root.return_value = root
            mock_init.return_value = _mock_config()
            mock_requires_human.return_value = True
            mock_anchor.return_value = EventAnchor(commit="abc1234", semver="0.0.14")

            adr_dir = root / "adr"
            obpis_dir = adr_dir / "obpis"
            obpis_dir.mkdir(parents=True)
            obpi_file = obpis_dir / "OBPI-0.0.14-02.md"
            obpi_file.write_text(_MINIMAL_BRIEF, encoding="utf-8")
            mock_resolve.return_value = (obpi_file, "OBPI-0.0.14-02")

            ledger = _mock_ledger("OBPI-0.0.14-02", "ADR-0.0.14")
            mock_ledger_cls.return_value = ledger
            mock_adr_resolve.return_value = (adr_dir / "ADR-0.0.14.md", "ADR-0.0.14")

            # Headless (no TTY) — must still complete: the operator's verbatim
            # --attestation-text is the attestation, recorded as
            # attestation_type operator-verbatim-conversational.
            obpi_complete_cmd(
                obpi="OBPI-0.0.14-02",
                attestor="Jeffry Babb",
                attestation_text="attest completed -- obpi_complete.py verified",
                implementation_summary="- Files: obpi_complete.py",
                key_proof="gz obpi complete exits 0",
                as_json=False,
                dry_run=False,
            )

            self.assertIn("status: Completed", obpi_file.read_text(encoding="utf-8"))
            ledger.append.assert_called_once()
            audit_file = adr_dir / "logs" / "obpi-audit.jsonl"
            parsed = json.loads(audit_file.read_text(encoding="utf-8").strip())
            self.assertEqual(parsed["attestation_type"], "operator-verbatim-conversational")

    @patch("gzkit.commands.obpi_complete._enforce_req_coverage_gate")
    @patch("gzkit.commands.obpi_complete._enforce_attestation_receipt_gate")
    @patch("gzkit.commands.obpi_complete.console", _quiet_console)
    @patch("gzkit.commands.obpi_complete.capture_validation_anchor")
    @patch("gzkit.commands.obpi_complete._requires_human_obpi_attestation")
    @patch("gzkit.commands.obpi_complete.resolve_adr_file")
    @patch("gzkit.commands.obpi_complete.get_project_root")
    @patch("gzkit.commands.obpi_complete.ensure_initialized")
    @patch("gzkit.commands.obpi_complete.resolve_obpi_file")
    @patch("gzkit.commands.obpi_complete.Ledger")
    def test_empty_attestation_text_exits_1(
        self,
        mock_ledger_cls,
        mock_resolve,
        mock_init,
        mock_root,
        mock_adr_resolve,
        mock_requires_human,
        mock_anchor,
        mock_receipt_gate,
        mock_coverage_gate,
    ):
        del mock_receipt_gate, mock_coverage_gate  # patched no-op; covered elsewhere
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            mock_root.return_value = root
            mock_init.return_value = _mock_config()
            mock_requires_human.return_value = True
            mock_anchor.return_value = EventAnchor(commit="abc1234", semver="0.0.14")

            adr_dir = root / "adr"
            obpis_dir = adr_dir / "obpis"
            obpis_dir.mkdir(parents=True)
            obpi_file = obpis_dir / "OBPI-0.0.14-02.md"
            obpi_file.write_text(_MINIMAL_BRIEF, encoding="utf-8")
            mock_resolve.return_value = (obpi_file, "OBPI-0.0.14-02")

            ledger = _mock_ledger("OBPI-0.0.14-02", "ADR-0.0.14")
            mock_ledger_cls.return_value = ledger
            mock_adr_resolve.return_value = (adr_dir / "ADR-0.0.14.md", "ADR-0.0.14")

            # Empty attestation text for a requires-human brief: there is no
            # attestation to record, so the command exits 1 (user error) and
            # leaves the brief unmutated.
            with self.assertRaises(SystemExit) as ctx:
                obpi_complete_cmd(
                    obpi="OBPI-0.0.14-02",
                    attestor="Jeffry Babb",
                    attestation_text="",
                    implementation_summary="- Files: obpi_complete.py",
                    key_proof="gz obpi complete exits 0",
                    as_json=False,
                    dry_run=False,
                )
            self.assertEqual(ctx.exception.code, 1)
            self.assertEqual(obpi_file.read_text(encoding="utf-8"), _MINIMAL_BRIEF)
            ledger.append.assert_not_called()

    @patch("gzkit.commands.obpi_complete.console", _quiet_console)
    @patch("gzkit.commands.obpi_complete.capture_validation_anchor")
    @patch("gzkit.commands.obpi_complete._requires_human_obpi_attestation")
    @patch("gzkit.commands.obpi_complete.resolve_adr_file")
    @patch("gzkit.commands.obpi_complete.get_project_root")
    @patch("gzkit.commands.obpi_complete.ensure_initialized")
    @patch("gzkit.commands.obpi_complete.resolve_obpi_file")
    @patch("gzkit.commands.obpi_complete.Ledger")
    def test_dry_run_skips_attestation(
        self,
        mock_ledger_cls,
        mock_resolve,
        mock_init,
        mock_root,
        mock_adr_resolve,
        mock_requires_human,
        mock_anchor,
    ):
        """--dry-run must preview headlessly without recording attestation."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            mock_root.return_value = root
            mock_init.return_value = _mock_config()
            mock_requires_human.return_value = True
            mock_anchor.return_value = EventAnchor(commit="abc1234", semver="0.0.14")

            adr_dir = root / "adr"
            obpis_dir = adr_dir / "obpis"
            obpis_dir.mkdir(parents=True)
            obpi_file = obpis_dir / "OBPI-0.0.14-02.md"
            obpi_file.write_text(_MINIMAL_BRIEF, encoding="utf-8")
            mock_resolve.return_value = (obpi_file, "OBPI-0.0.14-02")

            ledger = _mock_ledger("OBPI-0.0.14-02", "ADR-0.0.14")
            mock_ledger_cls.return_value = ledger
            mock_adr_resolve.return_value = (adr_dir / "ADR-0.0.14.md", "ADR-0.0.14")

            obpi_complete_cmd(
                obpi="OBPI-0.0.14-02",
                attestor="Jeffry Babb",
                attestation_text="dry-run preview",
                implementation_summary="- Files: obpi_complete.py",
                key_proof="gz obpi complete exits 0",
                as_json=False,
                dry_run=True,
            )
            # No state changes
            self.assertEqual(obpi_file.read_text(encoding="utf-8"), _MINIMAL_BRIEF)
            ledger.append.assert_not_called()


@covers("OBPI-0.0.14-02")
class TestAuthenticityGateUnit(unittest.TestCase):
    """Direct unit tests for _enforce_human_attestation_authenticity."""

    def test_non_tty_raises(self):
        from gzkit.commands.adr_audit import _enforce_human_attestation_authenticity
        from gzkit.commands.common import GzCliError

        with (
            patch("gzkit.commands.adr_audit.console", _quiet_console),
            patch(
                "gzkit.commands.adr_audit._is_human_attestation_tty_available",
                return_value=False,
            ),
        ):
            with self.assertRaises(GzCliError) as ctx:
                _enforce_human_attestation_authenticity(
                    obpi_id="OBPI-0.0.20-03",
                    parent_adr="ADR-0.0.20",
                    attestor="Jeffry Babb",
                    attestation_text="fabricated",
                )
            self.assertIn("TTY", str(ctx.exception))
            self.assertIn("GHI #290", str(ctx.exception))

    def test_wrong_confirmation_word_raises(self):
        from gzkit.commands.adr_audit import _enforce_human_attestation_authenticity
        from gzkit.commands.common import GzCliError

        with (
            patch("gzkit.commands.adr_audit.console", _quiet_console),
            patch(
                "gzkit.commands.adr_audit._is_human_attestation_tty_available",
                return_value=True,
            ),
            patch("gzkit.commands.adr_audit.input", create=True, return_value="attest"),
        ):
            with self.assertRaises(GzCliError) as ctx:
                _enforce_human_attestation_authenticity(
                    obpi_id="OBPI-0.0.20-03",
                    parent_adr="ADR-0.0.20",
                    attestor="Jeffry Babb",
                    attestation_text="case-sensitive test",
                )
            self.assertIn("declined", str(ctx.exception).lower())

    def test_lowercase_y_rejected(self):
        """A simple [y/N] prompt would be trivially defeatable. Require 'ATTEST'."""
        from gzkit.commands.adr_audit import _enforce_human_attestation_authenticity
        from gzkit.commands.common import GzCliError

        with (
            patch("gzkit.commands.adr_audit.console", _quiet_console),
            patch(
                "gzkit.commands.adr_audit._is_human_attestation_tty_available",
                return_value=True,
            ),
            patch("gzkit.commands.adr_audit.input", create=True, return_value="y"),
            self.assertRaises(GzCliError),
        ):
            _enforce_human_attestation_authenticity(
                obpi_id="OBPI-0.0.20-03",
                parent_adr="ADR-0.0.20",
                attestor="Jeffry Babb",
                attestation_text="y is not enough",
            )

    def test_eof_aborts(self):
        from gzkit.commands.adr_audit import _enforce_human_attestation_authenticity
        from gzkit.commands.common import GzCliError

        def _raise_eof(*_args, **_kwargs):
            raise EOFError

        with (
            patch("gzkit.commands.adr_audit.console", _quiet_console),
            patch(
                "gzkit.commands.adr_audit._is_human_attestation_tty_available",
                return_value=True,
            ),
            patch("gzkit.commands.adr_audit.input", create=True, side_effect=_raise_eof),
        ):
            with self.assertRaises(GzCliError) as ctx:
                _enforce_human_attestation_authenticity(
                    obpi_id="OBPI-0.0.20-03",
                    parent_adr="ADR-0.0.20",
                    attestor="Jeffry Babb",
                    attestation_text="eof path",
                )
            self.assertIn("aborted", str(ctx.exception).lower())

    def test_attest_exact_match_passes(self):
        from gzkit.commands.adr_audit import (
            ATTESTATION_TYPE_HUMAN,
            _enforce_human_attestation_authenticity,
        )

        with (
            patch("gzkit.commands.adr_audit.console", _quiet_console),
            patch(
                "gzkit.commands.adr_audit._is_human_attestation_tty_available",
                return_value=True,
            ),
            patch(
                "gzkit.commands.adr_audit.input",
                create=True,
                return_value="ATTEST",
            ),
        ):
            result = _enforce_human_attestation_authenticity(
                obpi_id="OBPI-0.0.20-03",
                parent_adr="ADR-0.0.20",
                attestor="Jeffry Babb",
                attestation_text="exact uppercase",
            )
            self.assertEqual(result, ATTESTATION_TYPE_HUMAN)


@covers("OBPI-0.0.14-02")
class TestAgentRelayedEscapePath(unittest.TestCase):
    """GHI #292 — --attestor-present escape path for agent+operator co-presence.

    The GHI #290 TTY gate conflated 'headless agent' with 'agent + operator
    co-present via tool-use Bash'. These tests pin the three branches of the
    post-#292 gate: TTY path still returns 'human'; non-TTY + --attestor-present
    + active pipeline marker returns 'agent-relayed-operator-attestation';
    non-TTY without either signal still fails closed.
    """

    def _write_marker(
        self,
        project_root: Path,
        obpi_id: str,
        parent_adr: str = "ADR-0.0.20",
        nonce: str = "0123456789abcdef0123456789abcdef",
        emit_ledger_event: bool = True,
    ) -> Path:
        """Write a GHI #412-authentic marker and matching ledger event.

        Pre-GHI #412 the test suite wrote a minimal ``{"obpi_id": ..., "current_stage": ...}``
        marker because the validator only ran ``is_file()``. The hardened
        validator requires the full ``pipeline_marker_payload`` shape AND a
        matching ``pipeline_launched`` ledger event with the same nonce.
        """
        from datetime import UTC, datetime

        plans_dir = project_root / ".claude" / "plans"
        plans_dir.mkdir(parents=True, exist_ok=True)
        marker = plans_dir / f".pipeline-active-{obpi_id}.json"
        timestamp = datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
        marker.write_text(
            json.dumps(
                {
                    "obpi_id": obpi_id,
                    "parent_adr": parent_adr,
                    "lane": "heavy",
                    "entry": "full",
                    "execution_mode": "normal",
                    "current_stage": "ceremony",
                    "started_at": timestamp,
                    "updated_at": timestamp,
                    "receipt_state": "pass",
                    "nonce": nonce,
                }
            ),
            encoding="utf-8",
        )
        if emit_ledger_event:
            ledger_dir = project_root / ".gzkit"
            ledger_dir.mkdir(parents=True, exist_ok=True)
            ledger_path = ledger_dir / "ledger.jsonl"
            event = {
                "schema": "gzkit.ledger.v1",
                "event": "pipeline_launched",
                "id": obpi_id,
                "ts": timestamp,
                "parent": parent_adr,
                "nonce": nonce,
                "marker_path": marker.relative_to(project_root).as_posix(),
                "lane": "heavy",
                "entry": "full",
            }
            with ledger_path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(event) + "\n")
        return marker

    def test_non_tty_with_attestor_present_and_marker_returns_agent_relayed(self):
        from gzkit.commands.adr_audit import (
            ATTESTATION_TYPE_AGENT_RELAYED,
            _enforce_human_attestation_authenticity,
        )

        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp)
            self._write_marker(project_root, "OBPI-0.0.20-03")
            with (
                patch("gzkit.commands.adr_audit.console", _quiet_console),
                patch(
                    "gzkit.commands.adr_audit._is_human_attestation_tty_available",
                    return_value=False,
                ),
            ):
                result = _enforce_human_attestation_authenticity(
                    obpi_id="OBPI-0.0.20-03",
                    parent_adr="ADR-0.0.20",
                    attestor="Jeffry Babb",
                    attestation_text="agent-relayed under active pipeline marker",
                    attestor_present=True,
                    project_root=project_root,
                )
                self.assertEqual(result, ATTESTATION_TYPE_AGENT_RELAYED)

    def test_non_tty_with_attestor_present_but_no_marker_raises(self):
        from gzkit.commands.adr_audit import _enforce_human_attestation_authenticity
        from gzkit.commands.common import GzCliError

        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp)
            # Deliberately do not write a marker.
            with (
                patch("gzkit.commands.adr_audit.console", _quiet_console),
                patch(
                    "gzkit.commands.adr_audit._is_human_attestation_tty_available",
                    return_value=False,
                ),
            ):
                with self.assertRaises(GzCliError) as ctx:
                    _enforce_human_attestation_authenticity(
                        obpi_id="OBPI-0.0.20-03",
                        parent_adr="ADR-0.0.20",
                        attestor="Jeffry Babb",
                        attestation_text="no marker, should fail",
                        attestor_present=True,
                        project_root=project_root,
                    )
                self.assertIn("marker file does not exist", str(ctx.exception))
                self.assertIn("gz obpi pipeline", str(ctx.exception))

    def test_non_tty_without_attestor_present_still_raises(self):
        from gzkit.commands.adr_audit import _enforce_human_attestation_authenticity
        from gzkit.commands.common import GzCliError

        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp)
            # Even with a marker present, without the flag the gate fails closed.
            self._write_marker(project_root, "OBPI-0.0.20-03")
            with (
                patch("gzkit.commands.adr_audit.console", _quiet_console),
                patch(
                    "gzkit.commands.adr_audit._is_human_attestation_tty_available",
                    return_value=False,
                ),
            ):
                with self.assertRaises(GzCliError) as ctx:
                    _enforce_human_attestation_authenticity(
                        obpi_id="OBPI-0.0.20-03",
                        parent_adr="ADR-0.0.20",
                        attestor="Jeffry Babb",
                        attestation_text="flag not set",
                        attestor_present=False,
                        project_root=project_root,
                    )
                self.assertIn("GHI #290", str(ctx.exception))
                self.assertIn("--attestor-present", str(ctx.exception))

    def test_tty_path_with_attestor_present_still_prompts_attest(self):
        """TTY path must not be bypassed by --attestor-present; the flag only
        opens the non-TTY marker-based escape."""
        from gzkit.commands.adr_audit import (
            ATTESTATION_TYPE_HUMAN,
            _enforce_human_attestation_authenticity,
        )
        from gzkit.commands.common import GzCliError

        with (
            patch("gzkit.commands.adr_audit.console", _quiet_console),
            patch(
                "gzkit.commands.adr_audit._is_human_attestation_tty_available",
                return_value=True,
            ),
            patch("gzkit.commands.adr_audit.input", create=True, return_value="nope"),
            self.assertRaises(GzCliError),
        ):
            _enforce_human_attestation_authenticity(
                obpi_id="OBPI-0.0.20-03",
                parent_adr="ADR-0.0.20",
                attestor="Jeffry Babb",
                attestation_text="TTY still prompts",
                attestor_present=True,
                project_root=Path("/nonexistent"),
            )

        # And when the prompt is satisfied, the resolved type is still 'human'.
        with (
            patch("gzkit.commands.adr_audit.console", _quiet_console),
            patch(
                "gzkit.commands.adr_audit._is_human_attestation_tty_available",
                return_value=True,
            ),
            patch("gzkit.commands.adr_audit.input", create=True, return_value="ATTEST"),
        ):
            result = _enforce_human_attestation_authenticity(
                obpi_id="OBPI-0.0.20-03",
                parent_adr="ADR-0.0.20",
                attestor="Jeffry Babb",
                attestation_text="TTY-typed wins",
                attestor_present=True,
                project_root=Path("/nonexistent"),
            )
            self.assertEqual(result, ATTESTATION_TYPE_HUMAN)


# ---------------------------------------------------------------------------
# OBPI-0.0.22-04 — sensitivity:security forces TTY+ATTEST gate via OR
# ---------------------------------------------------------------------------


_SECURITY_BRIEF = """\
---
id: OBPI-0.99.0-sec-feature-test
parent: ADR-0.99.0-some-feature
item: 1
lane: Lite
status: Draft
sensitivity: security
---

# OBPI-0.99.0-sec-feature-test: security-sensitive lite-feature brief

## Objective

Brief used by REQ-0.0.22-04-05 to confirm the OR composition reuses the
existing TTY + ATTEST gate without any new TTY-gating code.

## Allowed Paths

- `tests/test_obpi_complete_cmd.py`

## Requirements (FAIL-CLOSED)

1. Test fixture only.

## Acceptance Criteria

- [ ] REQ-0.99.0-01-01: fixture-only

## Evidence

### Implementation Summary

- Files created/modified: tests/test_obpi_complete_cmd.py
- Tests added: REQ-0.0.22-04-05 behavioral test
- Date completed: 2026-04-29
- Attestation status: Pending TTY confirmation
- Defects noted: None

### Key Proof

`gz obpi complete` exits 3 with no TTY when frontmatter declares
`sensitivity: security`, even though the parent ADR is lite + feature.

## Human Attestation

- Attestor: `<name>` when required, otherwise `n/a`
- Attestation: substantive attestation text or `n/a`
- Date: YYYY-MM-DD or `n/a`

---

**Brief Status:** Draft

**Date Completed:** -

**Evidence Hash:** -
"""


def _mock_ledger_lite_feature(obpi_id: str, parent_adr: str):
    """Mock ledger where the parent ADR is lite + feature (non-foundation)."""
    ledger = MagicMock()
    ledger.canonicalize_id.return_value = obpi_id
    graph = {
        obpi_id: {
            "type": "obpi",
            "parent": parent_adr,
            "ledger_completed": False,
        },
        parent_adr: {
            "type": "adr",
            "lane": "lite",
        },
    }
    ledger.get_artifact_graph.return_value = graph
    return ledger


@covers("OBPI-0.0.22-04")
class TestObpiCompleteSecuritySensitivityGate(unittest.TestCase):
    """REQ-0.0.22-04-05 — sensitivity:security forces the human-attestation
    requirement.

    The test uses the *real* ``_requires_human_obpi_attestation`` predicate
    (not a mock) to prove the OR composition wires through end-to-end. A
    ``lite + feature + sensitivity:security`` brief still requires human
    attestation — so the completion records attestation_type
    ``operator-verbatim-conversational``, whereas the same brief without the
    sensitivity field self-closes (``self-close-exception``). The prior GHI
    #290 TTY 'ATTEST' gate has been removed: the operator's verbatim
    --attestation-text satisfies the requirement headlessly. The
    security-review canonical-slot gate is patched to no-op here so the
    attestation-requirement composition is exercised in isolation.
    """

    @patch("gzkit.commands.obpi_complete._enforce_req_coverage_gate")
    @patch("gzkit.commands.obpi_complete._enforce_attestation_receipt_gate")
    @patch("gzkit.commands.obpi_complete._enforce_security_review_gate")
    @patch("gzkit.commands.obpi_complete.console", _quiet_console)
    @patch("gzkit.commands.obpi_complete.capture_validation_anchor")
    @patch("gzkit.commands.obpi_complete.resolve_adr_file")
    @patch("gzkit.commands.obpi_complete.get_project_root")
    @patch("gzkit.commands.obpi_complete.ensure_initialized")
    @patch("gzkit.commands.obpi_complete.resolve_obpi_file")
    @patch("gzkit.commands.obpi_complete.Ledger")
    @covers("REQ-0.0.22-04-05")
    def test_lite_feature_security_brief_requires_operator_verbatim_attestation(
        self,
        mock_ledger_cls,
        mock_resolve,
        mock_init,
        mock_root,
        mock_adr_resolve,
        mock_anchor,
        mock_security_gate,
        mock_receipt_gate,
        mock_coverage_gate,
    ):
        del mock_security_gate, mock_receipt_gate, mock_coverage_gate  # patched no-op
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            mock_root.return_value = root
            cfg = _mock_config()
            cfg.mode = "lite"
            mock_init.return_value = cfg
            mock_anchor.return_value = EventAnchor(commit="def5678", semver="0.99.0")

            adr_dir = root / "adr"
            obpis_dir = adr_dir / "obpis"
            obpis_dir.mkdir(parents=True)
            obpi_id = "OBPI-0.99.0-sec-feature-test"
            adr_id = "ADR-0.99.0-some-feature"
            obpi_file = obpis_dir / f"{obpi_id}.md"
            obpi_file.write_text(_SECURITY_BRIEF, encoding="utf-8")
            mock_resolve.return_value = (obpi_file, obpi_id)

            ledger = _mock_ledger_lite_feature(obpi_id, adr_id)
            mock_ledger_cls.return_value = ledger
            mock_adr_resolve.return_value = (adr_dir / f"{adr_id}.md", adr_id)

            # sensitivity:security forces requires_human=True via the OR
            # composition — the completion records operator-verbatim
            # attestation, not the self-close exception.
            obpi_complete_cmd(
                obpi=obpi_id,
                attestor="Jeffry Babb",
                attestation_text="attest completed -- security brief verified",
                implementation_summary="- Files: tests/test_obpi_complete_cmd.py",
                key_proof="security brief completes with operator-verbatim attestation",
                as_json=False,
                dry_run=False,
            )
            self.assertIn("status: Completed", obpi_file.read_text(encoding="utf-8"))
            audit_file = adr_dir / "logs" / "obpi-audit.jsonl"
            parsed = json.loads(audit_file.read_text(encoding="utf-8").strip())
            self.assertEqual(parsed["attestation_type"], "operator-verbatim-conversational")

    @patch("gzkit.commands.obpi_complete._enforce_req_coverage_gate")
    @patch("gzkit.commands.obpi_complete._enforce_attestation_receipt_gate")
    @patch("gzkit.commands.obpi_complete._enforce_security_review_gate")
    @patch("gzkit.commands.obpi_complete.console", _quiet_console)
    @patch("gzkit.commands.obpi_complete.capture_validation_anchor")
    @patch("gzkit.commands.obpi_complete.resolve_adr_file")
    @patch("gzkit.commands.obpi_complete.get_project_root")
    @patch("gzkit.commands.obpi_complete.ensure_initialized")
    @patch("gzkit.commands.obpi_complete.resolve_obpi_file")
    @patch("gzkit.commands.obpi_complete.Ledger")
    @covers("REQ-0.0.22-04-03")
    def test_lite_feature_no_sensitivity_remains_self_closeable_e2e(
        self,
        mock_ledger_cls,
        mock_resolve,
        mock_init,
        mock_root,
        mock_adr_resolve,
        mock_anchor,
        mock_security_gate,
        mock_receipt_gate,
        mock_coverage_gate,
    ):
        del mock_security_gate, mock_receipt_gate, mock_coverage_gate  # patched no-op
        # Sister proof to REQ-05: the *same* lite + feature parent without
        # the sensitivity field does NOT require human attestation — it
        # self-closes (attestation_type self-close-exception).
        baseline_brief = _SECURITY_BRIEF.replace("sensitivity: security\n", "")
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            mock_root.return_value = root
            cfg = _mock_config()
            cfg.mode = "lite"
            mock_init.return_value = cfg
            mock_anchor.return_value = EventAnchor(commit="def5678", semver="0.99.0")

            adr_dir = root / "adr"
            obpis_dir = adr_dir / "obpis"
            obpis_dir.mkdir(parents=True)
            obpi_id = "OBPI-0.99.0-sec-feature-test"
            adr_id = "ADR-0.99.0-some-feature"
            obpi_file = obpis_dir / f"{obpi_id}.md"
            obpi_file.write_text(baseline_brief, encoding="utf-8")
            mock_resolve.return_value = (obpi_file, obpi_id)

            ledger = _mock_ledger_lite_feature(obpi_id, adr_id)
            mock_ledger_cls.return_value = ledger
            mock_adr_resolve.return_value = (adr_dir / f"{adr_id}.md", adr_id)

            # Self-closeable path completes because the predicate returns
            # False — no security axis, lite lane, feature kind.
            obpi_complete_cmd(
                obpi=obpi_id,
                attestor="Jeffry Babb",
                attestation_text="self-close evidence baseline",
                implementation_summary="- Files: tests/test_obpi_complete_cmd.py",
                key_proof="completion succeeds when no sensitivity axis is present",
                as_json=False,
                dry_run=False,
            )
            self.assertIn("status: Completed", obpi_file.read_text(encoding="utf-8"))
            ledger.append.assert_called_once()


# ---------------------------------------------------------------------------
# GHI #412: pipeline-marker authenticity hardening — closes the
# "marker.is_file()" forgery surface and refuses agent-relayed attestation
# for sensitivity:security and foundation-kind scopes.
# ---------------------------------------------------------------------------


def _write_authentic_marker(
    project_root: Path,
    obpi_id: str,
    parent_adr: str,
    *,
    nonce: str = "00112233445566778899aabbccddeeff",
    started_at: str | None = None,
    current_stage: str = "ceremony",
    emit_ledger_event: bool = True,
) -> Path:
    from datetime import UTC, datetime

    plans_dir = project_root / ".claude" / "plans"
    plans_dir.mkdir(parents=True, exist_ok=True)
    marker = plans_dir / f".pipeline-active-{obpi_id}.json"
    if started_at is None:
        started_at = datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    marker.write_text(
        json.dumps(
            {
                "obpi_id": obpi_id,
                "parent_adr": parent_adr,
                "lane": "heavy",
                "entry": "full",
                "execution_mode": "normal",
                "current_stage": current_stage,
                "started_at": started_at,
                "updated_at": started_at,
                "receipt_state": "pass",
                "nonce": nonce,
            }
        ),
        encoding="utf-8",
    )
    if emit_ledger_event:
        ledger_dir = project_root / ".gzkit"
        ledger_dir.mkdir(parents=True, exist_ok=True)
        ledger_path = ledger_dir / "ledger.jsonl"
        with ledger_path.open("a", encoding="utf-8") as handle:
            handle.write(
                json.dumps(
                    {
                        "schema": "gzkit.ledger.v1",
                        "event": "pipeline_launched",
                        "id": obpi_id,
                        "ts": started_at,
                        "parent": parent_adr,
                        "nonce": nonce,
                        "marker_path": marker.relative_to(project_root).as_posix(),
                        "lane": "heavy",
                        "entry": "full",
                    }
                )
                + "\n"
            )
    return marker


class TestPipelineMarkerAuthenticityGhi412(unittest.TestCase):
    """GHI #412: closes the forgery surface where any writable repo file
    satisfied ``--attestor-present``. The validator now requires structure,
    freshness, parent_adr match, a 32-hex nonce, and a matching
    ``pipeline_launched`` ledger event."""

    def _run_gate(
        self,
        project_root: Path,
        *,
        obpi_id: str = "OBPI-0.0.20-03",
        parent_adr: str = "ADR-0.0.20",
        sensitivity: str | None = None,
        parent_kind: str | None = None,
    ):
        from gzkit.commands.adr_audit import _enforce_human_attestation_authenticity

        with (
            patch("gzkit.commands.adr_audit.console", _quiet_console),
            patch(
                "gzkit.commands.adr_audit._is_human_attestation_tty_available",
                return_value=False,
            ),
        ):
            return _enforce_human_attestation_authenticity(
                obpi_id=obpi_id,
                parent_adr=parent_adr,
                attestor="Jeffry Babb",
                attestation_text="GHI #412 unit",
                attestor_present=True,
                project_root=project_root,
                sensitivity=sensitivity,
                parent_kind=parent_kind,
            )

    def test_authentic_marker_with_ledger_event_returns_agent_relayed(self):
        from gzkit.commands.adr_audit import ATTESTATION_TYPE_AGENT_RELAYED

        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp)
            _write_authentic_marker(project_root, "OBPI-0.0.20-03", "ADR-0.0.20")
            self.assertEqual(self._run_gate(project_root), ATTESTATION_TYPE_AGENT_RELAYED)

    def test_marker_with_unparseable_json_is_rejected(self):
        from gzkit.commands.common import GzCliError

        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp)
            plans_dir = project_root / ".claude" / "plans"
            plans_dir.mkdir(parents=True, exist_ok=True)
            (plans_dir / ".pipeline-active-OBPI-0.0.20-03.json").write_text(
                "not-json{", encoding="utf-8"
            )
            with self.assertRaises(GzCliError) as ctx:
                self._run_gate(project_root)
            self.assertIn("not readable JSON", str(ctx.exception))

    def test_marker_with_obpi_mismatch_is_rejected(self):
        from gzkit.commands.common import GzCliError

        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp)
            plans_dir = project_root / ".claude" / "plans"
            plans_dir.mkdir(parents=True, exist_ok=True)
            (plans_dir / ".pipeline-active-OBPI-0.0.20-03.json").write_text(
                json.dumps(
                    {
                        "obpi_id": "OBPI-OTHER",
                        "parent_adr": "ADR-0.0.20",
                        "current_stage": "ceremony",
                        "nonce": "00" * 16,
                        "started_at": "2026-05-08T00:00:00Z",
                    }
                ),
                encoding="utf-8",
            )
            with self.assertRaises(GzCliError) as ctx:
                self._run_gate(project_root)
            self.assertIn("obpi_id does not match", str(ctx.exception))

    def test_marker_with_parent_adr_mismatch_is_rejected(self):
        from gzkit.commands.common import GzCliError

        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp)
            _write_authentic_marker(
                project_root,
                "OBPI-0.0.20-03",
                "ADR-OTHER",  # mismatch with the gate's expected parent
            )
            with self.assertRaises(GzCliError) as ctx:
                self._run_gate(project_root)
            self.assertIn("parent_adr does not match", str(ctx.exception))

    def test_marker_with_missing_nonce_is_rejected(self):
        from gzkit.commands.common import GzCliError

        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp)
            plans_dir = project_root / ".claude" / "plans"
            plans_dir.mkdir(parents=True, exist_ok=True)
            (plans_dir / ".pipeline-active-OBPI-0.0.20-03.json").write_text(
                json.dumps(
                    {
                        "obpi_id": "OBPI-0.0.20-03",
                        "parent_adr": "ADR-0.0.20",
                        "current_stage": "ceremony",
                        "started_at": "2026-05-08T00:00:00Z",
                    }
                ),
                encoding="utf-8",
            )
            with self.assertRaises(GzCliError) as ctx:
                self._run_gate(project_root)
            self.assertIn("nonce is missing or malformed", str(ctx.exception))

    def test_marker_with_malformed_nonce_is_rejected(self):
        from gzkit.commands.common import GzCliError

        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp)
            _write_authentic_marker(
                project_root,
                "OBPI-0.0.20-03",
                "ADR-0.0.20",
                nonce="not-a-32-hex-string",
                emit_ledger_event=False,
            )
            with self.assertRaises(GzCliError) as ctx:
                self._run_gate(project_root)
            self.assertIn("nonce is missing or malformed", str(ctx.exception))

    def test_stale_marker_is_rejected(self):
        from gzkit.commands.common import GzCliError

        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp)
            _write_authentic_marker(
                project_root,
                "OBPI-0.0.20-03",
                "ADR-0.0.20",
                started_at="2020-01-01T00:00:00Z",
            )
            with self.assertRaises(GzCliError) as ctx:
                self._run_gate(project_root)
            self.assertIn("stale", str(ctx.exception))

    def test_marker_without_matching_ledger_event_is_rejected(self):
        from gzkit.commands.common import GzCliError

        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp)
            _write_authentic_marker(
                project_root,
                "OBPI-0.0.20-03",
                "ADR-0.0.20",
                emit_ledger_event=False,
            )
            with self.assertRaises(GzCliError) as ctx:
                self._run_gate(project_root)
            self.assertIn("pipeline_launched ledger event", str(ctx.exception))

    def test_security_sensitivity_refuses_agent_relayed_even_with_authentic_marker(self):
        from gzkit.commands.common import GzCliError

        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp)
            _write_authentic_marker(project_root, "OBPI-0.0.20-03", "ADR-0.0.20")
            with self.assertRaises(GzCliError) as ctx:
                self._run_gate(project_root, sensitivity="security")
            self.assertIn("sensitivity:security", str(ctx.exception))
            self.assertIn("interactive shell", str(ctx.exception))

    def test_foundation_kind_with_authentic_marker_returns_agent_relayed_post_434(self):
        """GHI #434: agent-relayed attestation IS accepted for foundation-kind
        when the marker is authentic. The marker authenticity hardening from
        GHI #412 mitigation #1 (nonce + ledger event witness + freshness)
        sufficiently raises the forgery bar; the additional foundation-kind
        refusal from #412 mitigation #2 was reverted because it forced N
        TTY sessions per ADR closeout for negligible trust gain over #1.
        ``sensitivity: security`` remains TTY-only — see
        ``test_security_sensitivity_refuses_agent_relayed_even_with_authentic_marker``.
        """
        from gzkit.commands.adr_audit import ATTESTATION_TYPE_AGENT_RELAYED

        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp)
            _write_authentic_marker(project_root, "OBPI-0.0.20-03", "ADR-0.0.20")
            self.assertEqual(
                self._run_gate(project_root, parent_kind="foundation"),
                ATTESTATION_TYPE_AGENT_RELAYED,
            )


if __name__ == "__main__":
    unittest.main()
