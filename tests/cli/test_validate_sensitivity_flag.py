"""CLI tests for `gz validate --sensitivity` (REQ-0.0.22-03-05/06/07)."""

from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest import mock

from gzkit.cli.main import _build_parser
from gzkit.traceability import covers


def _registry_payload() -> list[dict[str, object]]:
    return [
        {
            "category": "ledger_integrity",
            "globs": ["src/gzkit/ledger.py"],
            "rationale": "Ledger writers.",
        },
    ]


def _setup_fixture_root(tmp: str, *, with_brief: bool = True) -> Path:
    root = Path(tmp)
    data = root / "data"
    data.mkdir(parents=True, exist_ok=True)
    (data / "security_surfaces.json").write_text(json.dumps(_registry_payload()), encoding="utf-8")
    if with_brief:
        obpi_dir = root / "docs" / "design" / "adr" / "foundation" / "ADR-fixture" / "obpis"
        obpi_dir.mkdir(parents=True, exist_ok=True)
        (obpi_dir / "OBPI-fixture-01.md").write_text(
            "---\n"
            "id: OBPI-fixture-01\n"
            "parent: ADR-fixture\n"
            "item: 1\n"
            "lane: Heavy\n"
            "status: Draft\n"
            "---\n\n"
            "# OBPI-fixture-01\n\n"
            "## Allowed Paths\n\n"
            "- `src/gzkit/ledger.py` -- under test\n",
            encoding="utf-8",
        )
    return root


class TestSensitivityFlagRegistration(unittest.TestCase):
    """The CLI parser registers --sensitivity and --explain."""

    @covers("REQ-0.0.22-03-05")
    @covers("REQ-0.0.22-03-06")
    def test_validate_parser_accepts_sensitivity_and_explain(self):
        parser = _build_parser()
        ns = parser.parse_args(
            ["validate", "--sensitivity", "--explain", "src/gzkit/ledger.py", "--json"]
        )
        self.assertTrue(getattr(ns, "check_sensitivity", False))
        # --explain shares its dest with --frontmatter mode; scope flag
        # disambiguates downstream.
        self.assertEqual(ns.frontmatter_explain, "src/gzkit/ledger.py")
        self.assertTrue(ns.as_json)


class TestSensitivityExplain(unittest.TestCase):
    """`--explain` predicts classification without disk side effects."""

    @covers("REQ-0.0.22-03-05")
    def test_explain_prints_prediction_and_exits_0(self):
        from gzkit.commands import validate_cmd

        with tempfile.TemporaryDirectory() as tmp:
            root = _setup_fixture_root(tmp, with_brief=False)
            buf = io.StringIO()
            with (
                mock.patch.object(validate_cmd, "get_project_root", return_value=root),
                redirect_stdout(buf),
                self.assertRaises(SystemExit) as ctx,
            ):
                validate_cmd.validate(
                    check_manifest=False,
                    check_documents=False,
                    check_surfaces=False,
                    check_ledger=False,
                    check_instructions=False,
                    check_briefs=False,
                    check_sensitivity=True,
                    sensitivity_explain="src/gzkit/ledger.py",
                    as_json=True,
                )
            self.assertEqual(ctx.exception.code, 0)
            payload = json.loads(buf.getvalue())
            self.assertEqual(payload["detected_sensitivity"], "security")
            self.assertIn("ledger_integrity", payload["matching_categories"])

    @covers("REQ-0.0.22-03-05")
    def test_explain_accepts_comma_and_newline_separated(self):
        from gzkit.commands import validate_cmd

        with tempfile.TemporaryDirectory() as tmp:
            root = _setup_fixture_root(tmp, with_brief=False)
            buf = io.StringIO()
            with (
                mock.patch.object(validate_cmd, "get_project_root", return_value=root),
                redirect_stdout(buf),
                self.assertRaises(SystemExit) as ctx,
            ):
                validate_cmd.validate(
                    check_manifest=False,
                    check_documents=False,
                    check_surfaces=False,
                    check_ledger=False,
                    check_instructions=False,
                    check_briefs=False,
                    check_sensitivity=True,
                    sensitivity_explain="src/gzkit/ledger.py,docs/runbook.md",
                    as_json=True,
                )
            self.assertEqual(ctx.exception.code, 0)
            payload = json.loads(buf.getvalue())
            self.assertEqual(payload["input_globs"], ["src/gzkit/ledger.py", "docs/runbook.md"])


class TestSensitivityJson(unittest.TestCase):
    """`--sensitivity --json` emits machine-readable per-brief records."""

    @covers("REQ-0.0.22-03-06")
    def test_json_records_have_required_fields(self):
        from gzkit.commands import validate_cmd

        with tempfile.TemporaryDirectory() as tmp:
            root = _setup_fixture_root(tmp, with_brief=True)
            buf = io.StringIO()
            err_buf = io.StringIO()
            with (
                mock.patch.object(validate_cmd, "get_project_root", return_value=root),
                redirect_stdout(buf),
                redirect_stderr(err_buf),
                self.assertRaises(SystemExit) as ctx,
            ):
                validate_cmd.validate(
                    check_manifest=False,
                    check_documents=False,
                    check_surfaces=False,
                    check_ledger=False,
                    check_instructions=False,
                    check_briefs=False,
                    check_sensitivity=True,
                    as_json=True,
                )
            # Undeclared overlap fails closed (GHI #625): the fixture brief
            # intersects a registered surface (src/gzkit/ledger.py) with no
            # declaration and is not grandfathered -> sensitivity-floor-violation,
            # exit 3. Records are still emitted on a violation.
            self.assertEqual(ctx.exception.code, 3)
            payload = json.loads(buf.getvalue())
            self.assertIn("records", payload)
            records = payload["records"]
            self.assertTrue(records, "expected at least one per-brief record")
            required = {
                "file",
                "declared_sensitivity",
                "detected_sensitivity",
                "intersecting_paths",
                "registry_categories",
            }
            for rec in records:
                self.assertTrue(required.issubset(rec.keys()), rec)


class TestSensitivityAll(unittest.TestCase):
    """`gz validate --audits` includes the sensitivity scope."""

    @covers("REQ-0.0.22-03-07")
    def test_audits_umbrella_threads_check_sensitivity(self):
        parser = _build_parser()
        ns = parser.parse_args(["validate", "--audits"])
        # The umbrella surfaces check_sensitivity via its dispatcher kwargs.
        # Patching the cached validate handler in parser_maintenance is the
        # only intercept site that doesn't fight the lazy-import cache; we
        # restore the cached entry on exit so other tests aren't affected.
        from gzkit.cli import parser_maintenance
        from gzkit.commands import validate_cmd

        captured: dict[str, object] = {}

        def fake_validate(**kwargs: object) -> None:
            captured.update(kwargs)

        prior_cache = parser_maintenance._HANDLER_CACHE.get("validate")
        parser_maintenance._HANDLER_CACHE["validate"] = fake_validate
        try:
            ns.func(ns)
        finally:
            if prior_cache is None:
                parser_maintenance._HANDLER_CACHE.pop("validate", None)
            else:
                parser_maintenance._HANDLER_CACHE["validate"] = prior_cache

        # Sanity-check: the cache restoration leaves the live module intact.
        assert callable(validate_cmd.validate)
        self.assertTrue(
            captured.get("check_sensitivity"),
            f"--audits must thread check_sensitivity=True; got {captured}",
        )


if __name__ == "__main__":
    unittest.main()
