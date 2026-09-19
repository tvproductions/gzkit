"""GHI #1057: plan containment must reach the CLI verdict and receipt."""

import json
import tempfile
import unittest
from io import StringIO
from pathlib import Path
from unittest.mock import patch

from gzkit.commands.plan_audit_cmd import (
    _extract_plan_paths,
    _path_within_allowed,
    plan_audit_cmd,
)


class TestPlanScope(unittest.TestCase):
    def test_matching_respects_components_globs_and_relative_spelling(self) -> None:
        cases = [
            ("src/gzkit/a.py", ["./src/gzkit/a.py"], True),
            ("./src/gzkit/a.py", ["src/gzkit/"], True),
            ("src/gzkit/a.py", ["src/gzkit/**/*.py"], True),
            ("src/gzkit/nested/a.py", ["src/gzkit/**/*.py"], True),
            ("src/gzkit/a.json", ["src/gzkit/**/*.py"], False),
            ("src/gzkit/ab.py", ["src/gzkit/a"], False),
            ("src/gzkit/a.py", [], False),
            ("src/gzkit/../outside.py", ["src/gzkit/"], False),
            ("../outside.py", ["."], False),
            ("src/../../outside.py", ["."], False),
            ("/tmp/outside.py", ["/tmp/"], False),
        ]
        for path, allowed, expected in cases:
            with self.subTest(path=path, allowed=allowed):
                self.assertEqual(_path_within_allowed(path, allowed), expected)

    def test_explicit_paths_keep_custom_roots_and_strip_source_coordinates(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            plan = Path(tmp) / "plan.md"
            plan.write_text(
                "Edit `.gzkit/config.json`, `data/map.json`, `scripts/check.py`, "
                "`custom/worker.py`, `AGENTS.md`, and `./pyproject.toml`.\n"
                "Read `src/allowed.py:12`, `src/allowed.py:12-15`, "
                "and `src/allowed.py:12:3`.\n"
                "Reject `../outside.py`. Preserve unquoted tests/test_sample.py.\n"
                "Ignore `uv run gz check`, `https://example.com/a.py`, and `0.35.0`.\n",
                encoding="utf-8",
            )
            self.assertEqual(
                set(_extract_plan_paths(plan)),
                {
                    ".gzkit/config.json",
                    "data/map.json",
                    "scripts/check.py",
                    "custom/worker.py",
                    "AGENTS.md",
                    "pyproject.toml",
                    "src/allowed.py",
                    "../outside.py",
                    "tests/test_sample.py",
                },
            )

    def test_outside_create_fails_receipt_while_allowed_create_passes(self) -> None:
        for path, expected in [
            ("src/outside.py", "FAIL"),
            (".gzkit/outside.json", "FAIL"),
            ("data/outside.json", "FAIL"),
            ("scripts/outside.py", "FAIL"),
            ("custom/outside.py", "FAIL"),
            ("AGENTS.md", "FAIL"),
            ("src/allowed/new.py", "PASS"),
            ("src/allowed/new.py:12", "PASS"),
        ]:
            with self.subTest(path=path), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                obpi = "OBPI-0.1.0-01-scope"
                briefs = root / "docs/design/adr/pre-release/ADR-0.1.0-scope/obpis"
                briefs.mkdir(parents=True)
                (briefs / f"{obpi}.md").write_text(
                    "## Allowed Paths\n- `src/allowed/`\n", encoding="utf-8"
                )
                (root / "src/allowed").mkdir(parents=True)
                plans = root / ".claude/plans"
                plans.mkdir(parents=True)
                plan = plans / "scope.md"
                plan.write_text(f"# {obpi}\n- `{path}` **CREATE**\n", encoding="utf-8")
                output = StringIO()
                with (
                    patch("gzkit.commands.common.ensure_initialized"),
                    patch("gzkit.commands.common.get_project_root", return_value=root),
                    patch("gzkit.commands.plan_audit_cmd._canonicalize_obpi_id", return_value=obpi),
                    patch("gzkit.pipeline_markers.find_plan_for_obpi", return_value=plan),
                    patch("sys.stdout", output),
                ):
                    if expected == "FAIL":
                        with self.assertRaises(SystemExit) as raised:
                            plan_audit_cmd(obpi, as_json=True)
                        self.assertEqual(raised.exception.code, 1)
                    else:
                        plan_audit_cmd(obpi, as_json=True)
                receipt = json.loads(
                    (plans / f".plan-audit-receipt-{obpi}.json").read_text(encoding="utf-8")
                )
                self.assertEqual(receipt["verdict"], expected)
                self.assertEqual(json.loads(output.getvalue()), receipt)
                self.assertEqual(receipt["gaps_found"], 1 if expected == "FAIL" else 0)
                if expected == "FAIL":
                    self.assertEqual(
                        receipt["gaps"], [f"Plan references path outside brief scope: {path}"]
                    )
