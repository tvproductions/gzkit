"""CLI tests for ``gz justify``.

Covers OBPI-0.0.19-02 REQ-06 through REQ-12 (happy path, ADR rejection,
draft-slug precondition, --save auto-path, --output conflict, help surface,
exit-code discipline). Subprocess boundaries are mocked at the import site
in ``gzkit.justify.cli`` per the OBPI-01 precedent.
"""

from __future__ import annotations

import io
import re
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from datetime import UTC, datetime
from pathlib import Path
from unittest import mock

from gzkit.commands.justify_cmd import justify_cmd
from gzkit.justify.cli import (
    ADR_REJECTION_MESSAGE,
    DRAFT_SLUG_REQUIRED_MESSAGE,
    handle_justify,
)
from gzkit.justify.models import AnchorRef, AnchorResolutionError, EvidenceBundle
from gzkit.traceability import covers


def _invoke_justify(**kwargs: object) -> int:
    """Call ``justify_cmd``; capture the ``SystemExit`` it raises on non-zero.

    ``justify_cmd`` raises ``SystemExit(code)`` for non-zero exits because
    ``gzkit.cli.main`` swallows handler return values. Tests want the integer
    exit code, so this helper collapses both paths into a returned int.
    """
    try:
        return justify_cmd(**kwargs)  # type: ignore[arg-type]
    except SystemExit as exc:
        if isinstance(exc.code, int):
            return exc.code
        return 1


def _fake_anchor(identifier: str = "GHI-232") -> AnchorRef:
    return AnchorRef(
        kind="ghi",
        identifier=identifier,
        title="Mock anchor",
        body="Mock body referencing GHI-232",
        labels=(),
        author="octocat",
    )


def _fake_bundle(anchor: AnchorRef) -> EvidenceBundle:
    return EvidenceBundle(
        anchor=anchor,
        matching_rules=(),
        ledger_events=(),
        recent_commits=(),
        related_anchors=(),
        taxonomy_reference="docs/governance/model-regression-taxonomy.md",
        warnings=(),
    )


def _patch_substrate(anchor: AnchorRef | None = None):
    """Context-manager stack that patches resolve_anchor + gather_evidence."""
    anchor = anchor or _fake_anchor()
    resolver = mock.patch(
        "gzkit.justify.cli.resolve_anchor",
        return_value=anchor,
    )
    gatherer = mock.patch(
        "gzkit.justify.cli.gather_evidence",
        return_value=_fake_bundle(anchor),
    )
    return resolver, gatherer


class TestAdrRejection(unittest.TestCase):
    @covers("REQ-0.0.19-02-07")
    def test_exact_message_and_exit_one(self) -> None:
        err = io.StringIO()
        with redirect_stderr(err):
            code = _invoke_justify(anchor="ADR-0.0.19")
        self.assertEqual(code, 1)
        self.assertEqual(err.getvalue().strip(), ADR_REJECTION_MESSAGE)

    @covers("REQ-0.0.19-02-07")
    def test_case_insensitive_rejection(self) -> None:
        err = io.StringIO()
        with redirect_stderr(err):
            code = _invoke_justify(anchor="adr-0.0.19")
        self.assertEqual(code, 1)
        self.assertIn("justify reasons about change instances", err.getvalue())


class TestDraftSlugPrecondition(unittest.TestCase):
    @covers("REQ-0.0.19-02-08")
    def test_draft_with_save_missing_slug_exits_one(self) -> None:
        err = io.StringIO()
        with redirect_stderr(err):
            code = _invoke_justify(anchor=None, save=True, draft="proposal text")
        self.assertEqual(code, 1)
        self.assertIn(DRAFT_SLUG_REQUIRED_MESSAGE, err.getvalue())

    @covers("REQ-0.0.19-02-08")
    def test_draft_without_save_does_not_require_slug(self) -> None:
        resolver, gatherer = _patch_substrate(
            anchor=AnchorRef(
                kind="draft",
                identifier=None,
                title=None,
                body="proposal text",
                labels=(),
                author=None,
                draft_text="proposal text",
                draft_slug=None,
            )
        )
        out = io.StringIO()
        with resolver, gatherer, redirect_stdout(out):
            code = _invoke_justify(anchor=None, draft="proposal text")
        self.assertEqual(code, 0)


