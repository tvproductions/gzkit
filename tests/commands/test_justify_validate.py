"""CLI tests for ``gz justify validate`` (OBPI-0.0.19-03).

Covers REQs 05 through 10 and REQ-12. Tests call ``handle_validate`` directly
for speed; one subprocess smoke test at the bottom exercises the registered
subverb wiring end-to-end.
"""

from __future__ import annotations

import io
import json
import subprocess
import sys
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from gzkit.commands.justify_cmd import justify_cmd
from gzkit.justify.cli import handle_validate
from gzkit.traceability import covers

FIXTURES = Path(__file__).resolve().parents[1] / "justify" / "fixtures"
COMPLETE_FIXTURE = FIXTURES / "walkthrough_complete.md"
INCOMPLETE_FIXTURE = FIXTURES / "walkthrough_incomplete.md"
MALFORMED_FIXTURE = FIXTURES / "walkthrough_malformed.md"


def _invoke_via_cmd(**kwargs: object) -> int:
    """Invoke justify_cmd; collapse the SystemExit to an int return."""
    try:
        return justify_cmd(**kwargs)  # type: ignore[arg-type]
    except SystemExit as exc:
        if isinstance(exc.code, int):
            return exc.code
        return 1


class TestValidateMissingFile(unittest.TestCase):
    """REQ-05: absent <file> positional yields exit 1."""

    @covers("REQ-0.0.19-03-05")
    def test_missing_file_positional_exits_one(self) -> None:
        stderr = io.StringIO()
        with redirect_stderr(stderr):
            code = handle_validate(file=None, json_output=False)
        self.assertEqual(code, 1)
        self.assertIn("required", stderr.getvalue().lower())

    @covers("REQ-0.0.19-03-05")
    def test_nonexistent_file_exits_one(self) -> None:
        stderr = io.StringIO()
        with redirect_stderr(stderr):
            code = handle_validate(file="/tmp/does-not-exist-justify.md", json_output=False)
        self.assertEqual(code, 1)
        self.assertIn("not found", stderr.getvalue().lower())


class TestValidateCompleteFixture(unittest.TestCase):
    """REQ-06: exit 0 + 'is complete' message on complete fixture."""

    @covers("REQ-0.0.19-03-06")
    def test_complete_fixture_exits_zero_with_is_complete(self) -> None:
        stdout = io.StringIO()
        stderr = io.StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            code = handle_validate(file=str(COMPLETE_FIXTURE), json_output=False)
        self.assertEqual(code, 0)
        self.assertIn("is complete", stdout.getvalue())
        self.assertEqual(stderr.getvalue(), "")


class TestValidateIncompleteFixture(unittest.TestCase):
    """REQ-07: exit 1 + lists unfilled ordinals."""

    @covers("REQ-0.0.19-03-07")
    def test_incomplete_fixture_exits_one_listing_unfilled_ordinals(self) -> None:
        stdout = io.StringIO()
        with redirect_stdout(stdout):
            code = handle_validate(file=str(INCOMPLETE_FIXTURE), json_output=False)
        output = stdout.getvalue()
        self.assertEqual(code, 1)
        self.assertIn("incomplete", output)
        # Fixture leaves sections 2, 5, 8 as placeholders.
        self.assertIn("2", output)
        self.assertIn("5", output)
        self.assertIn("8", output)
        # No traceback on the happy-path failure mode.
        self.assertNotIn("Traceback", output)


class TestValidateMalformedFixture(unittest.TestCase):
    """REQ-08: exit 2 + parse-error message."""

    @covers("REQ-0.0.19-03-08")
    def test_malformed_fixture_exits_two_with_parse_error(self) -> None:
        stdout = io.StringIO()
        with redirect_stdout(stdout):
            code = handle_validate(file=str(MALFORMED_FIXTURE), json_output=False)
        output = stdout.getvalue()
        self.assertEqual(code, 2)
        self.assertIn("could not be parsed", output)


class TestValidateJsonOutput(unittest.TestCase):
    """REQ-09: --json emits a parseable ValidateResult JSON object."""

    @covers("REQ-0.0.19-03-09")
    def test_json_output_for_complete_fixture_is_parseable(self) -> None:
        stdout = io.StringIO()
        with redirect_stdout(stdout):
            code = handle_validate(file=str(COMPLETE_FIXTURE), json_output=True)
        self.assertEqual(code, 0)
        payload = json.loads(stdout.getvalue())
        self.assertGreaterEqual(
            set(payload.keys()),
            {"file_path", "is_parseable", "is_complete", "unfilled_ordinals", "parse_error"},
        )
        self.assertTrue(payload["is_parseable"])
        self.assertTrue(payload["is_complete"])
        self.assertEqual(payload["unfilled_ordinals"], [])

    @covers("REQ-0.0.19-03-09")
    def test_json_output_for_incomplete_fixture_contains_unfilled_ordinals(self) -> None:
        stdout = io.StringIO()
        with redirect_stdout(stdout):
            code = handle_validate(file=str(INCOMPLETE_FIXTURE), json_output=True)
        self.assertEqual(code, 1)
        payload = json.loads(stdout.getvalue())
        self.assertTrue(payload["is_parseable"])
        self.assertFalse(payload["is_complete"])
        self.assertEqual(payload["unfilled_ordinals"], [2, 5, 8])
        self.assertIsNone(payload["parse_error"])

    @covers("REQ-0.0.19-03-09")
    def test_json_output_for_malformed_fixture_carries_parse_error(self) -> None:
        stdout = io.StringIO()
        with redirect_stdout(stdout):
            code = handle_validate(file=str(MALFORMED_FIXTURE), json_output=True)
        self.assertEqual(code, 2)
        payload = json.loads(stdout.getvalue())
        self.assertFalse(payload["is_parseable"])
        self.assertFalse(payload["is_complete"])
        self.assertIsNotNone(payload["parse_error"])


