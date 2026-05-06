"""CLI tests for ``gz complexity advise`` (OBPI-0.0.29-03).

Pins REQ-0.0.29-03-01 through REQ-0.0.29-03-07 (acceptance criteria).
Subprocess boundaries are absent: radon is invoked via its Python API
(``radon.complexity.cc_visit``) so REQ-0.0.29-03-10 is honored vacuously.

Test-class split per ``.gzkit/rules/tool-skill-runbook-alignment.md`` Invariant 3
and ``.claude/rules/tests.md`` § Output-form fixture carve-out:

* ``TestComplexityAdviseBehavior`` — REQ-derived semantic assertions
  (exit codes, JSON shape, parsing).
* ``TestComplexityAdviseOutputForm`` — Invariant-3 fixture pinning the
  default human prose form (string-shape assertions live only here).
* ``TestComplexityAdviseHelpManpageParity`` — REQ-04/05 help structure.

Tests build a synthetic distilled-characteristics + threshold-rule
environment under a temp project root because the engine fails closed on
the production distilled doc's empty practitioner-eye section (operator
attestation deferred). The synthetic fixture mirrors the pattern in
``tests/complexity/advisor/test_engine.py``.
"""

from __future__ import annotations

import io
import json
import os
import tempfile
import unittest
from collections.abc import Iterator
from contextlib import contextmanager, redirect_stderr, redirect_stdout
from pathlib import Path

from gzkit.commands.complexity_advise import complexity_advise_cmd
from gzkit.traceability import covers

_PRACTITIONER_EYE_SENTINEL = "Refactor signal: extract the responsibility seam and re-test."


def _distilled_characteristics(metric: str = "radon_cc") -> str:
    return "\n".join(
        [
            "---",
            "corpus_revision: 1",
            "---",
            "",
            "# Distilled complexity characteristics — synthetic fixture",
            "",
            f"## Metric: `{metric}`",
            "",
            "Across the corpus, synthetic distribution applies.",
            "",
            "**Doctrinal frame:** Martin (Clean Code) — function decomposition signal.",
            "",
            "### Practitioner-eye observation",
            "",
            _PRACTITIONER_EYE_SENTINEL,
            "",
        ]
    )


def _rule_body(metric: str, distilled_path: Path, anchor: str) -> str:
    return (
        "---\n"
        "id: complexity-thresholds\n"
        "paths:\n"
        '  - ".gzkit/rules/complexity-thresholds.md"\n'
        "description: synthetic\n"
        "---\n\n"
        "<!-- rule-version: 0.1.0 -->\n\n"
        "# Synthetic Complexity Thresholds\n\n"
        "## Citation\n\n"
        f"`{distilled_path.as_posix()} § {anchor} (corpus revision 1)`\n\n"
        "## Per-metric tables\n\n"
        f"### Metric: `{metric}`\n\n"
        f"Citation: `{distilled_path.as_posix()} § {anchor} (corpus revision 1)`\n\n"
        "| Trigger | Corpus percentile | Absolute number | Cited section |\n"
        "|---------|-------------------|-----------------|---------------|\n"
        f"| advise  | p75               | 4.0             | {anchor}      |\n"
        f"| warn    | p90               | 7.0             | {anchor}      |\n"
        f"| block   | p95               | 11.0            | {anchor}      |\n"
    )


@contextmanager
def _synthetic_environment(metric: str = "radon_cc") -> Iterator[Path]:
    """Yield path to a synthetic threshold rule under a temp project root.

    The distilled doc is written under ``docs/governance/complexity/``
    relative to the temp dir so that ``Citation.distilled_characteristics_path``
    parses (the canonical-pattern regex requires that prefix). The CWD is
    set to the temp dir so the engine resolves the relative citation path
    from there.
    """
    with tempfile.TemporaryDirectory() as raw_root:
        root = Path(raw_root)
        complexity_dir = root / "docs" / "governance" / "complexity"
        complexity_dir.mkdir(parents=True)
        distilled_path = complexity_dir / "distilled-characteristics-synthetic.md"
        distilled_path.write_text(_distilled_characteristics(metric), encoding="utf-8")
        rule_path = root / "complexity_thresholds.md"
        anchor = metric.replace("_", "-")
        rule_path.write_text(
            _rule_body(metric, distilled_path.relative_to(root), anchor),
            encoding="utf-8",
        )
        prior_cwd = Path.cwd()
        os.chdir(root)
        try:
            yield rule_path
        finally:
            os.chdir(prior_cwd)


def _invoke(**kwargs: object) -> tuple[int, str, str]:
    """Call ``complexity_advise_cmd`` collapsing SystemExit into an exit code."""
    out = io.StringIO()
    err = io.StringIO()
    code = 0
    try:
        with redirect_stdout(out), redirect_stderr(err):
            code = complexity_advise_cmd(**kwargs) or 0  # type: ignore[arg-type]
    except SystemExit as exc:
        raw = exc.code
        code = raw if isinstance(raw, int) else 1
    return int(code), out.getvalue(), err.getvalue()


CLEAN_SOURCE = """\
def add(a, b):
    return a + b


def double(x):
    return x * 2
"""