class TestHappyPaths(unittest.TestCase):
    @covers("REQ-0.0.19-02-06")
    def test_default_emits_scaffold_to_stdout(self) -> None:
        resolver, gatherer = _patch_substrate()
        out = io.StringIO()
        with resolver, gatherer, redirect_stdout(out):
            code = _invoke_justify(anchor="GHI-232")
        self.assertEqual(code, 0)
        rendered = out.getvalue()
        self.assertIn("# Walkthrough: GHI-232", rendered)
        h2_matches = re.findall(r"^## \d+\. ", rendered, flags=re.MULTILINE)
        self.assertEqual(len(h2_matches), 8)

    @covers("REQ-0.0.19-02-09")
    def test_save_writes_artifacts_justify_auto_path(self) -> None:
        resolver, gatherer = _patch_substrate()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixed = datetime(2026, 4, 22, 12, 34, 56, tzinfo=UTC)
            with resolver, gatherer:
                code = handle_justify(
                    anchor="GHI-232",
                    save=True,
                    output=None,
                    related=None,
                    draft=None,
                    draft_slug=None,
                    now=fixed,
                    project_root=root,
                )
            self.assertEqual(code, 0)
            artifact_dir = root / "artifacts" / "justify"
            self.assertTrue(artifact_dir.is_dir())
            files = sorted(artifact_dir.iterdir())
            self.assertEqual(len(files), 1)
            name = files[0].name
            self.assertTrue(name.startswith("GHI-232-"))
            self.assertTrue(name.endswith(".md"))
            self.assertIn("20260422T123456Z", name)
            body = files[0].read_text(encoding="utf-8")
            self.assertIn("# Walkthrough: GHI-232", body)

    @covers("REQ-0.0.19-02-06")
    def test_related_passed_through_as_list(self) -> None:
        resolver_ctx, gather_ctx = _patch_substrate()
        with resolver_ctx, gather_ctx as gather_mock, redirect_stdout(io.StringIO()):
            _invoke_justify(anchor="GHI-232", related="GHI-1, OBPI-0.0.19-02 ")
        _, kwargs = gather_mock.call_args
        self.assertEqual(kwargs["related"], ["GHI-1", "OBPI-0.0.19-02"])


