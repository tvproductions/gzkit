"""Acceptance-gate enforcement for the control-surface-rule-conflicts chore.

REQ source: ADR-pool.control-surface-rule-pair-conflict-audit § Audit-row
schema. GHI #448 surfaced the gap — acceptance.json was file-existence only
and would pass on empty or speculative conflict-matrix.md outputs.

Tests assert the parser semantics named in the ADR's audit-row schema:
fail-closed on empty matrix, missing Evidence column, empty Evidence cell,
or Evidence cell with no resolvable reference (GHI #N | SHA | insight id).

Resolution semantics live in the script under test. Network calls are
mocked at the subprocess boundary; insight-id resolution is exercised
against a tmpfile fixture.
"""

from __future__ import annotations

import importlib.util
import io
import re
import sys
import unittest
from pathlib import Path
from typing import Any
from unittest.mock import patch


def _load_check_evidence() -> Any:
    repo_root = Path(__file__).resolve().parents[2]
    script = (
        repo_root
        / "src"
        / "gzkit"
        / "chores"
        / "control-surface-rule-conflicts"
        / "check_evidence.py"
    )
    spec = importlib.util.spec_from_file_location("check_evidence", script)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules["check_evidence"] = module
    spec.loader.exec_module(module)
    return module


CE = _load_check_evidence()


_MATRIX_HEADER = (
    "| # | Rule A + § | Rule B + § | Worked Example | Evidence "
    "| Mechanical Winner | Suggested Resolution | Severity |\n"
    "|---|------------|------------|----------------|----------"
    "|-------------------|----------------------|----------|\n"
)


def _matrix_with_rows(*rows: str) -> str:
    return "# Conflict Matrix\n\n" + _MATRIX_HEADER + "".join(rows)


class ParseHeaderTests(unittest.TestCase):
    """Parser must locate the markdown table and validate the header set."""

    def test_empty_text_returns_no_table(self) -> None:
        self.assertIsNone(CE.parse_table(""))

    def test_text_without_table_returns_no_table(self) -> None:
        self.assertIsNone(CE.parse_table("# Heading\n\nProse only.\n"))

    def test_table_header_with_all_required_columns_parses(self) -> None:
        text = _matrix_with_rows()
        table = CE.parse_table(text)
        assert table is not None
        self.assertIn("evidence", {h.lower() for h in table.headers})
        self.assertIn("severity", {h.lower() for h in table.headers})

    def test_missing_evidence_column_is_invalid(self) -> None:
        text = (
            "| # | Rule A + § | Rule B + § | Worked Example "
            "| Wins Today | Suggested Resolution |\n"
            "|---|------------|------------|----------------"
            "|------------|----------------------|\n"
        )
        table = CE.parse_table("# Conflict Matrix\n\n" + text)
        assert table is not None
        issues = CE.validate_header(table.headers)
        self.assertTrue(any("evidence" in issue.lower() for issue in issues))

    def test_missing_severity_column_is_invalid(self) -> None:
        text = (
            "| Rule A + § | Rule B + § | Worked Example | Evidence "
            "| Mechanical Winner | Suggested Resolution |\n"
            "|------------|------------|----------------|----------"
            "|-------------------|----------------------|\n"
        )
        table = CE.parse_table("# Conflict Matrix\n\n" + text)
        assert table is not None
        issues = CE.validate_header(table.headers)
        self.assertTrue(any("severity" in issue.lower() for issue in issues))


class ExtractRefsTests(unittest.TestCase):
    """Evidence-cell parser surfaces GHI numbers, SHAs, and insight ids."""

    def test_extracts_ghi_reference(self) -> None:
        refs = CE.extract_refs("Surfaced via GHI #195")
        kinds = {r.kind for r in refs}
        self.assertIn("ghi", kinds)
        self.assertIn("195", {r.value for r in refs if r.kind == "ghi"})

    def test_extracts_bare_hash_reference(self) -> None:
        refs = CE.extract_refs("See #234 for prior art")
        self.assertIn("234", {r.value for r in refs if r.kind == "ghi"})

    def test_extracts_sha_reference(self) -> None:
        refs = CE.extract_refs("Commit 5e8174ba reconciled the conflict")
        self.assertIn("5e8174ba", {r.value for r in refs if r.kind == "sha"})

    def test_extracts_insight_id_token(self) -> None:
        refs = CE.extract_refs("Insight: scope-tracker-2026-04-21")
        self.assertIn("scope-tracker-2026-04-21", {r.value for r in refs if r.kind == "insight"})

    def test_empty_cell_yields_no_refs(self) -> None:
        self.assertEqual(CE.extract_refs(""), [])

    def test_whitespace_only_cell_yields_no_refs(self) -> None:
        self.assertEqual(CE.extract_refs("   \n\t  "), [])