# CC ~8 — crosses warn (>=7) but not block (>=11)
WARN_SOURCE = """\
def warn_band(x):
    if x > 0:
        if x > 1:
            return 1
        elif x > 2:
            return 2
        elif x > 3:
            return 3
        elif x > 4:
            return 4
        else:
            return 5
    return 0
"""

# CC = 12 — crosses block (>=11)
BLOCK_SOURCE = """\
def block_band(x):
    if x > 0:
        if x > 1:
            return 1
        elif x > 2:
            return 2
        elif x > 3:
            return 3
        elif x > 4:
            return 4
        elif x > 5:
            return 5
        elif x > 6:
            return 6
        elif x > 7:
            return 7
        elif x > 8:
            return 8
        elif x > 9:
            return 9
        elif x > 10:
            return 10
        else:
            return 11
    return 0
"""


def _write_source(temp_dir: Path, source: str, name: str = "subject.py") -> Path:
    target = temp_dir / name
    target.write_text(source, encoding="utf-8")
    return target


def _resolve_advise_subparser(parser: object) -> object:
    """Walk the argparse tree to the ``complexity advise`` subparser."""
    import argparse  # noqa: PLC0415

    assert isinstance(parser, argparse.ArgumentParser)
    for action in parser._actions:
        if isinstance(action, argparse._SubParsersAction) and "complexity" in action.choices:
            complexity_parser = action.choices["complexity"]
            for sub in complexity_parser._actions:
                if isinstance(sub, argparse._SubParsersAction) and "advise" in sub.choices:
                    return sub.choices["advise"]
    raise AssertionError("complexity/advise subparser not found")


class TestComplexityAdviseBehavior(unittest.TestCase):
    """REQ-derived semantic assertions (no string-shape assertions here)."""

    @covers("REQ-0.0.29-03-01")
    def test_clean_file_exit_zero(self) -> None:
        with (
            _synthetic_environment() as rule_path,
            tempfile.TemporaryDirectory() as src_tmp,
        ):
            target = _write_source(Path(src_tmp), CLEAN_SOURCE)
            code, out, _ = _invoke(path=str(target), rule_path=str(rule_path))
        self.assertEqual(code, 0)
        self.assertIn("no crossings", out.lower())

    @covers("REQ-0.0.29-03-02")
    def test_warn_band_exit_zero_with_diagnosis(self) -> None:
        with (
            _synthetic_environment() as rule_path,
            tempfile.TemporaryDirectory() as src_tmp,
        ):
            target = _write_source(Path(src_tmp), WARN_SOURCE)
            code, out, _ = _invoke(path=str(target), rule_path=str(rule_path))
        self.assertEqual(code, 0)
        lowered = out.lower()
        self.assertIn("archetype", lowered)
        self.assertIn("authority", lowered)

    @covers("REQ-0.0.29-03-03")
    def test_block_band_exit_three(self) -> None:
        with (
            _synthetic_environment() as rule_path,
            tempfile.TemporaryDirectory() as src_tmp,
        ):
            target = _write_source(Path(src_tmp), BLOCK_SOURCE)
            code, _, _ = _invoke(path=str(target), rule_path=str(rule_path))
        self.assertEqual(code, 3)

    @covers("REQ-0.0.29-03-04")
    def test_json_mode_emits_valid_json_array(self) -> None:
        with (
            _synthetic_environment() as rule_path,
            tempfile.TemporaryDirectory() as src_tmp,
        ):
            target = _write_source(Path(src_tmp), WARN_SOURCE)
            code, out, _ = _invoke(
                path=str(target),
                json_output=True,
                rule_path=str(rule_path),
            )
        self.assertEqual(code, 0)
        payload = json.loads(out)
        self.assertIsInstance(payload, list)
        self.assertGreaterEqual(len(payload), 1)
        first = payload[0]
        for required in (
            "metric",
            "crossing_band",
            "crossing_value",
            "archetype",
            "doctrinal_frame",
            "proof",
            "recommended_move",
        ):
            self.assertIn(required, first)
        self.assertEqual(first["metric"], "radon_cc")
        self.assertGreaterEqual(len(first["proof"]), 1)

    @covers("REQ-0.0.29-03-04")
    def test_json_mode_clean_file_emits_empty_array(self) -> None:
        with (
            _synthetic_environment() as rule_path,
            tempfile.TemporaryDirectory() as src_tmp,
        ):
            target = _write_source(Path(src_tmp), CLEAN_SOURCE)
            code, out, _ = _invoke(
                path=str(target),
                json_output=True,
                rule_path=str(rule_path),
            )
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(out), [])

    @covers("REQ-0.0.29-03-02")
    def test_bad_path_exits_one(self) -> None:
        with _synthetic_environment() as rule_path:
            code, _, err = _invoke(
                path="/nonexistent/path/that/should/not/exist.py",
                rule_path=str(rule_path),
            )
        self.assertEqual(code, 1)
        self.assertTrue(err.strip(), msg="bad path should emit stderr error")

    @covers("REQ-0.0.29-03-02")
    def test_missing_rule_path_exits_two(self) -> None:
        with _synthetic_environment(), tempfile.TemporaryDirectory() as src_tmp:
            target = _write_source(Path(src_tmp), CLEAN_SOURCE)
            missing_rule = Path(src_tmp) / "no-such-rule.md"
            code, _, err = _invoke(path=str(target), rule_path=str(missing_rule))
        self.assertEqual(code, 2)
        self.assertTrue(err.strip())

    @covers("REQ-0.0.29-03-01")
    def test_directory_walks_python_files(self) -> None:
        with (
            _synthetic_environment() as rule_path,
            tempfile.TemporaryDirectory() as src_tmp,
        ):
            tmp_path = Path(src_tmp)
            _write_source(tmp_path, CLEAN_SOURCE, "clean.py")
            _write_source(tmp_path, BLOCK_SOURCE, "block.py")
            (tmp_path / "ignored.txt").write_text("not python", encoding="utf-8")
            code, _, _ = _invoke(path=str(tmp_path), rule_path=str(rule_path))
        self.assertEqual(code, 3)  # block.py contributes a block-band crossing

    @covers("REQ-0.0.29-03-05")
    def test_help_invocation_via_parser(self) -> None:
        from gzkit.cli.main import _build_parser  # noqa: PLC0415

        parser = _build_parser()
        with self.assertRaises(SystemExit) as ctx:
            parser.parse_args(["complexity", "advise", "--help"])
        self.assertEqual(ctx.exception.code, 0)

    @covers("REQ-0.0.29-03-05")
    def test_standard_flags_accepted(self) -> None:
        from gzkit.cli.main import _build_parser  # noqa: PLC0415

        parser = _build_parser()
        ns = parser.parse_args(
            [
                "complexity",
                "advise",
                "x.py",
                "--quiet",
                "--verbose",
                "--dry-run",
                "--json",
                "--auto-chain",
            ]
        )
        self.assertTrue(ns.json_output)
        self.assertTrue(ns.quiet)
        self.assertTrue(ns.verbose)
        self.assertTrue(ns.dry_run)
        self.assertTrue(ns.auto_chain)


