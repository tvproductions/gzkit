"""Tests for pointer-integrity validator (OBPI-0.0.33-03).

Covers:
    REQ-0.0.33-03-01 — `> See [path#anchor]` resolves + back-pointer present → no errors
    REQ-0.0.33-03-02 — Unresolved anchor → exit-3 ValidationError naming both halves
    REQ-0.0.33-03-03 — Missing `<!-- lifted-from: -->` back-pointer → exit-3 ValidationError
    REQ-0.0.33-03-04 — Non-blockquote link is NOT checked
    REQ-0.0.33-03-05 — validate_pointer_integrity importable from trust_audits

All tests use ``tempfile.TemporaryDirectory`` for sandbox isolation.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from gzkit.governance.trust_audits.pointer_integrity import (
    validate_pointer_integrity,
)
from gzkit.traceability import covers


def _make_tree(
    tmp: str,
    *,
    agents_content: str = "",
    claude_content: str = "",
    rule_content: str | None = None,
    extra_files: dict[str, str] | None = None,
) -> Path:
    """Seed a minimal project root.

    Creates AGENTS.md, CLAUDE.md, optional .claude/rules/test-rule.md, and any
    additional files in extra_files (path relative to root → content).
    """
    root = Path(tmp)
    (root / "AGENTS.md").write_text(agents_content, encoding="utf-8")
    (root / "CLAUDE.md").write_text(claude_content, encoding="utf-8")

    if rule_content is not None:
        rules_dir = root / ".claude" / "rules"
        rules_dir.mkdir(parents=True, exist_ok=True)
        (rules_dir / "test-rule.md").write_text(rule_content, encoding="utf-8")

    if extra_files:
        for rel_path, content in extra_files.items():
            p = root / rel_path
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content, encoding="utf-8")

    return root


class TestPointerResolves(unittest.TestCase):
    """Pointer with valid anchor + back-pointer present → no errors."""

    @covers("REQ-0.0.33-03-01")
    def test_resolved_pointer_with_backpointer_is_clean(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            agents = (
                "Some prose here.\n"
                "> See [`docs/rationale.md` § My Section]"
                "(docs/rationale.md#my-section) for details.\n"
            )
            rationale = (
                "<!-- lifted-from: AGENTS.md#my-section -->\n"
                "# Rationale\n\n## My Section\n\nbody text\n"
            )
            root = _make_tree(
                tmp,
                agents_content=agents,
                extra_files={"docs/rationale.md": rationale},
            )
            errors = validate_pointer_integrity(root)
            self.assertEqual(errors, [], f"Expected clean, got: {[e.message for e in errors]}")

    @covers("REQ-0.0.33-03-01")
    def test_resolved_pointer_in_claude_md(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            claude = "> See [`docs/x.md` § Heading One](docs/x.md#heading-one) for the rationale.\n"
            target = "<!-- lifted-from: CLAUDE.md#heading-one -->\n## Heading One\n\nbody\n"
            root = _make_tree(
                tmp,
                claude_content=claude,
                extra_files={"docs/x.md": target},
            )
            errors = validate_pointer_integrity(root)
            self.assertEqual(errors, [])

    @covers("REQ-0.0.33-03-01")
    def test_resolved_pointer_in_rules_dir(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            rule = "> See [`docs/r.md` § Foo Bar](../../docs/r.md#foo-bar) for details.\n"
            target = (
                "<!-- lifted-from: .claude/rules/test-rule.md#foo-bar -->\n## Foo Bar\n\nbody\n"
            )
            root = _make_tree(
                tmp,
                rule_content=rule,
                extra_files={"docs/r.md": target},
            )
            errors = validate_pointer_integrity(root)
            self.assertEqual(errors, [])

    @covers("REQ-0.0.33-03-01")
    def test_anchor_with_double_hyphens_slugifies(self) -> None:
        # Heading "Anti-vibing mantra & relationship" → slug must collapse separators.
        with tempfile.TemporaryDirectory() as tmp:
            agents = (
                "> See [`docs/r.md` § Anti-vibing](docs/r.md#anti-vibing-mantra--relationship) "
                "for details.\n"
            )
            target = (
                "<!-- lifted-from: AGENTS.md#anti-vibing-mantra--relationship -->\n"
                "## Anti-vibing mantra & relationship\n\nbody\n"
            )
            root = _make_tree(
                tmp,
                agents_content=agents,
                extra_files={"docs/r.md": target},
            )
            errors = validate_pointer_integrity(root)
            self.assertEqual(errors, [])


class TestUnresolvedAnchor(unittest.TestCase):
    """Pointer where path missing or anchor absent → exit-3 ValidationError."""

    @covers("REQ-0.0.33-03-02")
    def test_missing_destination_file_emits_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            agents = "> See [`docs/nope.md` § Missing](docs/nope.md#missing) for details.\n"
            root = _make_tree(tmp, agents_content=agents)
            errors = validate_pointer_integrity(root)
            self.assertEqual(len(errors), 1)
            self.assertEqual(errors[0].type, "pointer_anchors")

    @covers("REQ-0.0.33-03-02")
    def test_missing_anchor_emits_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            agents = "> See [`docs/r.md` § Missing](docs/r.md#missing-anchor) for details.\n"
            target = (
                "<!-- lifted-from: AGENTS.md#missing-anchor -->\n## Some Other Heading\n\nbody\n"
            )
            root = _make_tree(
                tmp,
                agents_content=agents,
                extra_files={"docs/r.md": target},
            )
            errors = validate_pointer_integrity(root)
            self.assertEqual(len(errors), 1)
            self.assertEqual(errors[0].type, "pointer_anchors")

    @covers("REQ-0.0.33-03-02")
    def test_error_message_names_both_source_and_destination(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            agents = (
                "line one\n> See [`docs/nope.md` § Missing](docs/nope.md#missing) for details.\n"
            )
            root = _make_tree(tmp, agents_content=agents)
            errors = validate_pointer_integrity(root)
            self.assertEqual(len(errors), 1)
            msg = errors[0].message
            self.assertIn("AGENTS.md", msg, "Error must name source file")
            self.assertIn("docs/nope.md", msg, "Error must name destination path")
            self.assertIn("missing", msg, "Error must name the anchor")

    @covers("REQ-0.0.33-03-02")
    def test_error_message_includes_source_line_number(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            agents = "line one\nline two\n> See [`docs/nope.md` § X](docs/nope.md#x) for details.\n"
            root = _make_tree(tmp, agents_content=agents)
            errors = validate_pointer_integrity(root)
            self.assertEqual(len(errors), 1)
            self.assertIn(":3", errors[0].message, "Error must name source line number")


class TestMissingBackPointer(unittest.TestCase):
    """Destination referenced by forward pointer but lacking lifted-from → exit-3."""

    @covers("REQ-0.0.33-03-03")
    def test_missing_back_pointer_emits_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            agents = "> See [`docs/r.md` § My Section](docs/r.md#my-section) for details.\n"
            # heading exists but no <!-- lifted-from: --> comment
            target = "# Rationale\n\n## My Section\n\nbody\n"
            root = _make_tree(
                tmp,
                agents_content=agents,
                extra_files={"docs/r.md": target},
            )
            errors = validate_pointer_integrity(root)
            self.assertEqual(len(errors), 1)
            self.assertEqual(errors[0].type, "pointer_anchors")
            self.assertIn("lifted-from", errors[0].message)
            self.assertIn("docs/r.md", errors[0].message)

    @covers("REQ-0.0.33-03-03")
    def test_matching_back_pointer_anywhere_in_destination_is_accepted(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            agents = "> See [`docs/r.md` § H](docs/r.md#h) for details.\n"
            target = "# Rationale\n\n## H\n\nbody\n\n<!-- lifted-from: AGENTS.md#h -->\n"
            root = _make_tree(
                tmp,
                agents_content=agents,
                extra_files={"docs/r.md": target},
            )
            errors = validate_pointer_integrity(root)
            self.assertEqual(errors, [])


class TestPointerResolvesRelativeToSource(unittest.TestCase):
    """A pointer resolves against its own file's directory, as a reader resolves it.

    GHI #931: joining the link onto the project root made the only accepted form
    the one that is a broken link in every markdown viewer.
    """

    @covers("REQ-0.0.33-03-01")
    def test_relative_pointer_from_nested_rule_resolves(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            rule = "> See [`docs/r.md` § Foo Bar](../../docs/r.md#foo-bar) for details.\n"
            target = (
                "<!-- lifted-from: .claude/rules/test-rule.md#foo-bar -->\n## Foo Bar\n\nbody\n"
            )
            root = _make_tree(tmp, rule_content=rule, extra_files={"docs/r.md": target})
            errors = validate_pointer_integrity(root)
            self.assertEqual(errors, [])

    @covers("REQ-0.0.33-03-02")
    def test_root_relative_pointer_from_nested_rule_is_unresolved(self) -> None:
        # From .claude/rules/, "docs/r.md" names .claude/rules/docs/r.md — which
        # is what a reader's markdown viewer resolves, and it does not exist.
        with tempfile.TemporaryDirectory() as tmp:
            rule = "> See [`docs/r.md` § Foo Bar](docs/r.md#foo-bar) for details.\n"
            target = (
                "<!-- lifted-from: .claude/rules/test-rule.md#foo-bar -->\n## Foo Bar\n\nbody\n"
            )
            root = _make_tree(tmp, rule_content=rule, extra_files={"docs/r.md": target})
            errors = validate_pointer_integrity(root)
            self.assertEqual(len(errors), 1)
            self.assertEqual(errors[0].type, "pointer_anchors")
            self.assertIn("does not exist", errors[0].message)

    @covers("REQ-0.0.33-03-01")
    def test_root_surface_pointer_still_resolves(self) -> None:
        # AGENTS.md sits at the root, so source-relative and root-relative agree.
        with tempfile.TemporaryDirectory() as tmp:
            agents = "> See [`docs/r.md` § H](docs/r.md#h) for details.\n"
            target = "<!-- lifted-from: AGENTS.md#h -->\n## H\n\nbody\n"
            root = _make_tree(tmp, agents_content=agents, extra_files={"docs/r.md": target})
            errors = validate_pointer_integrity(root)
            self.assertEqual(errors, [])


class TestBackPointerMustMatch(unittest.TestCase):
    """The back-pointer must name THIS source and anchor, not merely exist.

    GHI #932: a bare substring test let one `lifted-from` comment discharge the
    obligation for every pointer into that file — a presence check standing in
    for a state check.
    """

    @covers("REQ-0.0.33-03-03")
    def test_back_pointer_naming_a_different_source_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            agents = "> See [`docs/r.md` § H](docs/r.md#h) for details.\n"
            target = "## H\n\nbody\n\n<!-- lifted-from: totally/unrelated.md#nothing -->\n"
            root = _make_tree(tmp, agents_content=agents, extra_files={"docs/r.md": target})
            errors = validate_pointer_integrity(root)
            self.assertEqual(len(errors), 1)
            self.assertEqual(errors[0].type, "pointer_anchors")
            self.assertIn("AGENTS.md#h", errors[0].message)

    @covers("REQ-0.0.33-03-03")
    def test_back_pointer_with_wrong_anchor_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            agents = "> See [`docs/r.md` § H](docs/r.md#h) for details.\n"
            target = "## H\n\nbody\n\n<!-- lifted-from: AGENTS.md#some-other-anchor -->\n"
            root = _make_tree(tmp, agents_content=agents, extra_files={"docs/r.md": target})
            errors = validate_pointer_integrity(root)
            self.assertEqual(len(errors), 1)
            self.assertIn("AGENTS.md#h", errors[0].message)

    @covers("REQ-0.0.33-03-03")
    def test_one_destination_carries_a_back_pointer_per_incoming_source(self) -> None:
        # Two sources lift into one destination; each needs its own comment.
        with tempfile.TemporaryDirectory() as tmp:
            agents = "> See [`docs/r.md` § H](docs/r.md#h) for details.\n"
            rule = "> See [`docs/r.md` § H](../../docs/r.md#h) for details.\n"
            target = "## H\n\nbody\n\n<!-- lifted-from: AGENTS.md#h -->\n"
            root = _make_tree(
                tmp, agents_content=agents, rule_content=rule, extra_files={"docs/r.md": target}
            )
            errors = validate_pointer_integrity(root)
            self.assertEqual(len(errors), 1)
            self.assertIn(".claude/rules/test-rule.md#h", errors[0].message)

            both = target + "<!-- lifted-from: .claude/rules/test-rule.md#h -->\n"
            (root / "docs" / "r.md").write_text(both, encoding="utf-8")
            self.assertEqual(validate_pointer_integrity(root), [])


class TestNonBlockquoteNotChecked(unittest.TestCase):
    """A regular markdown link outside `> See [...]` blockquote is NOT checked."""

    @covers("REQ-0.0.33-03-04")
    def test_inline_link_not_checked(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            agents = (
                "See [`docs/nope.md` § X](docs/nope.md#x-anchor-does-not-resolve) "
                "in an inline paragraph.\n"
            )
            root = _make_tree(tmp, agents_content=agents)
            errors = validate_pointer_integrity(root)
            self.assertEqual(errors, [], "Inline (non-blockquote) links must not be validated")

    @covers("REQ-0.0.33-03-04")
    def test_blockquote_without_See_keyword_not_checked(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            agents = "> Aside note: [`docs/nope.md` § X](docs/nope.md#x) is unrelated.\n"
            root = _make_tree(tmp, agents_content=agents)
            errors = validate_pointer_integrity(root)
            self.assertEqual(
                errors,
                [],
                "Blockquote lines without `See` token must not be validated",
            )


class TestPackageReExport(unittest.TestCase):
    """validate_pointer_integrity resolves from trust_audits package re-export."""

    @covers("REQ-0.0.33-03-05")
    def test_validate_pointer_integrity_importable_from_trust_audits(self) -> None:
        from gzkit.governance.trust_audits import validate_pointer_integrity as fn

        self.assertTrue(callable(fn))

    @covers("REQ-0.0.33-03-05")
    def test_function_signature_accepts_path(self) -> None:
        import inspect

        sig = inspect.signature(validate_pointer_integrity)
        params = list(sig.parameters)
        self.assertEqual(
            params,
            ["project_root"],
            "Function must accept exactly project_root: Path",
        )

    @covers("REQ-0.0.33-03-05")
    def test_function_returns_list(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = _make_tree(tmp)
            result = validate_pointer_integrity(root)
            self.assertIsInstance(result, list)


class TestPointerAnchorsRoutesToExit3(unittest.TestCase):
    """REQ-0.0.33-03-02 / REQ-0.0.33-03-03: pointer_anchors breach exits 3, not 1.

    The REQs explicitly prescribe exit 3 on unresolved-anchor and
    missing-back-pointer findings. Without ``pointer_anchors`` registered in
    ``_POLICY_BREACH_ERROR_TYPES``, the CLI dispatch routes the error through
    ``_print_validation_result``'s non-policy branch and exits 1 — silently
    narrowing the REQ contract.
    """

    @covers("REQ-0.0.33-03-02")
    def test_error_type_registered_as_policy_breach(self) -> None:
        from gzkit.commands import validate_cmd

        self.assertIn(
            "pointer_anchors",
            validate_cmd._POLICY_BREACH_ERROR_TYPES,
            msg="pointer_anchors must route through the exit-3 policy-breach path per REQ-03-02/03",
        )

    @covers("REQ-0.0.33-03-03")
    def test_cli_dispatch_raises_systemexit_3_on_pointer_anchors_breach(self) -> None:
        import contextlib
        import io

        from gzkit.commands import validate_cmd
        from gzkit.core.validation_rules import ValidationError

        breach = ValidationError(
            type="pointer_anchors",
            artifact="AGENTS.md",
            message="unresolved pointer: docs/nope.md#missing",
        )
        with (
            contextlib.redirect_stdout(io.StringIO()),
            self.assertRaises(SystemExit) as ctx,
        ):
            validate_cmd._print_validation_result(
                errors=[breach],
                scopes=["pointer_anchors"],
                frontmatter_only=False,
            )
        self.assertEqual(ctx.exception.code, 3)


if __name__ == "__main__":
    unittest.main()