class ResolveRefTests(unittest.TestCase):
    """Resolution honors local-binding for SHA/insight and best-effort for GHI."""

    def test_sha_resolves_via_git_log(self) -> None:
        with patch.object(CE, "_git_log_resolves", return_value=True):
            ref = CE.Ref(kind="sha", value="deadbeef")
            self.assertTrue(CE.resolve_ref(ref, gh_authenticated=False))

    def test_sha_unresolvable_when_git_log_fails(self) -> None:
        with patch.object(CE, "_git_log_resolves", return_value=False):
            ref = CE.Ref(kind="sha", value="cafebabe")
            self.assertFalse(CE.resolve_ref(ref, gh_authenticated=False))

    def test_insight_resolves_via_grep(self) -> None:
        with patch.object(CE, "_insight_grep_resolves", return_value=True):
            ref = CE.Ref(kind="insight", value="foo-bar")
            self.assertTrue(CE.resolve_ref(ref, gh_authenticated=False))

    def test_ghi_resolves_via_gh_when_authenticated(self) -> None:
        with patch.object(CE, "_gh_issue_resolves", return_value=True):
            ref = CE.Ref(kind="ghi", value="448")
            self.assertTrue(CE.resolve_ref(ref, gh_authenticated=True))

    def test_ghi_offline_falls_back_to_shape_check(self) -> None:
        ref = CE.Ref(kind="ghi", value="448")
        self.assertTrue(CE.resolve_ref(ref, gh_authenticated=False))

    def test_ghi_offline_rejects_implausible_number(self) -> None:
        ref = CE.Ref(kind="ghi", value="999999")
        self.assertFalse(CE.resolve_ref(ref, gh_authenticated=False))


class MatrixValidationTests(unittest.TestCase):
    """End-to-end matrix validation: shape + resolution per ADR § Audit-row schema."""

    def test_empty_matrix_fails(self) -> None:
        result = CE.validate_matrix_text("", gh_authenticated=False)
        self.assertNotEqual(result.exit_code, 0)
        self.assertTrue(any("empty" in m.lower() for m in result.messages))

    def test_matrix_without_table_fails(self) -> None:
        result = CE.validate_matrix_text(
            "# Conflict Matrix\n\nNo table here.\n", gh_authenticated=False
        )
        self.assertNotEqual(result.exit_code, 0)

    def test_matrix_with_no_data_rows_fails(self) -> None:
        result = CE.validate_matrix_text(_matrix_with_rows(), gh_authenticated=False)
        self.assertNotEqual(result.exit_code, 0)
        self.assertTrue(any("row" in m.lower() for m in result.messages))

    def test_row_with_empty_evidence_cell_fails(self) -> None:
        row = (
            "| 1 | `tests.md` § X | `arb.md` § Y | Worked |  | tests.md | reconcile | blocking |\n"
        )
        result = CE.validate_matrix_text(_matrix_with_rows(row), gh_authenticated=False)
        self.assertNotEqual(result.exit_code, 0)
        self.assertTrue(any("evidence" in m.lower() for m in result.messages))

    def test_row_with_resolvable_ghi_passes(self) -> None:
        row = (
            "| 1 | `tests.md` § X | `arb.md` § Y | Worked | GHI #195 |"
            " tests.md | reconcile | blocking |\n"
        )
        result = CE.validate_matrix_text(_matrix_with_rows(row), gh_authenticated=False)
        self.assertEqual(result.exit_code, 0, msg=result.messages)

    def test_row_with_unresolvable_evidence_fails(self) -> None:
        row = (
            "| 1 | `tests.md` § X | `arb.md` § Y | Worked | "
            "no-references-at-all-here | tests.md | reconcile | blocking |\n"
        )
        with patch.object(CE, "_insight_grep_resolves", return_value=False):
            result = CE.validate_matrix_text(_matrix_with_rows(row), gh_authenticated=False)
        self.assertNotEqual(result.exit_code, 0)


class SelfTestEntrypointTests(unittest.TestCase):
    """The --self-test mode is what acceptance.json invokes; it must be deterministic."""

    def test_self_test_exits_zero(self) -> None:
        """Self-test passes and reports how much it ran.

        Asserts the summary's shape and that the counts are non-zero — not the
        literal tally. Pinning the count made adding a fixture a test failure,
        which penalizes exactly the thing the suite wants (the counts are now
        derived in ``run_self_test`` for the same reason).
        """
        with patch("sys.stdout", new_callable=io.StringIO) as stdout:
            self.assertEqual(CE.run_self_test(), 0)
        summary = stdout.getvalue()
        match = re.search(r"OK \((\d+) matrix fixtures \+ (\d+) parser checks\)", summary)
        self.assertIsNotNone(match, f"self-test must print its summary; got: {summary!r}")
        assert match is not None
        self.assertGreater(int(match.group(1)), 0, "self-test ran zero matrix fixtures")
        self.assertGreater(int(match.group(2)), 0, "self-test ran zero parser checks")


if __name__ == "__main__":
    unittest.main()