class TestOutputPathConflict(unittest.TestCase):
    @covers("REQ-0.0.19-02-10")
    def test_output_path_exists_exits_one(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            existing = Path(tmp) / "scaffold.md"
            existing.write_text("previous content", encoding="utf-8")
            err = io.StringIO()
            with redirect_stderr(err):
                code = _invoke_justify(anchor="GHI-232", output=str(existing))
            self.assertEqual(code, 1)
            self.assertIn("output path already exists", err.getvalue())
            self.assertEqual(existing.read_text(encoding="utf-8"), "previous content")

    @covers("REQ-0.0.19-02-06")
    def test_output_path_new_writes_scaffold(self) -> None:
        resolver, gatherer = _patch_substrate()
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "new.md"
            with resolver, gatherer:
                code = _invoke_justify(anchor="GHI-232", output=str(target))
            self.assertEqual(code, 0)
            self.assertIn("# Walkthrough: GHI-232", target.read_text(encoding="utf-8"))


class TestExitCodeDiscipline(unittest.TestCase):
    @covers("REQ-0.0.19-02-06")
    def test_anchor_resolution_error_maps_to_exit_two(self) -> None:
        with mock.patch(
            "gzkit.justify.cli.resolve_anchor",
            side_effect=AnchorResolutionError("anchor not found"),
        ):
            err = io.StringIO()
            with redirect_stderr(err):
                code = _invoke_justify(anchor="GHI-9999")
        self.assertEqual(code, 2)
        self.assertIn("anchor not found", err.getvalue())

    @covers("REQ-0.0.19-02-06")
    def test_anchor_value_error_maps_to_exit_one(self) -> None:
        with mock.patch(
            "gzkit.justify.cli.resolve_anchor",
            side_effect=ValueError("bad anchor"),
        ):
            err = io.StringIO()
            with redirect_stderr(err):
                code = _invoke_justify(anchor="bad-anchor-shape")
        self.assertEqual(code, 1)
        self.assertIn("bad anchor", err.getvalue())

    @covers("REQ-0.0.19-02-06")
    def test_missing_anchor_and_draft_exits_one(self) -> None:
        err = io.StringIO()
        with redirect_stderr(err):
            code = _invoke_justify(anchor=None)
        self.assertEqual(code, 1)
        self.assertIn("anchor or --draft is required", err.getvalue())


class TestDeterminism(unittest.TestCase):
    @covers("REQ-0.0.19-02-04")
    def test_identical_inputs_produce_identical_outputs(self) -> None:
        resolver, gatherer = _patch_substrate()
        fixed = datetime(2026, 4, 22, 0, 0, 0, tzinfo=UTC)
        out1 = io.StringIO()
        out2 = io.StringIO()
        with resolver, gatherer, redirect_stdout(out1):
            handle_justify(
                anchor="GHI-232",
                save=False,
                output=None,
                related=None,
                draft=None,
                draft_slug=None,
                now=fixed,
            )
        resolver2, gatherer2 = _patch_substrate()
        with resolver2, gatherer2, redirect_stdout(out2):
            handle_justify(
                anchor="GHI-232",
                save=False,
                output=None,
                related=None,
                draft=None,
                draft_slug=None,
                now=fixed,
            )
        self.assertEqual(out1.getvalue(), out2.getvalue())


class TestCliAuditCoverage(unittest.TestCase):
    @covers("REQ-0.0.19-02-12")
    def test_justify_registered_in_doc_coverage_manifest(self) -> None:
        from gzkit.doc_coverage.manifest import load_manifest

        manifest = load_manifest(Path.cwd())
        self.assertIn("justify", manifest.commands)
        entry = manifest.commands["justify"]
        surfaces = entry.surfaces.model_dump()
        self.assertTrue(surfaces["manpage"], "Gate 3 stub requires manpage true")
        self.assertTrue(surfaces["index_entry"], "Gate 3 stub requires index_entry true")
        self.assertTrue(surfaces["docstring"], "docstring surface always required")

    @covers("REQ-0.0.19-02-12")
    def test_justify_command_doc_and_index_exist(self) -> None:
        command_doc = Path("docs/user/manpages/justify.md")
        self.assertTrue(command_doc.is_file(), "command doc stub must exist for Gate 3")
        index_text = Path("docs/user/manpages/index.md").read_text(encoding="utf-8")
        self.assertIn("justify.md", index_text, "justify must appear in commands index")


class TestHelpSurface(unittest.TestCase):
    @covers("REQ-0.0.19-02-11")
    def test_help_lists_anchor_and_all_flags(self) -> None:
        from gzkit.cli.main import _get_parser

        parser = _get_parser()
        help_io = io.StringIO()
        try:
            subparsers_action = next(
                action
                for action in parser._actions  # noqa: SLF001
                if "justify" in (getattr(action, "choices", None) or ())
            )
        except StopIteration:  # pragma: no cover — registration missing
            self.fail("justify subcommand not registered under top-level parser")
        justify_parser = subparsers_action.choices["justify"]
        justify_parser.print_help(file=help_io)
        text = help_io.getvalue()
        self.assertIn("anchor", text)
        for flag in ("--save", "--output", "--related", "--draft", "--draft-slug"):
            self.assertIn(flag, text, f"help missing {flag}")
        self.assertRegex(text.lower(), r"exit code")
        self.assertRegex(text.lower(), r"example")


if __name__ == "__main__":
    unittest.main()
