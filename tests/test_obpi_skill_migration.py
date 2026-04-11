"""Static verification tests for OBPI-0.0.14-03 — skill migration to CLI commands.

These tests verify that the gz-obpi-pipeline and gz-obpi-lock skills delegate
to gz obpi CLI commands and contain zero direct Write/Edit tool references
to governance paths.
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path


def covers(target: str):  # noqa: D401
    """Identity decorator linking test to ADR/OBPI target for traceability."""

    def _identity(obj):  # type: ignore[no-untyped-def]
        return obj

    return _identity


# ---------------------------------------------------------------------------
# Resolve skill file paths relative to project root
# ---------------------------------------------------------------------------

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_PIPELINE_SKILL = _PROJECT_ROOT / ".claude" / "skills" / "gz-obpi-pipeline" / "SKILL.md"
_PIPELINE_DISPATCH = _PROJECT_ROOT / ".claude" / "skills" / "gz-obpi-pipeline" / "DISPATCH.md"
_LOCK_SKILL = _PROJECT_ROOT / ".claude" / "skills" / "gz-obpi-lock" / "SKILL.md"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# Pipeline skill — Stage 1 delegates to gz obpi lock claim
# ---------------------------------------------------------------------------


@covers("OBPI-0.0.14-03")
class TestPipelineStage1LockClaim(unittest.TestCase):
    """REQ-0.0.14-03-01: Pipeline Stage 1 instructs gz obpi lock claim."""

    @covers("REQ-0.0.14-03-01")
    def test_pipeline_references_gz_obpi_lock_claim(self):
        content = _read(_PIPELINE_SKILL)
        matches = re.findall(r"gz obpi lock claim", content)
        self.assertGreater(len(matches), 0, "Pipeline SKILL.md must reference 'gz obpi lock claim'")


# ---------------------------------------------------------------------------
# Pipeline skill — Stage 5 delegates to gz obpi complete
# ---------------------------------------------------------------------------


@covers("OBPI-0.0.14-03")
class TestPipelineStage5Complete(unittest.TestCase):
    """REQ-0.0.14-03-02: Pipeline Stage 5 instructs gz obpi complete."""

    @covers("REQ-0.0.14-03-02")
    def test_pipeline_references_gz_obpi_complete(self):
        content = _read(_PIPELINE_SKILL)
        matches = re.findall(r"gz obpi complete", content)
        self.assertGreater(len(matches), 0, "Pipeline SKILL.md must reference 'gz obpi complete'")


# ---------------------------------------------------------------------------
# Pipeline skill — Stage 5 delegates to gz obpi lock release
# ---------------------------------------------------------------------------


@covers("OBPI-0.0.14-03")
class TestPipelineStage5LockRelease(unittest.TestCase):
    """REQ-0.0.14-03-03: Pipeline Stage 5 instructs gz obpi lock release."""

    @covers("REQ-0.0.14-03-03")
    def test_pipeline_references_gz_obpi_lock_release(self):
        content = _read(_PIPELINE_SKILL)
        matches = re.findall(r"gz obpi lock release", content)
        self.assertGreater(
            len(matches), 0, "Pipeline SKILL.md must reference 'gz obpi lock release'"
        )


# ---------------------------------------------------------------------------
# Lock skill — delegates entirely to gz obpi lock subcommands
# ---------------------------------------------------------------------------


@covers("OBPI-0.0.14-03")
class TestLockSkillDelegation(unittest.TestCase):
    """REQ-0.0.14-03-04: Lock skill delegates to gz obpi lock subcommands."""

    @covers("REQ-0.0.14-03-04")
    def test_lock_skill_references_gz_obpi_lock(self):
        content = _read(_LOCK_SKILL)
        matches = re.findall(r"gz obpi lock", content)
        self.assertGreater(len(matches), 0, "Lock SKILL.md must reference 'gz obpi lock'")

    @covers("REQ-0.0.14-03-04")
    def test_lock_skill_covers_all_subcommands(self):
        content = _read(_LOCK_SKILL)
        for sub in ("claim", "release", "check", "list"):
            self.assertIn(
                f"gz obpi lock {sub}",
                content,
                f"Lock SKILL.md must reference 'gz obpi lock {sub}'",
            )


# ---------------------------------------------------------------------------
# No fallback direct-write language
# ---------------------------------------------------------------------------


@covers("OBPI-0.0.14-03")
class TestNoFallbackDirectWrites(unittest.TestCase):
    """REQ-0.0.14-03-05: No fallback direct-write language in skills."""

    @covers("REQ-0.0.14-03-05")
    def test_pipeline_no_write_tool_to_locks(self):
        content = _read(_PIPELINE_SKILL)
        # Match "Write" tool usage targeting lock paths
        write_to_locks = re.findall(r"Write.*\.gzkit/locks", content, re.IGNORECASE)
        self.assertEqual(
            len(write_to_locks), 0, "Pipeline must not instruct Write to .gzkit/locks/"
        )

    @covers("REQ-0.0.14-03-05")
    def test_lock_skill_no_write_tool_to_locks(self):
        content = _read(_LOCK_SKILL)
        write_to_locks = re.findall(r"Write.*\.gzkit/locks", content, re.IGNORECASE)
        self.assertEqual(
            len(write_to_locks), 0, "Lock skill must not instruct Write to .gzkit/locks/"
        )


# ---------------------------------------------------------------------------
# Pipeline stage structure unchanged (5 stages)
# ---------------------------------------------------------------------------


@covers("OBPI-0.0.14-03")
class TestPipelineStageCount(unittest.TestCase):
    """REQ-0.0.14-03-06: Pipeline stage structure unchanged (5 stages)."""

    @covers("REQ-0.0.14-03-06")
    def test_pipeline_has_five_stages(self):
        content = _read(_PIPELINE_SKILL)
        # Look for Stage N headers or numbered stage references
        stage_headers = re.findall(r"Stage\s+(\d+)", content)
        unique_stages = sorted({int(s) for s in stage_headers})
        for expected in (1, 2, 3, 4, 5):
            self.assertIn(expected, unique_stages, f"Pipeline must reference Stage {expected}")


# ---------------------------------------------------------------------------
# Abort/handoff instructs gz obpi lock release --force
# ---------------------------------------------------------------------------


@covers("OBPI-0.0.14-03")
class TestAbortHandoff(unittest.TestCase):
    """REQ-0.0.14-03-07: Abort/handoff instructs gz obpi lock release --force."""

    @covers("REQ-0.0.14-03-07")
    def test_pipeline_references_release_force(self):
        content = _read(_PIPELINE_SKILL)
        matches = re.findall(r"release\s+--force", content)
        self.assertGreater(len(matches), 0, "Pipeline must reference 'release --force' for abort")


# ---------------------------------------------------------------------------
# Zero Write tool references to .gzkit/locks/ or .lock.json
# ---------------------------------------------------------------------------


@covers("OBPI-0.0.14-03")
class TestZeroWriteToLockPaths(unittest.TestCase):
    """REQ-0.0.14-03-08: Zero Write tool references to lock paths."""

    @covers("REQ-0.0.14-03-08")
    def test_pipeline_no_write_to_lock_json(self):
        content = _read(_PIPELINE_SKILL)
        hits = re.findall(r"Write.*\.lock\.json", content, re.IGNORECASE)
        self.assertEqual(len(hits), 0, "Pipeline must not Write to .lock.json files")

    @covers("REQ-0.0.14-03-08")
    def test_lock_skill_no_write_to_lock_json(self):
        content = _read(_LOCK_SKILL)
        hits = re.findall(r"Write.*\.lock\.json", content, re.IGNORECASE)
        self.assertEqual(len(hits), 0, "Lock skill must not Write to .lock.json files")

    @covers("REQ-0.0.14-03-08")
    def test_dispatch_no_write_to_lock_json(self):
        # DISPATCH.md consolidated into SKILL.md — verify same invariant there
        content = _read(_PIPELINE_SKILL)
        hits = re.findall(r"Write.*\.lock\.json", content, re.IGNORECASE)
        self.assertEqual(len(hits), 0, "Pipeline skill must not Write to .lock.json files")


# ---------------------------------------------------------------------------
# Zero Edit tool references to brief status in pipeline Stage 5
# ---------------------------------------------------------------------------


@covers("OBPI-0.0.14-03")
class TestZeroEditBriefStatus(unittest.TestCase):
    """REQ-0.0.14-03-09: Zero Edit tool refs to brief status in Stage 5."""

    @covers("REQ-0.0.14-03-09")
    def test_pipeline_no_edit_brief_status(self):
        content = _read(_PIPELINE_SKILL)
        # Check for Edit tool instructions targeting brief status fields
        edit_status = re.findall(r"Edit.*Brief Status", content, re.IGNORECASE)
        self.assertEqual(len(edit_status), 0, "Pipeline must not Edit brief status directly")

    @covers("REQ-0.0.14-03-09")
    def test_pipeline_no_edit_frontmatter_status(self):
        content = _read(_PIPELINE_SKILL)
        edit_fm = re.findall(r"Edit.*status:\s*(Draft|Completed)", content, re.IGNORECASE)
        self.assertEqual(len(edit_fm), 0, "Pipeline must not Edit frontmatter status directly")


# ---------------------------------------------------------------------------
# Each skill references gz obpi subcommands for delegated operations
# ---------------------------------------------------------------------------


@covers("OBPI-0.0.14-03")
class TestSkillsReferenceGzObpi(unittest.TestCase):
    """REQ-0.0.14-03-10: Skills reference gz obpi subcommands."""

    @covers("REQ-0.0.14-03-10")
    def test_pipeline_references_gz_obpi(self):
        content = _read(_PIPELINE_SKILL)
        matches = re.findall(r"gz obpi", content)
        self.assertGreater(len(matches), 0, "Pipeline must reference 'gz obpi' commands")

    @covers("REQ-0.0.14-03-10")
    def test_lock_skill_references_gz_obpi(self):
        content = _read(_LOCK_SKILL)
        matches = re.findall(r"gz obpi", content)
        self.assertGreater(len(matches), 0, "Lock skill must reference 'gz obpi' commands")


# ---------------------------------------------------------------------------
# Pipeline tool-use log shows Bash calls to gz obpi, not Write/Edit
# ---------------------------------------------------------------------------


@covers("OBPI-0.0.14-03")
class TestPipelineToolUsePattern(unittest.TestCase):
    """REQ-0.0.14-03-11: Pipeline instructs Bash calls to gz obpi, not Write/Edit to governance."""

    @covers("REQ-0.0.14-03-11")
    def test_pipeline_instructs_gz_obpi_via_bash(self):
        content = _read(_PIPELINE_SKILL)
        # Pipeline must instruct gz obpi commands (inline or code blocks)
        # These are Bash-executed commands, not Write/Edit tool calls
        gz_obpi_refs = re.findall(r"(?:uv run )?gz obpi (?:lock |complete)", content)
        self.assertGreater(
            len(gz_obpi_refs),
            0,
            "Pipeline must instruct 'gz obpi' CLI commands (Bash-style execution)",
        )

    @covers("REQ-0.0.14-03-11")
    def test_pipeline_no_write_edit_tool_to_governance_in_code_blocks(self):
        content = _read(_PIPELINE_SKILL)
        # Extract all code blocks and verify none instruct Write/Edit to governance paths
        code_blocks = re.findall(r"```[^`]*```", content, re.DOTALL)
        for block in code_blocks:
            write_gov = re.findall(
                r"(Write|Edit).*\.(gzkit|lock\.json|obpi-audit)", block, re.IGNORECASE
            )
            self.assertEqual(
                len(write_gov),
                0,
                f"Code block must not instruct Write/Edit to governance paths: {block[:80]}",
            )

    @covers("REQ-0.0.14-03-11")
    def test_dispatch_code_blocks_use_gz_obpi(self):
        # DISPATCH.md consolidated into SKILL.md — verify same invariant there
        content = _read(_PIPELINE_SKILL)
        gz_obpi_refs = re.findall(r"gz obpi", content)
        self.assertGreater(
            len(gz_obpi_refs),
            0,
            "Pipeline skill must reference 'gz obpi' commands",
        )


# ---------------------------------------------------------------------------
# Pipeline produces same ledger events as pre-migration flow
# ---------------------------------------------------------------------------


@covers("OBPI-0.0.14-03")
class TestPipelineLedgerEventParity(unittest.TestCase):
    """REQ-0.0.14-03-12: Pipeline references commands that emit expected ledger events."""

    @covers("REQ-0.0.14-03-12")
    def test_pipeline_references_lock_claim_which_emits_ledger_event(self):
        """Lock claim is referenced in pipeline and its event emission is tested in OBPI-01."""
        content = _read(_PIPELINE_SKILL)
        self.assertIn("gz obpi lock claim", content)
        # The command itself emits obpi_lock_claimed — tested in test_obpi_lock_cmd.py

    @covers("REQ-0.0.14-03-12")
    def test_pipeline_references_lock_release_which_emits_ledger_event(self):
        """Lock release is referenced in pipeline and its event emission is tested in OBPI-01."""
        content = _read(_PIPELINE_SKILL)
        self.assertIn("gz obpi lock release", content)
        # The command itself emits obpi_lock_released — tested in test_obpi_lock_cmd.py

    @covers("REQ-0.0.14-03-12")
    def test_pipeline_references_complete_which_emits_receipt(self):
        """Complete is referenced in pipeline and its receipt emission is tested in OBPI-02."""
        content = _read(_PIPELINE_SKILL)
        self.assertIn("gz obpi complete", content)
        # The command itself emits obpi_receipt_emitted — tested in test_obpi_complete_cmd.py


if __name__ == "__main__":
    unittest.main()
