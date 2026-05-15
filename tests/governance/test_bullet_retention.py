"""Tests for bullet retention validator (OBPI-0.0.33-01).

Covers:
    REQ-0.0.33-01-01 — Mechanical/Promotable bullet present in surface → no errors
    REQ-0.0.33-01-02 — Mechanical/Promotable bullet absent from surface → exit-3 ValidationError
    REQ-0.0.33-01-03 — Judgment/Ambiguous bullets are NOT enforced
    REQ-0.0.33-01-04 — validate_bullet_retention resolves from trust_audits re-export
    REQ-0.0.33-01-05 — --bullet-retention flag registered in CLI

All tests use ``tempfile.TemporaryDirectory`` for sandbox isolation; never
write to the live repo root.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from gzkit.governance.trust_audits.bullet_retention import validate_bullet_retention
from gzkit.traceability import covers

# ---------------------------------------------------------------------------
# Minimal synthetic scorecard tables
# ---------------------------------------------------------------------------

_SCORECARD_MECHANICAL = """\
| # | Rule | Score | Notes |
|---|------|-------|-------|
| 1 | use uv run for commands | **Mechanical** | enforced by hook |
"""

_SCORECARD_PROMOTABLE = """\
| # | Rule | Score | Notes |
|---|------|-------|-------|
| 1 | top-level imports only | **Promotable** | partially enforced |
"""

_SCORECARD_JUDGMENT = """\
| # | Rule | Score | Notes |
|---|------|-------|-------|
| 1 | read agents before work | **Judgment** | pre-work discipline |
"""

_SCORECARD_AMBIGUOUS = """\
| # | Rule | Score | Notes |
|---|------|-------|-------|
| 1 | some ambiguous rule | **Ambiguous** | unclear scope |
"""

_SCORECARD_MIXED = """\
| # | Rule | Score | Notes |
|---|------|-------|-------|
| 1 | use uv run for commands | **Mechanical** | enforced by hook |
| 2 | read agents before work | **Judgment** | pre-work discipline |
| 3 | top-level imports only | **Promotable** | partially enforced |
"""


def _make_tree(
    tmp: str,
    scorecard_content: str,
    agents_content: str = "",
    claude_content: str = "",
    rule_content: str | None = None,
) -> Path:
    """Seed a minimal project root for bullet-retention tests.

    Creates:
      docs/governance/advisory-rules-audit.md  ← scorecard
      AGENTS.md                                 ← per-turn surface (optional body)
      CLAUDE.md                                 ← per-turn surface (optional body)
      .claude/rules/test-rule.md               ← per-turn rule (when rule_content given)
    """
    root = Path(tmp)
    scorecard_path = root / "docs" / "governance" / "advisory-rules-audit.md"
    scorecard_path.parent.mkdir(parents=True, exist_ok=True)
    scorecard_path.write_text(scorecard_content, encoding="utf-8")

    (root / "AGENTS.md").write_text(agents_content, encoding="utf-8")
    (root / "CLAUDE.md").write_text(claude_content, encoding="utf-8")

    if rule_content is not None:
        rules_dir = root / ".claude" / "rules"
        rules_dir.mkdir(parents=True, exist_ok=True)
        (rules_dir / "test-rule.md").write_text(rule_content, encoding="utf-8")

    return root


class TestBulletPresentReturnsNoErrors(unittest.TestCase):
    """Mechanical or Promotable bullet present verbatim in surface → no ValidationError."""

    @covers("REQ-0.0.33-01-01")
    def test_mechanical_bullet_in_agents_md_is_clean(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = _make_tree(
                tmp,
                scorecard_content=_SCORECARD_MECHANICAL,
                agents_content="use uv run for commands when executing Python",
            )
            errors = validate_bullet_retention(root)
            self.assertEqual(
                errors,
                [],
                "A Mechanical bullet present verbatim in AGENTS.md must produce no errors",
            )

    @covers("REQ-0.0.33-01-01")
    def test_promotable_bullet_in_claude_md_is_clean(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = _make_tree(
                tmp,
                scorecard_content=_SCORECARD_PROMOTABLE,
                claude_content="top-level imports only — standard library first",
            )
            errors = validate_bullet_retention(root)
            self.assertEqual(errors, [], "A Promotable bullet in CLAUDE.md must produce no errors")

    @covers("REQ-0.0.33-01-01")
    def test_bullet_in_rules_dir_is_clean(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = _make_tree(
                tmp,
                scorecard_content=_SCORECARD_MECHANICAL,
                rule_content="use uv run for commands in all shell invocations",
            )
            errors = validate_bullet_retention(root)
            self.assertEqual(
                errors,
                [],
                "A Mechanical bullet found under .claude/rules/** must produce no errors",
            )

    @covers("REQ-0.0.33-01-01")
    def test_bullet_with_different_surrounding_whitespace_matches(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = _make_tree(
                tmp,
                scorecard_content=_SCORECARD_MECHANICAL,
                agents_content="  -  use uv run for commands  (binding)  ",
            )
            errors = validate_bullet_retention(root)
            self.assertEqual(
                errors,
                [],
                "Whitespace and bullet-marker variation must not prevent a match",
            )


class TestBulletAbsentReturnsError(unittest.TestCase):
    """Mechanical or Promotable bullet absent from per-turn surface → exit-3 ValidationError."""

    @covers("REQ-0.0.33-01-02")
    def test_missing_mechanical_bullet_emits_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = _make_tree(
                tmp,
                scorecard_content=_SCORECARD_MECHANICAL,
                agents_content="this surface does not contain the rule",
            )
            errors = validate_bullet_retention(root)
            self.assertEqual(len(errors), 1, "Exactly one error expected for one missing bullet")

    @covers("REQ-0.0.33-01-02")
    def test_missing_bullet_error_type_is_bullet_retention(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = _make_tree(
                tmp,
                scorecard_content=_SCORECARD_MECHANICAL,
                agents_content="unrelated text",
            )
            errors = validate_bullet_retention(root)
            self.assertEqual(errors[0].type, "bullet_retention")

    @covers("REQ-0.0.33-01-02")
    def test_missing_bullet_error_names_the_bullet_text(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = _make_tree(
                tmp,
                scorecard_content=_SCORECARD_MECHANICAL,
                agents_content="unrelated text",
            )
            errors = validate_bullet_retention(root)
            self.assertIn(
                "use uv run for commands",
                errors[0].message,
                "Error message must name the missing bullet text",
            )

    @covers("REQ-0.0.33-01-02")
    def test_missing_bullet_error_names_classification(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = _make_tree(
                tmp,
                scorecard_content=_SCORECARD_MECHANICAL,
                agents_content="unrelated text",
            )
            errors = validate_bullet_retention(root)
            self.assertIn(
                "Mechanical",
                errors[0].message,
                "Error message must name the source classification",
            )

    @covers("REQ-0.0.33-01-02")
    def test_missing_promotable_bullet_also_emits_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = _make_tree(
                tmp,
                scorecard_content=_SCORECARD_PROMOTABLE,
                agents_content="unrelated content only",
            )
            errors = validate_bullet_retention(root)
            self.assertEqual(len(errors), 1)
            self.assertEqual(errors[0].type, "bullet_retention")

    @covers("REQ-0.0.33-01-02")
    def test_empty_surface_corpus_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = _make_tree(
                tmp,
                scorecard_content=_SCORECARD_MECHANICAL,
            )
            errors = validate_bullet_retention(root)
            self.assertGreater(
                len(errors),
                0,
                "Empty surface corpus must not silently pass for enforced bullets",
            )


class TestJudgmentAndAmbiguousNotEnforced(unittest.TestCase):
    """Judgment/Ambiguous bullets are NOT enforced regardless of surface content."""

    @covers("REQ-0.0.33-01-03")
    def test_judgment_bullet_absent_from_surface_is_not_flagged(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = _make_tree(
                tmp,
                scorecard_content=_SCORECARD_JUDGMENT,
                agents_content="this surface mentions nothing about the judgment rule",
            )
            errors = validate_bullet_retention(root)
            self.assertEqual(
                errors,
                [],
                "Judgment bullets must not be enforced even when absent from the surface",
            )

    @covers("REQ-0.0.33-01-03")
    def test_ambiguous_bullet_absent_from_surface_is_not_flagged(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = _make_tree(
                tmp,
                scorecard_content=_SCORECARD_AMBIGUOUS,
                agents_content="surface does not contain ambiguous content",
            )
            errors = validate_bullet_retention(root)
            self.assertEqual(
                errors,
                [],
                "Ambiguous bullets must not be enforced",
            )

    @covers("REQ-0.0.33-01-03")
    def test_mixed_scorecard_only_enforces_mechanical_and_promotable(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            # Only Mechanical and Promotable bullets present; Judgment absent
            root = _make_tree(
                tmp,
                scorecard_content=_SCORECARD_MIXED,
                agents_content=(
                    "use uv run for commands and top-level imports only"
                    " — both Mechanical/Promotable bullets satisfied here"
                ),
            )
            errors = validate_bullet_retention(root)
            self.assertEqual(
                errors,
                [],
                "Mixed scorecard: only enforced bullets need to be in the surface",
            )

    @covers("REQ-0.0.33-01-03")
    def test_mixed_scorecard_still_errors_when_enforced_bullet_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = _make_tree(
                tmp,
                scorecard_content=_SCORECARD_MIXED,
                agents_content="read agents before work — only the judgment rule is here",
            )
            errors = validate_bullet_retention(root)
            self.assertGreater(
                len(errors),
                0,
                "Missing Mechanical/Promotable bullets must still emit errors",
            )
            for err in errors:
                self.assertEqual(err.type, "bullet_retention")


class TestPackageReExport(unittest.TestCase):
    """validate_bullet_retention resolves from the trust_audits package re-export."""

    @covers("REQ-0.0.33-01-04")
    def test_validate_bullet_retention_importable_from_trust_audits(self) -> None:
        from gzkit.governance.trust_audits import validate_bullet_retention as fn

        self.assertTrue(callable(fn))

    @covers("REQ-0.0.33-01-04")
    def test_function_signature_accepts_path(self) -> None:
        import inspect

        sig = inspect.signature(validate_bullet_retention)
        params = list(sig.parameters)
        self.assertEqual(
            params,
            ["project_root"],
            "Function must accept exactly project_root: Path",
        )

    @covers("REQ-0.0.33-01-04")
    def test_function_returns_list(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = _make_tree(tmp, scorecard_content="no table here\n")
            result = validate_bullet_retention(root)
            self.assertIsInstance(result, list)


class TestCLIFlagRegistered(unittest.TestCase):
    """--bullet-retention appears in gz validate --help output."""

    @covers("REQ-0.0.33-01-05")
    def test_bullet_retention_flag_in_help(self) -> None:
        import io
        from contextlib import redirect_stderr, redirect_stdout

        from gzkit.cli import main

        output = io.StringIO()
        try:
            with redirect_stdout(output), redirect_stderr(output):
                main(["validate", "--help"])
        except SystemExit:
            pass
        help_text = output.getvalue()
        self.assertIn(
            "--bullet-retention",
            help_text,
            "gz validate --bullet-retention must be registered in CLI",
        )


if __name__ == "__main__":
    unittest.main()