class TestComplexityAdviseOutputForm(unittest.TestCase):
    """Output-form fixture asserting the verb's default human-readable prose form.

    String-shape assertions live ONLY in this class per
    ``.gzkit/rules/tool-skill-runbook-alignment.md`` § Invariant 3
    and ``.claude/rules/tests.md`` § Output-form fixture carve-out.
    """

    @covers("REQ-0.0.29-03-02")
    def test_default_prose_names_archetype_authority_proof_recommendation(self) -> None:
        with (
            _synthetic_environment() as rule_path,
            tempfile.TemporaryDirectory() as src_tmp,
        ):
            target = _write_source(Path(src_tmp), WARN_SOURCE)
            code, out, _ = _invoke(path=str(target), rule_path=str(rule_path))
        self.assertEqual(code, 0)
        lowered = out.lower()
        self.assertIn("archetype", lowered)
        self.assertIn("authority", lowered)
        self.assertIn("proof", lowered)
        self.assertIn("recommended", lowered)


class TestComplexityAdviseCliAuditParity(unittest.TestCase):
    """REQ-07: ``gz cli audit`` covers the new verb (manpage, doc, index)."""

    @covers("REQ-0.0.29-03-07")
    def test_cli_audit_covers_complexity_advise(self) -> None:
        """Verify cross-coverage scanner finds no gaps for ``complexity advise``."""
        from gzkit.commands.common import get_project_root  # noqa: PLC0415
        from gzkit.doc_coverage.scanner import check_surfaces_report  # noqa: PLC0415

        report = check_surfaces_report(get_project_root())
        complexity_advise = next(
            (c for c in report.coverage if c.command == "complexity advise"),
            None,
        )
        self.assertIsNotNone(
            complexity_advise,
            msg="`complexity advise` not present in cross-coverage scan",
        )
        self.assertTrue(
            complexity_advise.all_passed,  # type: ignore[union-attr]
            msg=(
                f"complexity advise coverage gaps: "
                f"{[s.surface for s in complexity_advise.surfaces if not s.passed]}"  # type: ignore[union-attr]
            ),
        )


class TestComplexityAdviseHelpManpageParity(unittest.TestCase):
    """REQ-04 + REQ-05: help text contains the standard sections."""

    @covers("REQ-0.0.29-03-05")
    @covers("REQ-0.0.29-03-06")
    def test_parser_help_contains_required_sections(self) -> None:
        from gzkit.cli.main import _build_parser  # noqa: PLC0415

        parser = _build_parser()
        advise_parser = _resolve_advise_subparser(parser)
        help_text = advise_parser.format_help()  # type: ignore[attr-defined]
        self.assertIn("usage:", help_text.lower())
        self.assertIn("--json", help_text)
        self.assertIn("--quiet", help_text)
        self.assertTrue(
            "example" in help_text.lower() or "gz complexity advise" in help_text,
            msg="advise --help must include at least one example invocation",
        )


if __name__ == "__main__":
    unittest.main()