class TestValidateHelpSurface(unittest.TestCase):
    """REQ-10: --help lists exit codes 0/1/2 and an example."""

    @covers("REQ-0.0.19-03-10")
    def test_help_output_documents_exit_codes_and_examples(self) -> None:
        result = subprocess.run(
            [sys.executable, "-m", "gzkit", "justify", "--help"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
        self.assertEqual(result.returncode, 0)
        help_text = result.stdout
        # Exit-code doctrine meanings (0 complete, 1 incomplete, 2 unparseable)
        # must be reachable from the help surface.
        for token in ("0", "1", "2", "validate", "complete", "incomplete", "unparseable"):
            self.assertIn(token, help_text.lower() if token not in {"0", "1", "2"} else help_text)


class TestValidateCmdRoutingEndToEnd(unittest.TestCase):
    """End-to-end dispatch: justify_cmd with subverb='validate' routes correctly."""

    @covers("REQ-0.0.19-03-06")
    def test_justify_cmd_routes_validate_subverb(self) -> None:
        stdout = io.StringIO()
        with redirect_stdout(stdout):
            code = _invoke_via_cmd(
                subverb="validate",
                file=str(COMPLETE_FIXTURE),
                json_output=False,
            )
        self.assertEqual(code, 0)
        self.assertIn("is complete", stdout.getvalue())


class TestValidateSubprocessSmoke(unittest.TestCase):
    """End-to-end smoke over subprocess to lock the registered subverb wiring."""

    @covers("REQ-0.0.19-03-06")
    def test_subprocess_validate_on_complete_fixture(self) -> None:
        result = subprocess.run(
            [sys.executable, "-m", "gzkit", "justify", "validate", str(COMPLETE_FIXTURE)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn("is complete", result.stdout)

    @covers("REQ-0.0.19-03-08")
    def test_subprocess_validate_on_malformed_fixture(self) -> None:
        result = subprocess.run(
            [sys.executable, "-m", "gzkit", "justify", "validate", str(MALFORMED_FIXTURE)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn("could not be parsed", result.stdout)


class TestCliAuditCoverage(unittest.TestCase):
    """REQ-12: gz cli audit passes with the new subverb covered."""

    @covers("REQ-0.0.19-03-12")
    def test_cli_audit_exits_zero_after_validate_subverb_lands(self) -> None:
        result = subprocess.run(
            [sys.executable, "-m", "gzkit", "cli", "audit"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
        self.assertEqual(
            result.returncode,
            0,
            f"gz cli audit failed (stdout={result.stdout!r}, stderr={result.stderr!r})",
        )


class TestFixtureDriftGuard(unittest.TestCase):
    """Fixture drift guard: committed fixtures must match fresh renders.

    This is an Invariant-3-adjacent check — if the Jinja2 template drifts,
    the committed fixtures will lag and tests may silently encode old output
    shapes. Re-rendering and comparing byte-for-byte catches that.
    """

    @covers("REQ-0.0.19-03-02")
    def test_complete_fixture_matches_fresh_render(self) -> None:
        from gzkit.justify.models import AnchorRef, EvidenceBundle
        from gzkit.justify.walkthrough import (
            SECTION_HEADINGS,
            SECTION_PROMPTS,
            Walkthrough,
            WalkthroughSection,
            render_markdown,
        )

        anchor = AnchorRef(kind="ghi", identifier="GHI-232", title=None, body=None)
        sections = [
            WalkthroughSection(
                ordinal=i,
                heading=SECTION_HEADINGS[i - 1],
                prompt=SECTION_PROMPTS[i],
                evidence_citations=[],
                reasoning=f"Reasoning for section {i}.",
            )
            for i in range(1, 9)
        ]
        walkthrough = Walkthrough(
            anchor=anchor,
            evidence=EvidenceBundle(
                anchor=anchor,
                matching_rules=(),
                ledger_events=(),
                recent_commits=(),
                related_anchors=(),
                taxonomy_reference="docs/governance/model-regression-taxonomy.md",
                warnings=(),
            ),
            generated_at="2026-04-22T00:00:00+00:00",
            sections=sections,
            scaffold_version="1.0",
        )
        fresh = render_markdown(walkthrough)
        committed = COMPLETE_FIXTURE.read_text(encoding="utf-8")
        self.assertEqual(
            committed,
            fresh,
            "walkthrough_complete.md has drifted from the current Jinja2 "
            "template; regenerate it or the parser round-trip tests no "
            "longer exercise real output.",
        )


if __name__ == "__main__":
    unittest.main()
