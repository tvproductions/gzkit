"""Tests for gz validate --brief-command-shape (OBPI-0.0.63-07).

Covers:
    REQ-0.0.63-07-01 — compound Verification command → fails validation (exit 3)
    REQ-0.0.63-07-02 — all-shell-less Verification commands → passes (exit 0)
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from gzkit.traceability import covers


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


_BRIEF_TEMPLATE = """\
---
id: OBPI-0.0.63-07-test
parent: ADR-0.0.63-test
item: 1
lane: Heavy
status: Draft
---

# Test brief

## Verification

{verification_block}

## Acceptance Criteria

- [ ] REQ-0.0.63-07-01 [BEHAVIOR]: test requirement
"""

_ADR_OBPI_DIR = Path("docs") / "design" / "adr" / "foundation" / "ADR-0.0.63-test" / "obpis"


def _root_with_verification(verification_block: str) -> Path:
    tmp = Path(tempfile.mkdtemp())
    _write(
        tmp / _ADR_OBPI_DIR / "OBPI-0.0.63-07-test.md",
        _BRIEF_TEMPLATE.format(verification_block=verification_block),
    )
    return tmp


class TestBriefCommandShapeValidator(unittest.TestCase):
    """REQ-0.0.63-07-01 / REQ-0.0.63-07-02: audit_brief_command_shape()."""

    @covers("REQ-0.0.63-07-01")  # audit-exempt: regression-invariant-overlay rederived-validator-fail-closed
    def test_compound_and_command_fails_validation(self) -> None:
        """A brief with a && compound in Verification must produce a ValidationError."""
        from gzkit.governance.trust_audits.briefs import audit_brief_command_shape

        root = _root_with_verification("```bash\ntest -f x && echo ok\n```")
        errors = audit_brief_command_shape(root)
        self.assertEqual(len(errors), 1, f"Expected 1 error; got {len(errors)}: {errors}")
        self.assertEqual(errors[0].type, "brief_command_shape")
        self.assertIn("OBPI-0.0.63-07-test.md", errors[0].artifact)
        self.assertIn("test -f x && echo ok", errors[0].message)
        self.assertIn("Rewrite as separate single-program lines", errors[0].message)

    def test_pipe_operator_fails_validation(self) -> None:
        """A pipe in Verification block must be flagged."""
        from gzkit.governance.trust_audits.briefs import audit_brief_command_shape

        root = _root_with_verification("```bash\ngrep foo bar.txt | wc -l\n```")
        errors = audit_brief_command_shape(root)
        self.assertEqual(len(errors), 1)
        self.assertIn("grep foo bar.txt | wc -l", errors[0].message)

    def test_multiple_compound_commands_all_flagged(self) -> None:
        """Two compound commands in one brief must each produce an error."""
        from gzkit.governance.trust_audits.briefs import audit_brief_command_shape

        root = _root_with_verification("```bash\ntest -f x && echo ok\ngrep foo bar | wc -l\n```")
        errors = audit_brief_command_shape(root)
        self.assertEqual(len(errors), 2, f"Expected 2 errors; got {len(errors)}: {errors}")

    @covers("REQ-0.0.63-07-02")  # audit-exempt: regression-invariant-overlay rederived-validator-pass-path
    def test_shell_less_commands_pass_validation(self) -> None:
        """A brief with only shell-less commands must return no errors."""
        from gzkit.governance.trust_audits.briefs import audit_brief_command_shape

        root = _root_with_verification(
            "```bash\nuv run gz check\nuv run gz validate --documents\n```"
        )
        errors = audit_brief_command_shape(root)
        self.assertEqual(errors, [], f"Expected no errors; got {errors}")

    def test_quoted_pipe_not_flagged(self) -> None:
        """A pipe inside a quoted argument is data, not syntax — must not be flagged."""
        from gzkit.governance.trust_audits.briefs import audit_brief_command_shape

        root = _root_with_verification('```bash\npython -c "a | b"\n```')
        errors = audit_brief_command_shape(root)
        self.assertEqual(errors, [], f"Quoted pipe must not be flagged; got {errors}")

    def test_empty_verification_section_passes(self) -> None:
        """A brief with no fenced commands in Verification passes cleanly."""
        from gzkit.governance.trust_audits.briefs import audit_brief_command_shape

        root = _root_with_verification("")
        errors = audit_brief_command_shape(root)
        self.assertEqual(errors, [], f"Empty Verification must produce no errors; got {errors}")

    def test_no_adr_root_returns_empty(self) -> None:
        """When docs/design/adr/ does not exist, return empty list."""
        from gzkit.governance.trust_audits.briefs import audit_brief_command_shape

        with tempfile.TemporaryDirectory() as tmp:
            errors = audit_brief_command_shape(Path(tmp))
            self.assertEqual(errors, [])

    def test_completed_brief_with_compound_command_is_skipped(self) -> None:
        """A completed brief with a compound command must be skipped (authoring-time gate only)."""
        from gzkit.governance.trust_audits.briefs import audit_brief_command_shape

        completed_brief = _BRIEF_TEMPLATE.format(
            verification_block="```bash\ntest -f x && echo ok\n```"
        ).replace("status: Draft", "status: Completed")
        tmp = Path(tempfile.mkdtemp())
        _write(
            tmp / _ADR_OBPI_DIR / "OBPI-0.0.63-07-test.md",
            completed_brief,
        )
        errors = audit_brief_command_shape(tmp)
        self.assertEqual(errors, [], f"Completed brief must be skipped; got {errors}")


if __name__ == "__main__":
    unittest.main()
