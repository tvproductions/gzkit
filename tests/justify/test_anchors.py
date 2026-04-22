"""Anchor resolver tests for gzkit.justify.anchors."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from gzkit.justify.anchors import resolve_anchor
from gzkit.justify.models import AnchorResolutionError
from gzkit.traceability import covers


class TestResolveGhiErrors(unittest.TestCase):
    @covers("REQ-0.0.19-01-04")
    def test_resolve_ghi_nonzero_raises_anchor_resolution_error(self) -> None:
        with (
            patch(
                "gzkit.justify.anchors.run_exec",
                return_value=(1, "", "gh: authentication required"),
            ),
            self.assertRaises(AnchorResolutionError) as ctx,
        ):
            resolve_anchor("GHI-42", project_root=Path("/tmp"))
        self.assertIn("authentication required", str(ctx.exception))
        self.assertIn("rc=1", str(ctx.exception))

    @covers("REQ-0.0.19-01-04")
    def test_resolve_ghi_empty_stdout_raises(self) -> None:
        with (
            patch("gzkit.justify.anchors.run_exec", return_value=(0, "   ", "")),
            self.assertRaises(AnchorResolutionError),
        ):
            resolve_anchor("GHI-1", project_root=Path("/tmp"))

    @covers("REQ-0.0.19-01-04")
    def test_resolve_ghi_never_uses_shell_true(self) -> None:
        recorded: dict[str, object] = {}

        def fake(cmd: list[str], cwd: Path, timeout: int | None = None) -> tuple[int, str, str]:
            recorded["cmd"] = cmd
            recorded["cwd"] = cwd
            recorded["timeout"] = timeout
            return (
                0,
                json.dumps(
                    {"number": 1, "title": "t", "body": "b", "labels": [], "author": {"login": "x"}}
                ),
                "",
            )

        with patch("gzkit.justify.anchors.run_exec", side_effect=fake):
            resolve_anchor("GHI-1", project_root=Path("/tmp"))

        cmd = recorded["cmd"]
        self.assertIsInstance(cmd, list)
        assert isinstance(cmd, list)
        self.assertEqual(cmd[0], "gh")
        self.assertIn("--json", cmd)


class TestResolveGhi(unittest.TestCase):
    @covers("REQ-0.0.19-01-03")
    def test_resolve_ghi_populates_fields(self) -> None:
        payload = json.dumps(
            {
                "number": 232,
                "title": "Plan-mode gate deadlock",
                "body": "deadlock between native plan mode and plan-audit-gate",
                "labels": [{"name": "defect"}, {"name": "pipeline"}],
                "author": {"login": "ahuimanu"},
            }
        )
        with patch("gzkit.justify.anchors.run_exec", return_value=(0, payload, "")):
            anchor = resolve_anchor("GHI-232", project_root=Path("/tmp"))
        self.assertEqual(anchor.kind, "ghi")
        self.assertEqual(anchor.identifier, "GHI-232")
        self.assertEqual(anchor.title, "Plan-mode gate deadlock")
        self.assertIn("deadlock", anchor.body or "")
        self.assertEqual(set(anchor.labels), {"defect", "pipeline"})
        self.assertEqual(anchor.author, "ahuimanu")

    @covers("REQ-0.0.19-01-03")
    def test_resolve_ghi_accepts_hash_shape(self) -> None:
        payload = json.dumps(
            {"number": 7, "title": "t", "body": "b", "labels": [], "author": {"login": "x"}}
        )
        with patch("gzkit.justify.anchors.run_exec", return_value=(0, payload, "")):
            anchor = resolve_anchor("#7", project_root=Path("/tmp"))
        self.assertEqual(anchor.identifier, "GHI-7")


class TestResolveObpi(unittest.TestCase):
    @covers("REQ-0.0.19-01-05")
    def test_resolve_obpi_locates_via_filename_glob(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            brief_dir = root / "docs" / "design" / "adr" / "foundation" / "ADR-0.0.19-x" / "obpis"
            brief_dir.mkdir(parents=True)
            brief = brief_dir / "OBPI-0.0.19-01-anchor-foo.md"
            brief.write_text("# brief body\n", encoding="utf-8")

            anchor = resolve_anchor("OBPI-0.0.19-01", project_root=root)
        self.assertEqual(anchor.kind, "obpi")
        self.assertEqual(anchor.identifier, "OBPI-0.0.19-01")
        self.assertEqual(anchor.source_path, str(brief))
        self.assertIn("brief body", anchor.body or "")

    @covers("REQ-0.0.19-01-05")
    def test_resolve_obpi_zero_matches_raises(self) -> None:
        with tempfile.TemporaryDirectory() as tmp, self.assertRaises(AnchorResolutionError) as ctx:
            resolve_anchor("OBPI-0.0.19-01", project_root=Path(tmp))
        self.assertIn("no OBPI brief found", str(ctx.exception))

    @covers("REQ-0.0.19-01-05")
    def test_resolve_obpi_multiple_matches_raises_with_candidates(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            b1 = root / "docs/design/adr/foundation/ADR-A/obpis/OBPI-0.0.19-01-alpha.md"
            b2 = root / "docs/design/adr/foundation/ADR-B/obpis/OBPI-0.0.19-01-beta.md"
            for b in (b1, b2):
                b.parent.mkdir(parents=True, exist_ok=True)
                b.write_text("x", encoding="utf-8")
            with self.assertRaises(AnchorResolutionError) as ctx:
                resolve_anchor("OBPI-0.0.19-01", project_root=root)
        msg = str(ctx.exception)
        self.assertIn("multiple", msg)
        self.assertIn("alpha", msg)
        self.assertIn("beta", msg)


class TestResolveDraftAndMalformed(unittest.TestCase):
    @covers("REQ-0.0.19-01-06")
    def test_resolve_draft_literal_passthrough(self) -> None:
        anchor = resolve_anchor(
            None,
            draft_text="consider refactoring the parser",
            draft_slug="refactor-parser",
        )
        self.assertEqual(anchor.kind, "draft")
        self.assertEqual(anchor.draft_text, "consider refactoring the parser")
        self.assertEqual(anchor.draft_slug, "refactor-parser")

    @covers("REQ-0.0.19-01-06")
    def test_resolve_draft_missing_slug_raises_value_error(self) -> None:
        with self.assertRaises(ValueError):
            resolve_anchor(None, draft_text="hi")

    @covers("REQ-0.0.19-01-06")
    def test_resolve_draft_missing_text_raises_value_error(self) -> None:
        with self.assertRaises(ValueError):
            resolve_anchor(None, draft_slug="slug-ok")

    @covers("REQ-0.0.19-01-06")
    def test_resolve_draft_bad_slug_raises_value_error(self) -> None:
        with self.assertRaises(ValueError):
            resolve_anchor(None, draft_text="hi", draft_slug="Bad Slug")

    @covers("REQ-0.0.19-01-06")
    def test_resolve_malformed_raises_value_error_listing_shapes(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            resolve_anchor("foo-bar")
        msg = str(ctx.exception)
        self.assertIn("GHI-", msg)
        self.assertIn("OBPI-", msg)
        self.assertIn("draft", msg)


if __name__ == "__main__":
    unittest.main()
