"""CLI tests for ``gz complexity distill`` (GHI #400).

Pins the Output Contract declared by
``.gzkit/skills/gz-complexity-distill/SKILL.md`` (REQ-0.0.27-06-04) and
the no-overwrite policy declared by ``OBPI-0.0.27-04`` (REQ-0.0.27-04-05).
Subprocess boundaries (radon / lizard / cohesion) are short-circuited via
``--baseline-json``; no real measurement runs in unit tests.

Test classes are split per ``.gzkit/rules/tool-skill-runbook-alignment.md``
§ Invariant 3 / ``.gzkit/rules/tests.md`` § Output-form fixture carve-out:

- ``TestComplexityDistillBehavior`` — REQ-derived semantic assertions
  (exit codes, file production, prior auto-detect, cold-start path).
- ``TestComplexityDistillOutputForm`` — Invariant-3 fixture asserting the
  observed default rendering matches the SKILL.md Output Contract form
  (string-shape assertions live only here).
"""

from __future__ import annotations

import io
import json
import shutil
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from gzkit.commands.complexity_distill_cmd import complexity_distill_cmd
from gzkit.traceability import covers

PROJECT_ROOT = Path(__file__).resolve().parents[2]
FIXTURE_BASELINE = (
    PROJECT_ROOT
    / "docs"
    / "governance"
    / "complexity"
    / "baselines"
    / "2026-05-04"
    / "baseline.json"
)
FIXTURE_TODAY = "2026-05-05"


def _invoke(**kwargs: object) -> tuple[int, str, str]:
    """Call ``complexity_distill_cmd``; return ``(exit_code, stdout, stderr)``."""
    out = io.StringIO()
    err = io.StringIO()
    code = 0
    try:
        with redirect_stdout(out), redirect_stderr(err):
            complexity_distill_cmd(**kwargs)  # type: ignore[arg-type]
    except SystemExit as exc:
        code = int(exc.code) if isinstance(exc.code, int) else 1
    return code, out.getvalue(), err.getvalue()


