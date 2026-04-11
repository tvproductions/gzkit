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
            mock_anchor.return_value = {"commit": "abc1234", "semver": "0.0.14"}

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
            mock_anchor.return_value = {"commit": "abc1234", "semver": "0.0.14"}

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
    """Test full happy path with mocked dependencies."""

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
    ):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            mock_root.return_value = root
            mock_init.return_value = _mock_config()
            mock_requires_human.return_value = True
            mock_anchor.return_value = {"commit": "abc1234", "semver": "0.0.14"}

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
            self.assertEqual(parsed["attestation_type"], "human")

            # Main ledger should have been appended
            ledger.append.assert_called_once()


@covers("OBPI-0.0.14-02")
class TestObpiCompleteCmdRollback(unittest.TestCase):
    """Test rollback when main ledger append fails."""

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
    ):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            mock_root.return_value = root
            mock_init.return_value = _mock_config()
            mock_requires_human.return_value = False
            mock_anchor.return_value = {"commit": "abc1234", "semver": "0.0.14"}

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


if __name__ == "__main__":
    unittest.main()