class TestComplexityDistillBehavior(unittest.TestCase):
    """REQ-derived semantic assertions for ``gz complexity distill``."""

    def setUp(self) -> None:
        self._tmpdir = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmpdir.cleanup)
        self.work_dir = Path(self._tmpdir.name)

    @covers("REQ-0.0.27-06-04")
    def test_writes_dated_distilled_characteristics_under_output_dir(self) -> None:
        code, _, _ = _invoke(
            baseline_json=str(FIXTURE_BASELINE),
            output_dir=str(self.work_dir),
            no_prior=True,
            today_override=FIXTURE_TODAY,
        )
        self.assertEqual(code, 0, "clean run must exit 0")
        produced = self.work_dir / f"distilled-characteristics-{FIXTURE_TODAY}.md"
        self.assertTrue(
            produced.exists(),
            f"verb must write the dated distilled-characteristics document at {produced}",
        )

    @covers("REQ-0.0.27-06-04")
    def test_invalid_today_returns_user_config_error(self) -> None:
        code, _, err = _invoke(
            baseline_json=str(FIXTURE_BASELINE),
            output_dir=str(self.work_dir),
            no_prior=True,
            today_override="not-a-date",
        )
        self.assertEqual(code, 1, "bad --today must exit 1 (user/config error)")
        self.assertIn("invalid --today", err)

    @covers("REQ-0.0.27-06-04")
    def test_missing_baseline_returns_user_config_error(self) -> None:
        code, _, err = _invoke(
            baseline_json=str(self.work_dir / "does-not-exist.json"),
            output_dir=str(self.work_dir),
            no_prior=True,
            today_override=FIXTURE_TODAY,
        )
        self.assertEqual(code, 1, "missing baseline JSON must exit 1")
        self.assertGreater(len(err), 0, "error message must be emitted on stderr")

    @covers("REQ-0.0.27-06-04")
    def test_collision_without_allow_sibling_returns_policy_breach(self) -> None:
        # First run lands the document.
        first_code, _, _ = _invoke(
            baseline_json=str(FIXTURE_BASELINE),
            output_dir=str(self.work_dir),
            no_prior=True,
            today_override=FIXTURE_TODAY,
        )
        self.assertEqual(first_code, 0)
        # Second run hits REQ-0.0.27-04-05 no-overwrite guard.
        code, _, err = _invoke(
            baseline_json=str(FIXTURE_BASELINE),
            output_dir=str(self.work_dir),
            no_prior=True,
            today_override=FIXTURE_TODAY,
        )
        self.assertEqual(code, 3, "same-date collision must exit 3 (policy breach)")
        self.assertIn("already exists", err)

    @covers("REQ-0.0.27-06-04")
    def test_collision_with_allow_sibling_writes_dated_sibling(self) -> None:
        _invoke(
            baseline_json=str(FIXTURE_BASELINE),
            output_dir=str(self.work_dir),
            no_prior=True,
            today_override=FIXTURE_TODAY,
        )
        code, _, _ = _invoke(
            baseline_json=str(FIXTURE_BASELINE),
            output_dir=str(self.work_dir),
            no_prior=True,
            allow_dated_sibling=True,
            today_override=FIXTURE_TODAY,
        )
        self.assertEqual(code, 0, "--allow-dated-sibling must clear the policy breach")
        sibling = self.work_dir / f"distilled-characteristics-{FIXTURE_TODAY}-1.md"
        self.assertTrue(sibling.exists(), "sibling must be written on collision-with-flag")

    @covers("REQ-0.0.27-06-04")
    def test_no_prior_emits_cold_start_diff_section(self) -> None:
        _invoke(
            baseline_json=str(FIXTURE_BASELINE),
            output_dir=str(self.work_dir),
            no_prior=True,
            today_override=FIXTURE_TODAY,
        )
        document = (self.work_dir / f"distilled-characteristics-{FIXTURE_TODAY}.md").read_text(
            encoding="utf-8"
        )
        # REQ-0.0.27-04-04 cold-start sentinel: no prior → "Cold start" prose.
        self.assertIn("Cold start", document, "cold-start path must emit the sentinel")

    @covers("REQ-0.0.27-06-04")
    def test_auto_detected_prior_emits_diff_section_against_prior(self) -> None:
        # Land a prior document under output_dir.
        prior_path = self.work_dir / "distilled-characteristics-2026-05-04.md"
        shutil.copyfile(
            PROJECT_ROOT
            / "docs"
            / "governance"
            / "complexity"
            / "distilled-characteristics-2026-05-04.md",
            prior_path,
        )
        code, _, _ = _invoke(
            baseline_json=str(FIXTURE_BASELINE),
            output_dir=str(self.work_dir),
            today_override=FIXTURE_TODAY,
        )
        self.assertEqual(code, 0)
        document = (self.work_dir / f"distilled-characteristics-{FIXTURE_TODAY}.md").read_text(
            encoding="utf-8"
        )
        self.assertNotIn(
            "Cold start", document, "auto-detected prior must NOT emit the cold-start sentinel"
        )

    @covers("REQ-0.0.27-06-04")
    def test_baseline_json_with_extra_fields_returns_user_config_error(self) -> None:
        # The handler validates BaselineArtifact strictly (extra="forbid");
        # malformed baseline files surface as exit 1, not exit 2.
        bad = self.work_dir / "bad-baseline.json"
        payload = json.loads(FIXTURE_BASELINE.read_text(encoding="utf-8"))
        payload["unexpected_field"] = "drift"
        bad.write_text(json.dumps(payload), encoding="utf-8")
        code, _, _ = _invoke(
            baseline_json=str(bad),
            output_dir=str(self.work_dir),
            no_prior=True,
            today_override=FIXTURE_TODAY,
        )
        self.assertEqual(code, 1, "schema-drift in baseline JSON must exit 1 (user/config)")


class TestComplexityDistillOutputForm(unittest.TestCase):
    """Invariant 3 fixture — pins the SKILL.md Output Contract rendering form.

    String-shape assertions live in this class only, per
    ``.gzkit/rules/tool-skill-runbook-alignment.md`` § Invariant 3 and
    ``.gzkit/rules/tests.md`` § Output-form fixture carve-out.
    """

    def setUp(self) -> None:
        self._tmpdir = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmpdir.cleanup)
        self.work_dir = Path(self._tmpdir.name)

    def test_stdout_summary_carries_contract_lines(self) -> None:
        code, out, _ = _invoke(
            baseline_json=str(FIXTURE_BASELINE),
            output_dir=str(self.work_dir),
            no_prior=True,
            today_override=FIXTURE_TODAY,
        )
        self.assertEqual(code, 0)
        # Output Contract shape (manpage § OUTPUT CONTRACT):
        #   Distillation pass complete.
        #     Corpus revision: <int>
        #     Baseline artifact: <posix path>
        #     Distilled document: <posix path>
        #     Per-metric sections rendered: <int>
        for marker in (
            "Distillation pass complete.",
            "Corpus revision:",
            "Baseline artifact:",
            "Distilled document:",
            "Per-metric sections rendered:",
        ):
            self.assertIn(marker, out, f"Output Contract marker missing: {marker!r}")

    def test_stdout_paths_use_posix_separators(self) -> None:
        # Cross-platform rule: relative paths render with .as_posix() so the
        # summary stays operator-portable across Windows/macOS/Linux.
        _, out, _ = _invoke(
            baseline_json=str(FIXTURE_BASELINE),
            output_dir=str(self.work_dir),
            no_prior=True,
            today_override=FIXTURE_TODAY,
        )
        self.assertNotIn(
            "\\",
            out,
            "summary paths must render via .as_posix() per .claude/rules/cross-platform.md",
        )


if __name__ == "__main__":
    unittest.main()
